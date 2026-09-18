"""Turntable stills — runs INSIDE Blender (``bpy`` only, no project imports).

Invoked by the worker as::

    blender -b --factory-startup --python-exit-code 1 --python render_stills.py -- '<json>'

The JSON argument carries ``source`` (GLB path), ``out_dir``, ``count``, ``resolution``,
``samples``, ``camera`` (``perspective`` | ``orthographic``) and ``margin``.

Pipeline: empty scene → import glTF → world-space bounding box → pivot empty at the box
centre → camera framed to the bounding sphere with margin → 3-light studio rig + neutral
world → Cycles CPU, transparent film → rotate the PIVOT (not the camera) through N evenly
spaced angles, writing ``still_NN.png`` → ``report.json``. Any failure exits non-zero so the
worker fails closed; a missing/unwritten still is an error, never a silent gap.
"""

from __future__ import annotations

import json
import math
import os
import sys
import traceback

import bpy
from mathutils import Vector

STILL_PATTERN = "still_{index:02d}.png"
REPORT_NAME = "report.json"
CAMERA_ELEVATION_RAD = math.radians(10.0)
# Area-light watts per m² of key-light distance; tuned on the box fixture so a mid-tone
# albedo lands mid-histogram under the Standard view transform rather than clipping white.
LIGHT_WATTS_PER_M2 = 9.0
WORLD_STRENGTH = 0.12
FRAME_LIMITS = {"count": (1, 36), "resolution": (256, 2048), "samples": (1, 1024)}


class RenderError(RuntimeError):
    """Any condition that must abort the render with a non-zero exit."""


def parse_args(argv: list[str]) -> dict:
    """Read the single JSON payload after ``--`` and bounds-check every numeric field."""
    if "--" not in argv or len(argv) <= argv.index("--") + 1:
        raise RenderError("missing JSON payload after '--'")
    payload = json.loads(argv[argv.index("--") + 1])
    for key in ("source", "out_dir", "count", "resolution", "samples", "camera", "margin"):
        if key not in payload:
            raise RenderError(f"payload missing {key!r}")
    for key, (low, high) in FRAME_LIMITS.items():
        value = payload[key]
        if not isinstance(value, int) or not low <= value <= high:
            raise RenderError(f"{key}={value!r} outside [{low}, {high}]")
    if payload["camera"] not in {"perspective", "orthographic"}:
        raise RenderError(f"unknown camera mode {payload['camera']!r}")
    if not isinstance(payload["margin"], (int, float)) or not 0.0 <= payload["margin"] <= 1.0:
        raise RenderError(f"margin={payload['margin']!r} outside [0, 1]")
    if not os.path.isfile(payload["source"]):
        raise RenderError(f"source GLB not found: {payload['source']}")
    return payload


def import_glb(path: str) -> list[bpy.types.Object]:
    """Reset to an empty scene, import the GLB and return its mesh objects (≥1 required)."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    result = bpy.ops.import_scene.gltf(filepath=path)
    if "FINISHED" not in result:
        raise RenderError(f"glTF import returned {sorted(result)}")
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not meshes:
        raise RenderError("glTF import produced no mesh objects")
    return meshes


def world_bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    """Axis-aligned world-space bounds over every object's transformed bound_box."""
    bpy.context.view_layer.update()
    low = Vector((math.inf,) * 3)
    high = Vector((-math.inf,) * 3)
    for obj in objects:
        for corner in obj.bound_box:
            point = obj.matrix_world @ Vector(corner)
            low = Vector(map(min, low, point))
            high = Vector(map(max, high, point))
    if any(math.isinf(component) for component in (*low, *high)):
        raise RenderError("could not compute finite bounds")
    if (high - low).length <= 1e-6:
        raise RenderError("degenerate geometry: zero-size bounds")
    return low, high


def build_pivot(objects: list[bpy.types.Object], center: Vector) -> bpy.types.Object:
    """Parent the imported roots to an empty at ``center`` so rotation spins the garment."""
    pivot = bpy.data.objects.new("turntable_pivot", None)
    bpy.context.scene.collection.objects.link(pivot)
    pivot.location = center
    bpy.context.view_layer.update()
    inverse = pivot.matrix_world.inverted()
    roots = {obj for obj in bpy.context.scene.objects if obj.parent is None and obj is not pivot}
    for obj in roots:
        obj.parent = pivot
        obj.matrix_parent_inverse = inverse
    return pivot


