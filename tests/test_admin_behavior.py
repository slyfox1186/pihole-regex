"""Check pihole_admin.py's database, update and chart code against disposable databases and fakes."""

import importlib.util
import os
import sqlite3
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import pihole_admin

LOGGER = "PiholeDBAdmin"
HAVE_MATPLOTLIB = importlib.util.find_spec("matplotlib") is not None
TOP = [{"domain": "ads.example.com", "count": 3}]


def fake_requests(payload, status=200):
    """A stand-in requests module whose get() returns one canned response."""
    module = types.ModuleType("requests")

    class RequestException(Exception):
        pass

    class Response:
        status_code = status

        @staticmethod
        def json():
            return payload

    module.RequestException = RequestException
    module.get = lambda *_args, **_kwargs: Response()
    return module


def version_output(stdout):
    return subprocess.CompletedProcess(["pihole", "-v"], 0, stdout=stdout, stderr="")


class AdminTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.gravity = root / "gravity.db"
        self.queries = root / "pihole-FTL.db"
        with sqlite3.connect(self.gravity) as conn:
            conn.executescript(
                "CREATE TABLE info (property TEXT PRIMARY KEY, value TEXT);"
                "CREATE TABLE domainlist (id INTEGER PRIMARY KEY, type INTEGER, domain TEXT,"
                " enabled INTEGER, date_added INTEGER, UNIQUE(domain, type));"
            )
        conn.close()
        with sqlite3.connect(self.queries) as conn:
            conn.executescript(
                "CREATE TABLE query_storage (id INTEGER PRIMARY KEY, timestamp INTEGER, domain TEXT);"
                "CREATE VIEW queries AS SELECT id, timestamp, domain, 2 AS status FROM query_storage;"
            )
        conn.close()
        self.admin = pihole_admin.PiholeDBAdmin(str(self.gravity), str(self.queries))
        self.addCleanup(self.admin.close_pools)

    def run_sql(self, path, sql, params=()):
        with sqlite3.connect(path) as conn:
            rows = conn.execute(sql, params).fetchall()
        conn.close()
        return rows


class CheckForUpdatesTests(AdminTestCase):
    def check(self, stdout, payload, answer="n"):
        with patch.dict(sys.modules, {"requests": fake_requests(payload)}), \
                patch.object(pihole_admin.subprocess, "run", return_value=version_output(stdout)), \
                patch("builtins.input", return_value=answer), \
                self.assertLogs(LOGGER, "INFO") as logs:
            self.admin.check_for_updates()
        return "\n".join(logs.output)

    def test_reads_the_pihole_v6_core_version(self):
        out = self.check("Core version is v6.6 (Latest: v6.6)\nWeb version is v6.6.1 (Latest: v6.6.1)\n"
                         "FTL version is v6.9 (Latest: v6.9)\n", {"tag_name": "v6.6"})
        self.assertIn("Current Pi-hole version: v6.6", out)
        self.assertIn("Pi-hole is up to date.", out)

    def test_still_reads_the_pihole_v5_version(self):
        # The line formats of Pi-hole v5.18.3's advanced/Scripts/version.sh.
        for stdout in (("  Pi-hole version is v5.18.2 (Latest: v5.18.3)\n"
                        "  web version is v5.21 (Latest: v5.21)\n"),
                       "  Pi-hole version is development v5.18.2 (Latest: v5.18.3)\n",
                       "  Current Pi-hole version is v5.18.2\n"):
            with self.subTest(stdout=stdout):
                out = self.check(stdout, {"tag_name": "v5.18.3"})
                self.assertIn("Current Pi-hole version: v5.18.2", out)
                self.assertIn("Update skipped by user.", out)

    def test_unknown_version_is_reported(self):
        out = self.check("Core version is N/A (Latest: v6.6)\n", {"tag_name": "v6.6"})
        self.assertIn("Could not parse current Pi-hole version.", out)

    def test_closed_input_skips_the_update(self):
        with patch.dict(sys.modules, {"requests": fake_requests({"tag_name": "v6.7"})}), \
                patch.object(pihole_admin.subprocess, "run",
                             return_value=version_output("Core version is v6.6\n")), \
                patch("builtins.input", side_effect=EOFError), \
                patch.object(self.admin, "update_pihole") as update, \
                self.assertLogs(LOGGER, "INFO") as logs:
            self.admin.check_for_updates()
        update.assert_not_called()
        self.assertIn("Update skipped by user.", "\n".join(logs.output))

    def test_release_reply_without_a_tag_is_reported(self):
        for payload in ([], {"tag_name": None}, {}):
            with self.subTest(payload=payload):
                out = self.check("Core version is v6.6\n", payload)
                self.assertIn("Could not parse latest Pi-hole version from GitHub.", out)

    def test_missing_pihole_command_is_reported(self):
        with patch.dict(sys.modules, {"requests": fake_requests({})}), \
                patch.object(pihole_admin.subprocess, "run", side_effect=FileNotFoundError), \
                self.assertLogs(LOGGER, "ERROR") as logs:
            self.admin.check_for_updates()
        self.assertIn("Pi-hole command not found", "\n".join(logs.output))


