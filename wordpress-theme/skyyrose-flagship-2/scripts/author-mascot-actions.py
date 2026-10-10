#!/usr/bin/env python3
"""Bake production full-body actions into the Skyy mascot GLB with Blender.

Run with Blender, not system Python:
    blender --background --factory-startup --python scripts/author-mascot-actions.py -- \
      assets/models/skyy-mascot.glb /tmp/skyy-mascot-animated.glb

The source GLB is never modified in place. Every invocation imports the canonical
source into a clean scene, replaces the incomplete bind-pose actions, and exports
a new Draco-compressed GLB with deterministic action names consumed by skyy-3d.js.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy

FPS = 30
REQUIRED_BONES = {
    "pelvis",
    "spine",
    "chest",
    "neck",
    "head",
    "upper_arm.L",
    "forearm.L",
    "upper_arm.R",
    "forearm.R",
    "thigh.L",
    "shin.L",
    "thigh.R",
    "shin.R",
}


# The supplied source mesh is authored Z-up in Blender while its inherited
# armature sits in a different bind space and leaves the entire upper body on
# `neutral_bone`. Rebuild the rest rig against the visible body before baking
# clips. Coordinates are normalized to the source character's 0.98 m height.
RIG_POINTS = {
    "pelvis": ((0.0, 0.0, 0.30), (0.0, 0.0, 0.38)),
    "spine": ((0.0, 0.0, 0.38), (0.0, 0.0, 0.52)),
    "chest": ((0.0, 0.0, 0.52), (0.0, 0.0, 0.66)),
    "neck": ((0.0, 0.0, 0.66), (0.0, 0.0, 0.75)),
    "head": ((0.0, 0.0, 0.75), (0.0, 0.0, 0.90)),
    "upper_arm.L": ((0.15, 0.0, 0.64), (0.30, 0.0, 0.64)),
    "forearm.L": ((0.30, 0.0, 0.64), (0.39, 0.0, 0.64)),
    "hand.L": ((0.39, 0.0, 0.64), (0.46, 0.0, 0.64)),
    "upper_arm.R": ((-0.15, 0.0, 0.64), (-0.30, 0.0, 0.64)),
    "forearm.R": ((-0.30, 0.0, 0.64), (-0.39, 0.0, 0.64)),
    "hand.R": ((-0.39, 0.0, 0.64), (-0.46, 0.0, 0.64)),
    "thigh.L": ((0.09, 0.0, 0.32), (0.12, 0.0, 0.17)),
    "shin.L": ((0.12, 0.0, 0.17), (0.13, 0.0, 0.05)),
    "foot.L": ((0.13, 0.0, 0.05), (0.13, -0.12, 0.02)),
    "thigh.R": ((-0.09, 0.0, 0.32), (-0.12, 0.0, 0.17)),
    "shin.R": ((-0.12, 0.0, 0.17), (-0.13, 0.0, 0.05)),
    "foot.R": ((-0.13, 0.0, 0.05), (-0.13, -0.12, 0.02)),
    "neutral_bone": ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
}

PARENTS = {
    "spine": "pelvis",
    "chest": "spine",
    "neck": "chest",
    "head": "neck",
    "upper_arm.L": "chest",
    "forearm.L": "upper_arm.L",
    "hand.L": "forearm.L",
    "upper_arm.R": "chest",
    "forearm.R": "upper_arm.R",
    "hand.R": "forearm.R",
    "thigh.L": "pelvis",
    "shin.L": "thigh.L",
    "foot.L": "shin.L",
    "thigh.R": "pelvis",
    "shin.R": "thigh.R",
    "foot.R": "shin.R",
}


def rebuild_rest_rig(armature: bpy.types.Object) -> None:
    """Align inherited bones to the visible mesh's actual Z-up bind pose."""

    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for name, (head, tail) in RIG_POINTS.items():
        bone = armature.data.edit_bones.get(name)
        if bone is None:
            bone = armature.data.edit_bones.new(name)
        bone.head = head
        bone.tail = tail
        bone.roll = 0.0
        bone.use_connect = False
    for child_name, parent_name in PARENTS.items():
        armature.data.edit_bones[child_name].parent = armature.data.edit_bones[parent_name]
    bpy.ops.object.mode_set(mode="OBJECT")


