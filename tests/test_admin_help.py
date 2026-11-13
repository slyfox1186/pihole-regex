"""Check the pihole_admin.py help screen and the option table that drives its parser."""

import io
import re
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pihole_admin

SCRIPT = Path(pihole_admin.__file__)
ANSI = re.compile(r"\033\[[0-9;]*m")
OPTIONS = [option for _title, _intro, group in pihole_admin.OPTION_SECTIONS for option in group]


class HelpTextTests(unittest.TestCase):
    def test_every_option_is_listed_once(self):
        lines = pihole_admin.help_text("pihole_admin.py", False, 80).splitlines()
        for option in OPTIONS:
            with self.subTest(option=option.flags[-1]):
                self.assertEqual(sum(line.startswith(f"  {option.label}") for line in lines), 1)

    def test_color_changes_nothing_but_the_escape_codes(self):
        for width in (60, 80, 100):
            with self.subTest(width=width):
                plain = pihole_admin.help_text("pihole_admin.py", False, width)
                colored = pihole_admin.help_text("pihole_admin.py", True, width)
                self.assertNotIn("\033", plain)
                self.assertIn("\033[", colored)
                self.assertEqual(ANSI.sub("", colored), plain)

    def test_lines_fit_the_terminal(self):
        for width in (80, 100):
            with self.subTest(width=width):
                text = pihole_admin.help_text("pihole_admin.py", False, width)
                self.assertLessEqual(max(len(line) for line in text.splitlines()), width)

    def test_wide_terminals_are_capped(self):
        self.assertEqual(pihole_admin.help_text("pihole_admin.py", False, 300),
                         pihole_admin.help_text("pihole_admin.py", False, pihole_admin.HELP_MAX_WIDTH))

    def test_narrow_terminal_puts_descriptions_under_the_option(self):
        lines = pihole_admin.help_text("pihole_admin.py", False, 60).splitlines()
        for option in OPTIONS:
            with self.subTest(option=option.flags[-1]):
                self.assertIn(f"  {option.label}", lines)
        text_lines = [line for line in lines if line.startswith(" " * 10)]
        self.assertLessEqual(max(len(line) for line in text_lines), 60)


class ParserTests(unittest.TestCase):
    def test_every_option_parses_to_its_value(self):
        args = pihole_admin.build_parser().parse_args([
            "-o", "-b", "/tmp/x", "-s", "-c", "30", "-aw", "a.com b.org", "-ab", "c.com",
            "-rw", "d.com", "-rb", "e.com", "-g", "-td", "20", "-q", "clients",
            "--order-by", "blocked", "--limit", "5", "-aq", "SELECT 1", "-r", "-u", "-rd",
            "-fs", "90", "-cd", "-aqt", "60",
        ])
        self.assertEqual(vars(args), {
            "optimize": True, "backup": "/tmp/x", "stats": True, "clean": 30,
            "add_whitelist": "a.com b.org", "add_blacklist": "c.com",
            "remove_whitelist": "d.com", "remove_blacklist": "e.com",
            "update_gravity": True, "top_domains": 20, "query": "clients",
            "order_by": "blocked", "limit": 5, "advanced_query": "SELECT 1", "report": True,
            "check_updates": True, "remove_duplicates": True, "find_similar": 90,
            "categorize_domains": True, "analyze_query_trends": 60,
        })

    def test_defaults(self):
        args = pihole_admin.build_parser().parse_args(["--stats"])
        self.assertEqual((args.limit, args.order_by, args.clean, args.query), (10, None, None, None))

    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", ["pihole_admin.py", *argv]), \
                redirect_stdout(out), redirect_stderr(err), self.assertRaises(SystemExit) as caught:
            pihole_admin.main()
        return caught.exception.code, out.getvalue(), err.getvalue()

    def test_help_exits_zero_on_stdout(self):
        for flag in ("-h", "--help"):
            with self.subTest(flag=flag):
                code, out, err = self.run_main(flag)
                self.assertEqual((code, err), (0, ""))
                self.assertIn("USAGE", out)
                self.assertNotIn("\033", out)

    def test_no_arguments_shows_help_and_exits_one(self):
        code, out, _err = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("USAGE", out)

    def test_bad_option_points_at_help(self):
        for argv in (["--bogus"], ["--query", "people"], ["--clean", "soon"]):
            with self.subTest(argv=argv):
                code, out, err = self.run_main(*argv)
                self.assertEqual((code, out), (2, ""))
                self.assertTrue(err.startswith("Error: "))
                self.assertIn("Run pihole_admin.py --help to see the options.", err)
                self.assertNotIn("usage:", err)


class MissingPackageTests(unittest.TestCase):
    def run_without_packages(self, *argv):
        # A None entry in sys.modules makes the import fail, as on a system without the package.
        code = (
            "import runpy, sys\n"
            "for name in ('requests', 'tabulate', 'matplotlib', 'pandas', 'seaborn', 'rapidfuzz', 'tld'):\n"
            "    sys.modules[name] = None\n"
            f"sys.argv = {[str(SCRIPT), *argv]!r}\n"
            f"runpy.run_path({str(SCRIPT)!r}, run_name='__main__')\n"
        )
        return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=False)

    def test_help_needs_no_third_party_package(self):
        result = self.run_without_packages("--help")
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        self.assertIn("EXTRA PACKAGES", result.stdout)

    def test_table_without_tabulate_gives_an_install_hint(self):
        with self.assertRaises(SystemExit) as caught, patch.dict(sys.modules, {"tabulate": None}):
            pihole_admin._grid([{"domain": "example.com", "count": 1}])
        self.assertIn("pip install tabulate", str(caught.exception.code))


if __name__ == "__main__":
    unittest.main()
