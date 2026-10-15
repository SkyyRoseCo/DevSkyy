"""Prevent the recovered POT's missing plural-message regression."""

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from inputs import ROOT

spec = importlib.util.spec_from_file_location(
    "pot", ROOT / "wordpress-theme/skyyrose-flagship-2/scripts/build-pot.py"
)
pot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pot)


class TranslationTests(unittest.TestCase):
    def test_escaped_quotes_and_backslashes_remain_literal_messages(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "page.php").write_text(
                r"""<?php __('Skyy\'s path \\ home', 'skyyrose-flagship-2');
_n("one \"view\"", "many \"views\"", $n, "skyyrose-flagship-2");"""
            )
            with patch.object(pot, "THEME", root):
                self.assertEqual(pot.collect(), {"Skyy's path \\ home": ["page.php:1"]})
                self.assertEqual(
                    pot.collect_plurals(),
                    {'one "view"': ('many "views"', ["page.php:2"])},
                )

    def test_unterminated_escape_runs_do_not_backtrack_exponentially(self):
        script = r"""
import importlib.util
import sys
spec = importlib.util.spec_from_file_location("pot", sys.argv[1])
pot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pot)
for quote in ("'", '"'):
    malformed = quote + "\\a" * 2000
    assert pot.CALL.search("__(" + malformed) is None
    assert pot.PLURAL_CALL.search("_n(" + malformed) is None
    assert pot.PLURAL_CALL.search("_n('one', " + malformed) is None
"""
        subprocess.run(
            [sys.executable, "-c", script, str(pot.THEME / "scripts/build-pot.py")],
            check=True,
            timeout=5,
        )

    def test_runtime_plural_is_retained(self):
        plural, references = pot.collect_plurals()["%d published view"]
        self.assertEqual(plural, "%d published views")
        self.assertEqual(len(references), 1)
        source, line_number = references[0].rsplit(":", 1)
        self.assertEqual(source, "template-parts/commerce/product-hero.php")
        self.assertGreater(int(line_number), 0)
        source_lines = (pot.THEME / source).read_text().splitlines()
        self.assertIn(
            "_n( '%d published view', '%d published views',",
            source_lines[int(line_number) - 1],
        )
        rendered = pot.render(pot.collect())
        self.assertIn('msgid_plural "%d published views"\nmsgstr[0] ""\nmsgstr[1] ""', rendered)

    def test_excludes_fixtures_and_parses_double_quotes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "scripts").mkdir()
            (root / "scripts/test.php").write_text(
                "<?php _n('fake', 'fakes', $n, 'skyyrose-flagship-2');"
            )
            (root / "page.php").write_text('<?php _n("one", "many", $n, "skyyrose-flagship-2");')
            with patch.object(pot, "THEME", root):
                self.assertEqual(pot.collect_plurals(), {"one": ("many", ["page.php:1"])})