class CommandFailureTests(AdminTestCase):
    def test_gravity_update_that_cannot_start_is_reported(self):
        with patch.object(pihole_admin.subprocess, "Popen", side_effect=PermissionError("denied")), \
                self.assertLogs(LOGGER, "ERROR") as logs:
            self.admin.update_gravity()
        self.assertIn("Could not run 'pihole -g': denied", "\n".join(logs.output))

    def test_pihole_update_that_cannot_start_is_reported(self):
        with patch.object(pihole_admin.subprocess, "run", side_effect=PermissionError("denied")), \
                patch("builtins.print"), \
                self.assertLogs(LOGGER, "ERROR") as logs:
            self.admin.update_pihole()
        self.assertIn("Could not run 'pihole -up': denied", "\n".join(logs.output))


class DatabaseTests(AdminTestCase):
    def test_custom_statement_without_rows_does_not_crash(self):
        self.run_sql(self.queries, "INSERT INTO query_storage (timestamp, domain) VALUES (1, 'a.example')")
        with self.assertLogs(LOGGER, "INFO") as logs:
            result = self.admin.run_custom_query("DELETE FROM query_storage")
        self.assertEqual(result, [])
        self.assertIn("1 rows changed", "\n".join(logs.output))
        self.assertEqual(self.run_sql(self.queries, "SELECT COUNT(*) FROM query_storage"), [(0,)])

    def test_custom_select_still_returns_rows(self):
        self.run_sql(self.queries, "INSERT INTO query_storage (timestamp, domain) VALUES (1, 'a.example')")
        with self.assertLogs(LOGGER, "INFO"):
            result = self.admin.run_custom_query("SELECT domain FROM query_storage")
        self.assertEqual(result, [{"domain": "a.example"}])

    def test_clean_removes_only_old_queries(self):
        now = int(pihole_admin.time.time())
        self.run_sql(self.queries, "INSERT INTO query_storage (timestamp, domain) VALUES (?, 'old'), (?, 'new')",
                     (now - 40 * 86400, now - 86400))
        with self.assertLogs(LOGGER, "INFO"):
            self.admin.clean_old_data(30)
        self.assertEqual(self.run_sql(self.queries, "SELECT domain FROM query_storage"), [("new",)])

    def test_gravity_update_time_is_shown_in_local_time(self):
        cases = (("1700000000", pihole_admin.datetime.fromtimestamp(1700000000)
                  .strftime("%m-%d-%Y %I:%M:%S %p")),
                 ("99999999999999999999", "Invalid timestamp"),
                 ("soon", "Invalid timestamp"))
        for stored, shown in cases:
            with self.subTest(stored=stored):
                self.run_sql(self.gravity, "INSERT OR REPLACE INTO info VALUES ('updated', ?)", (stored,))
                with self.assertLogs(LOGGER, "INFO"):
                    stats = self.admin.get_statistics()
                self.assertEqual(stats["last_gravity_update"], shown)

    def test_similarity_scores_are_whole_numbers(self):
        self.run_sql(self.gravity, "INSERT INTO domainlist (type, domain, enabled) VALUES"
                                   " (1, 'ads.example.com', 1), (1, 'ad.example.com', 1)")
        with self.assertLogs(LOGGER, "INFO"):
            similar = self.admin.find_similar_domains(80)
        (match,) = similar["ads.example.com"]
        self.assertEqual(match[0], "ad.example.com")
        self.assertIsInstance(match[2], int)


class ChartTests(AdminTestCase):
    def in_directory(self, path):
        old = os.getcwd()
        os.chdir(path)
        self.addCleanup(os.chdir, old)

    def test_charts_without_matplotlib_give_an_install_hint(self):
        with patch.dict(sys.modules, {"matplotlib": None, "matplotlib.pyplot": None}), \
                self.assertLogs(LOGGER, "ERROR") as logs:
            self.admin.generate_charts(TOP, TOP)
        self.assertIn("pip install matplotlib", "\n".join(logs.output))

    @unittest.skipUnless(HAVE_MATPLOTLIB, "matplotlib is not installed")
    def test_chart_is_saved(self):
        self.in_directory(self.tmp.name)
        with self.assertLogs(LOGGER, "INFO") as logs:
            self.admin.generate_charts(TOP, TOP)
        self.assertTrue(Path(self.tmp.name, "pihole_domain_stats.png").stat().st_size > 0)
        self.assertIn("Charts saved as pihole_domain_stats.png", "\n".join(logs.output))

    @unittest.skipUnless(HAVE_MATPLOTLIB, "matplotlib is not installed")
    def test_unwritable_chart_is_reported(self):
        locked = Path(self.tmp.name, "locked")
        locked.mkdir(mode=0o555)
        self.addCleanup(locked.chmod, 0o755)
        self.in_directory(locked)
        with self.assertLogs(LOGGER, "ERROR") as logs:
            self.admin.generate_charts(TOP, TOP)
        self.assertIn("Error generating charts", "\n".join(logs.output))
        self.assertNotIn("Charts saved", "\n".join(logs.output))


if __name__ == "__main__":
    unittest.main()
