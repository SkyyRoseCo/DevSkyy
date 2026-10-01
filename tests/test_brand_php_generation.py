"""Brand projection works for explicit no-tagline and external local outputs."""

from pathlib import Path

from scripts.sync_brand_to_php import main


def test_local_output_and_check_support_no_active_tagline(tmp_path: Path) -> None:
    output = tmp_path / "brand.generated.php"
    assert main(["--output", str(output), "--check"]) == 1
    assert main(["--output", str(output)]) == 0
    assert "define( 'SKYYROSE_BRAND_TAGLINE', '' );" in output.read_text()
    assert main(["--output", str(output), "--check"]) == 0
    output.write_text(
        output.read_text().replace(
            "SKYYROSE_BRAND_TAGLINE', ''", "SKYYROSE_BRAND_TAGLINE', 'stale'"
        )
    )
    assert main(["--output", str(output), "--check"]) == 1
