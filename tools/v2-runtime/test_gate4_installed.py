"""Offline archive/refusal controls; synthetic temporary files only."""

import tempfile
from pathlib import Path
import warnings
import zipfile

import audit_gate4_installed as audit


def main():
    controls = []
    with tempfile.TemporaryDirectory(prefix="gate4-offline-controls-") as temporary:
        root = Path(temporary)
        valid = root / "valid.zip"
        with zipfile.ZipFile(valid, "w") as archive:
            archive.writestr("fixture/", b"")
            archive.writestr("fixture/main.php", b"synthetic inert code")
        files = audit.archive_files(valid, "fixture")
        baseline = {
            "plugins/fixture/main.php": {
                "sha256": audit.sha(files["main.php"]),
                "bytes": len(files["main.php"]),
            }
        }
        if not audit.compare("fixture", files, baseline)["exact_recorded_census_match"]:
            raise RuntimeError("Positive comparison failed")
        controls.append({"name": "exact-recorded-census", "result": "PASS"})
        for name, members in [
            ("duplicate", ["fixture/main.php", "fixture/main.php"]),
            ("traversal", ["fixture/../main.php"]),
            ("normalized-alias", ["fixture//main.php"]),
            ("absolute", ["/fixture/main.php"]),
            ("member-bound", [f"fixture/{n}.php" for n in range(513)]),
        ]:
            path = root / (name + ".zip")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with zipfile.ZipFile(path, "w") as archive:
                    for member in members:
                        archive.writestr(member, b"x")
            try:
                audit.archive_files(path, "fixture")
            except ValueError:
                controls.append({"name": name, "result": "PASS_REFUSED"})
            else:
                raise RuntimeError("Unsafe archive accepted: " + name)
        path = root / "symlink.zip"
        with zipfile.ZipFile(path, "w") as archive:
            info = zipfile.ZipInfo("fixture/link.php")
            info.create_system = 3
            info.external_attr = 0o120777 << 16
            archive.writestr(info, b"elsewhere")
        try:
            audit.archive_files(path, "fixture")
        except ValueError:
            controls.append({"name": "symlink-member", "result": "PASS_REFUSED"})
        else:
            raise RuntimeError("Symlink member accepted")
        target = root / "target"
        target.mkdir()
        (root / "link").symlink_to(target, target_is_directory=True)
        try:
            audit.retain(root / "link/file.php", b"x")
        except ValueError:
            if (target / "file.php").exists():
                raise RuntimeError("Ancestor refusal still wrote data")
            controls.append({"name": "symlink-ancestor", "result": "PASS_REFUSED_NO_WRITE"})
        else:
            raise RuntimeError("Symlink ancestor accepted")
        for name, candidate in [
            ("missing-file", {}),
            ("unrecorded-extra", {**files, "extra.php": b"x"}),
            ("changed-bytes", {"main.php": b"different"}),
        ]:
            if audit.compare("fixture", candidate, baseline)["exact_recorded_census_match"]:
                raise RuntimeError("Non-exact census accepted: " + name)
            controls.append({"name": name, "result": "PASS_NONMATCH"})
    audit.write(
        audit.OUT / "offline-controls.json",
        {
            "schema": "skyyrose.offline-installed-audit-controls.v1",
            "status": "PASS_SYNTHETIC_OFFLINE_CONTROLS",
            "authentication": "NOT_APPLICABLE",
            "source_pins": {
                str(path.relative_to(audit.ROOT)): audit.pin(path)
                for path in [Path(audit.__file__), Path(__file__).resolve()]
            },
            "controls": controls,
            "scope": "Synthetic archive/path/comparison controls only; no plugin/bootstrap/runtime parity claim",
        },
    )
    print(f"PASS {len(controls)} offline controls")


if __name__ == "__main__":
    main()