def nearest_pair(value: float, centers: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """Return two neighboring controls with stable linear blend weights."""

    ordered = sorted(centers, key=lambda item: item[1])
    if value <= ordered[0][1]:
        return [(ordered[0][0], 1.0)]
    if value >= ordered[-1][1]:
        return [(ordered[-1][0], 1.0)]
    for left, right in zip(ordered[:-1], ordered[1:], strict=True):
        if left[1] <= value <= right[1]:
            span = right[1] - left[1]
            right_weight = (value - left[1]) / span
            return [(left[0], 1.0 - right_weight), (right[0], right_weight)]
    raise RuntimeError("Could not resolve skin blend")


def rebuild_skin_weights(mesh: bpy.types.Object) -> None:
    """Bind every character vertex to the full-body rig in large batches.

    The source weights cover legs but leave head, torso, and arms unbound. A
    deterministic region blend is safer than Blender bone heat on this dense
    one-million-vertex scan and makes the authoring step reproducible.
    """

    groups = {
        name: mesh.vertex_groups.get(name) or mesh.vertex_groups.new(name=name)
        for name in RIG_POINTS
    }
    for group in groups.values():
        group.remove(range(len(mesh.data.vertices)))

    assignments: dict[tuple[str, float], list[int]] = {}
    for vertex in mesh.data.vertices:
        x, _depth, z = vertex.co
        absolute_x = abs(x)
        if z >= 0.70:
            weights = [("head", 1.0)]
        elif absolute_x >= 0.135 and z >= 0.42:
            side = "L" if x >= 0.0 else "R"
            weights = nearest_pair(
                absolute_x,
                [(f"upper_arm.{side}", 0.22), (f"forearm.{side}", 0.345), (f"hand.{side}", 0.43)],
            )
        elif z >= 0.30:
            weights = nearest_pair(
                z,
                [("pelvis", 0.33), ("spine", 0.45), ("chest", 0.59), ("neck", 0.68)],
            )
        else:
            side = "L" if x >= 0.0 else "R"
            weights = nearest_pair(
                z,
                [(f"foot.{side}", 0.025), (f"shin.{side}", 0.11), (f"thigh.{side}", 0.245)],
            )
        for name, weight in weights:
            quantized = round(max(0.0, min(1.0, weight)), 3)
            if quantized:
                assignments.setdefault((name, quantized), []).append(vertex.index)

    for (name, weight), indices in assignments.items():
        groups[name].add(indices, weight, "REPLACE")

    print(f"SKINNED {len(mesh.data.vertices)} vertices across {len(assignments)} weighted batches")


def radians(values: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(math.radians(value) for value in values)


def reset_pose(armature: bpy.types.Object) -> None:
    for bone in armature.pose.bones:
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = (0.0, 0.0, 0.0)
        bone.location = (0.0, 0.0, 0.0)
        bone.scale = (1.0, 1.0, 1.0)


def keyed_pose(
    armature: bpy.types.Object,
    frame: int,
    rotations: dict[str, tuple[float, float, float]],
    locations: dict[str, tuple[float, float, float]] | None = None,
) -> None:
    reset_pose(armature)
    for name, degrees in rotations.items():
        armature.pose.bones[name].rotation_euler = radians(degrees)
    for name, location in (locations or {}).items():
        armature.pose.bones[name].location = location

    bpy.context.scene.frame_set(frame)
    for bone in armature.pose.bones:
        bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=bone.name)
        bone.keyframe_insert(data_path="location", frame=frame, group=bone.name)


def base_pose() -> dict[str, tuple[float, float, float]]:
    """Relax the source T-pose into Skyy's neutral full-body host stance."""

    return {
        "upper_arm.L": (0.0, 0.0, -88.0),
        "forearm.L": (0.0, 0.0, -78.0),
        "upper_arm.R": (0.0, 0.0, 88.0),
        "forearm.R": (0.0, 0.0, 78.0),
        "thigh.L": (0.0, 0.0, -2.0),
        "thigh.R": (0.0, 0.0, 2.0),
    }


def merged(**changes: tuple[float, float, float]) -> dict[str, tuple[float, float, float]]:
    pose = base_pose()
    pose.update(changes)
    return pose


def create_action(
    armature: bpy.types.Object,
    name: str,
    frames: list[
        tuple[int, dict[str, tuple[float, float, float]], dict[str, tuple[float, float, float]]]
    ],
) -> None:
    action = bpy.data.actions.new(name=name)
    armature.animation_data.action = action
    for frame, rotations, locations in frames:
        keyed_pose(armature, frame, rotations, locations)
    armature.animation_data.action = None


def build_actions(armature: bpy.types.Object) -> None:
    if armature.animation_data is None:
        armature.animation_data_create()
    armature.animation_data.action = None

    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)

    idle = [
        (1, merged(chest=(0.0, 0.0, 0.0), head=(0.0, 0.0, -2.0)), {"pelvis": (0.0, 0.0, 0.0)}),
        (
            24,
            merged(
                **{
                    "upper_arm.L": (2.0, 0.0, -86.0),
                    "upper_arm.R": (-2.0, 0.0, 89.0),
                    "forearm.L": (0.0, 0.0, -74.0),
                    "chest": (1.5, 0.0, 1.0),
                    "head": (-1.0, 3.0, 1.0),
                }
            ),
            {"pelvis": (0.004, 0.004, 0.0)},
        ),
        (
            48,
            merged(
                **{
                    "upper_arm.L": (-2.0, 0.0, -89.0),
                    "upper_arm.R": (2.0, 0.0, 86.0),
                    "forearm.R": (0.0, 0.0, 74.0),
                    "chest": (-1.0, 0.0, -1.0),
                    "head": (1.0, -3.0, -1.0),
                }
            ),
            {"pelvis": (-0.004, 0.0, 0.0)},
        ),
        (72, merged(chest=(0.0, 0.0, 0.0), head=(0.0, 0.0, -2.0)), {"pelvis": (0.0, 0.0, 0.0)}),
    ]

    walk = [
        (
            1,
            merged(
                **{
                    "upper_arm.L": (-20.0, 0.0, -84.0),
                    "upper_arm.R": (20.0, 0.0, 84.0),
                    "thigh.L": (25.0, 0.0, -2.0),
                    "thigh.R": (-25.0, 0.0, 2.0),
                    "shin.R": (22.0, 0.0, 0.0),
                }
            ),
            {"pelvis": (0.0, 0.0, 0.0)},
        ),
        (
            10,
            merged(
                **{
                    "thigh.L": (0.0, 0.0, -2.0),
                    "thigh.R": (0.0, 0.0, 2.0),
                    "shin.L": (12.0, 0.0, 0.0),
                    "shin.R": (12.0, 0.0, 0.0),
                }
            ),
            {"pelvis": (0.0, 0.018, 0.0)},
        ),
        (
            19,
            merged(
                **{
                    "upper_arm.L": (20.0, 0.0, -84.0),
                    "upper_arm.R": (-20.0, 0.0, 84.0),
                    "thigh.L": (-25.0, 0.0, -2.0),
                    "thigh.R": (25.0, 0.0, 2.0),
                    "shin.L": (22.0, 0.0, 0.0),
                }
            ),
            {"pelvis": (0.0, 0.0, 0.0)},
        ),
        (
            28,
            merged(
                **{
                    "thigh.L": (0.0, 0.0, -2.0),
                    "thigh.R": (0.0, 0.0, 2.0),
                    "shin.L": (12.0, 0.0, 0.0),
                    "shin.R": (12.0, 0.0, 0.0),
                }
            ),
            {"pelvis": (0.0, 0.018, 0.0)},
        ),
        (
            37,
            merged(
                **{
                    "upper_arm.L": (-20.0, 0.0, -84.0),
                    "upper_arm.R": (20.0, 0.0, 84.0),
                    "thigh.L": (25.0, 0.0, -2.0),
                    "thigh.R": (-25.0, 0.0, 2.0),
                    "shin.R": (22.0, 0.0, 0.0),
                }
            ),
            {"pelvis": (0.0, 0.0, 0.0)},
        ),
    ]

    wave = [
        (1, merged(head=(0.0, 0.0, -3.0)), {}),
        (
            12,
            merged(
                **{
                    "upper_arm.R": (0.0, 0.0, -18.0),
                    "forearm.R": (0.0, 0.0, 72.0),
                    "head": (0.0, -5.0, 2.0),
                }
            ),
            {},
        ),
        (
            24,
            merged(
                **{
                    "upper_arm.R": (-8.0, 0.0, -18.0),
                    "forearm.R": (18.0, 0.0, 68.0),
                    "head": (0.0, -5.0, 2.0),
                }
            ),
            {},
        ),
        (
            36,
            merged(
                **{
                    "upper_arm.R": (8.0, 0.0, -18.0),
                    "forearm.R": (-12.0, 0.0, 74.0),
                    "head": (0.0, -5.0, 2.0),
                }
            ),
            {},
        ),
        (
            48,
            merged(
                **{
                    "upper_arm.R": (-8.0, 0.0, -18.0),
                    "forearm.R": (18.0, 0.0, 68.0),
                    "head": (0.0, -5.0, 2.0),
                }
            ),
            {},
        ),
        (60, merged(head=(0.0, 0.0, -3.0)), {}),
    ]

    talk = [
        (1, merged(head=(-2.0, 0.0, -2.0)), {}),
        (
            12,
            merged(
                **{
                    "forearm.L": (-12.0, 0.0, -58.0),
                    "forearm.R": (10.0, 0.0, 54.0),
                    "head": (3.0, -4.0, 1.0),
                }
            ),
            {},
        ),
        (
            24,
            merged(
                **{
                    "forearm.L": (8.0, 0.0, -68.0),
                    "forearm.R": (-12.0, 0.0, 62.0),
                    "head": (-3.0, 4.0, -1.0),
                }
            ),
            {},
        ),
        (
            36,
            merged(
                **{
                    "forearm.L": (-8.0, 0.0, -60.0),
                    "forearm.R": (8.0, 0.0, 58.0),
                    "head": (2.0, -2.0, 1.0),
                }
            ),
            {},
        ),
        (48, merged(head=(-2.0, 0.0, -2.0)), {}),
    ]

    joy = [
        (1, merged(), {"pelvis": (0.0, 0.0, 0.0)}),
        (
            10,
            merged(
                **{
                    "upper_arm.L": (-12.0, 0.0, -18.0),
                    "upper_arm.R": (12.0, 0.0, 18.0),
                    "forearm.L": (0.0, 0.0, -35.0),
                    "forearm.R": (0.0, 0.0, 35.0),
                    "shin.L": (14.0, 0.0, 0.0),
                    "shin.R": (14.0, 0.0, 0.0),
                }
            ),
            {"pelvis": (0.0, 0.035, 0.0)},
        ),
        (
            20,
            merged(
                **{
                    "upper_arm.L": (8.0, 0.0, -30.0),
                    "upper_arm.R": (-8.0, 0.0, 30.0),
                    "head": (-5.0, 0.0, 0.0),
                }
            ),
            {"pelvis": (0.0, 0.0, 0.0)},
        ),
        (36, merged(), {"pelvis": (0.0, 0.0, 0.0)}),
    ]

    create_action(armature, "Skyy_Idle", idle)
    create_action(armature, "Skyy_Walk", walk)
    create_action(armature, "Skyy_Wave", wave)
    create_action(armature, "Skyy_Talk", talk)
    create_action(armature, "Skyy_Joy", joy)
    create_action(armature, "Skyy_Exit", walk)