def add_camera(center: Vector, radius: float, mode: str, margin: float) -> bpy.types.Object:
    """Frame the bounding sphere (radius grown by ``margin``) from a low front elevation."""
    data = bpy.data.cameras.new("turntable_camera")
    camera = bpy.data.objects.new("turntable_camera", data)
    bpy.context.scene.collection.objects.link(camera)
    framed = radius * (1.0 + margin)
    if mode == "orthographic":
        data.type = "ORTHO"
        data.ortho_scale = 2.0 * framed
        distance = radius * 4.0
    else:
        data.type = "PERSP"
        data.lens = 50.0
        data.sensor_fit = "AUTO"
        half_fov = math.atan((data.sensor_width / 2.0) / data.lens)
        distance = framed / math.sin(half_fov)
    data.clip_start = max(distance - radius * 4.0, 0.01)
    data.clip_end = distance + radius * 4.0
    camera.location = center + Vector(
        (0.0, -distance * math.cos(CAMERA_ELEVATION_RAD), distance * math.sin(CAMERA_ELEVATION_RAD))
    )
    camera.rotation_euler = (math.pi / 2.0 - CAMERA_ELEVATION_RAD, 0.0, 0.0)
    bpy.context.scene.camera = camera
    return camera


def _area_light(name: str, position: Vector, target: Vector, energy: float, size: float) -> None:
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.size = size
    light = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(light)
    light.location = position
    light.rotation_euler = (target - position).to_track_quat("-Z", "Y").to_euler()


def add_studio_rig(center: Vector, radius: float) -> None:
    """Key / fill / rim area lights scaled to the garment size, plus a neutral grey world."""
    distance = radius * 3.0
    power = LIGHT_WATTS_PER_M2 * distance * distance
    size = max(radius, 0.25)
    offsets = {
        "key": (Vector((-0.7, -0.6, 0.6)), power),
        "fill": (Vector((0.8, -0.5, 0.2)), power * 0.45),
        "rim": (Vector((0.2, 0.9, 0.7)), power * 0.7),
    }
    for name, (direction, energy) in offsets.items():
        _area_light(
            f"light_{name}", center + direction.normalized() * distance, center, energy, size
        )
    world = bpy.data.worlds.new("studio_world")
    if world.node_tree is None:
        world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    if background is None:
        raise RenderError("world node tree has no Background node")
    background.inputs["Color"].default_value = (0.45, 0.45, 0.45, 1.0)
    background.inputs["Strength"].default_value = WORLD_STRENGTH
    bpy.context.scene.world = world


def configure_render(resolution: int, samples: int) -> None:
    """Cycles on CPU, transparent film, square RGBA PNG output; assert the engine took."""
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    if scene.render.engine != "CYCLES":
        raise RenderError("Cycles render engine is unavailable in this Blender build")
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = False
    scene.render.use_persistent_data = True
    scene.render.film_transparent = True
    scene.render.resolution_x = resolution
    scene.render.resolution_y = resolution
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.view_settings.view_transform = "Standard"


def render_turntable(pivot: bpy.types.Object, count: int, out_dir: str) -> list[str]:
    """Rotate the pivot through ``count`` evenly spaced angles, writing one PNG per angle."""
    os.makedirs(out_dir, exist_ok=True)
    scene = bpy.context.scene
    written: list[str] = []
    for index in range(count):
        pivot.rotation_euler = (0.0, 0.0, 2.0 * math.pi * index / count)
        target = os.path.join(out_dir, STILL_PATTERN.format(index=index))
        scene.render.filepath = target
        result = bpy.ops.render.render(write_still=True)
        if "FINISHED" not in result or not os.path.isfile(target) or os.path.getsize(target) == 0:
            raise RenderError(f"still {index} was not written to {target}")
        written.append(target)
    return written


def run(payload: dict) -> dict:
    """Full turntable pipeline; returns the report dict that is also written to disk."""
    meshes = import_glb(payload["source"])
    low, high = world_bounds(meshes)
    center = (low + high) / 2.0
    radius = (high - low).length / 2.0
    pivot = build_pivot(meshes, center)
    add_camera(center, radius, payload["camera"], float(payload["margin"]))
    add_studio_rig(center, radius)
    configure_render(payload["resolution"], payload["samples"])
    stills = render_turntable(pivot, payload["count"], payload["out_dir"])
    report = {
        "blender": bpy.app.version_string,
        "mesh_objects": len(meshes),
        "bounds_min": list(low),
        "bounds_max": list(high),
        "radius": radius,
        "camera": payload["camera"],
        "resolution": payload["resolution"],
        "samples": payload["samples"],
        "stills": [os.path.basename(path) for path in stills],
    }
    with open(os.path.join(payload["out_dir"], REPORT_NAME), "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    return report


def main(argv: list[str]) -> int:
    try:
        report = run(parse_args(argv))
    except Exception:  # noqa: BLE001 — every failure must surface as a non-zero exit
        traceback.print_exc()
        return 1
    print(f"RENDER_REPORT {json.dumps(report)}")
    return 0


if __name__ == "__main__":
    code = main(sys.argv)
    if code != 0:
        sys.exit(code)