def main() -> None:
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    if len(argv) != 2:
        raise SystemExit("Expected: <source.glb> <output.glb>")

    source = Path(argv[0]).resolve()
    output = Path(argv[1]).resolve()
    if not source.is_file():
        raise SystemExit(f"Source GLB does not exist: {source}")
    if source == output:
        raise SystemExit("Source and output must differ; in-place authoring is forbidden")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))

    armatures = [obj for obj in bpy.data.objects if obj.type == "ARMATURE"]
    if len(armatures) != 1:
        raise RuntimeError(f"Expected exactly one armature, found {len(armatures)}")
    armature = armatures[0]
    missing = REQUIRED_BONES.difference(armature.pose.bones.keys())
    if missing:
        raise RuntimeError(f"Missing required bones: {sorted(missing)}")

    skinned_meshes = [
        obj
        for obj in bpy.data.objects
        if obj.type == "MESH" and any(modifier.type == "ARMATURE" for modifier in obj.modifiers)
    ]
    if len(skinned_meshes) != 1:
        raise RuntimeError(f"Expected exactly one skinned mesh, found {len(skinned_meshes)}")

    bpy.context.scene.render.fps = FPS
    rebuild_rest_rig(armature)
    rebuild_skin_weights(skinned_meshes[0])
    build_actions(armature)
    reset_pose(armature)
    bpy.context.scene.frame_set(1)

    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(output),
        export_format="GLB",
        export_animations=True,
        export_animation_mode="ACTIONS",
        export_bake_animation=True,
        export_optimize_animation_size=True,
        export_optimize_animation_keep_anim_armature=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=10,
        export_draco_texcoord_quantization=12,
    )
    print(f"AUTHORED {output}")
    print("ACTIONS Skyy_Idle Skyy_Walk Skyy_Wave Skyy_Talk Skyy_Joy Skyy_Exit")


if __name__ == "__main__":
    main()
