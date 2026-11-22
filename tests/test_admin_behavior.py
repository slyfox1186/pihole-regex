"""Check pihole_admin.py's database, update and chart code against disposable databases and fakes."""

import importlib.util
import io
import os
import signal
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import pihole_admin

LOGGER = "PiholeDBAdmin"
HAVE_MATPLOTLIB = importlib.util.find_spec("matplotlib") is not None
TOP = [{"domain": "ads.example.com", "count": 3}]
# The domain list tables and triggers of a live Pi-hole v6.9 gravity.db.
GRAVITY_SCHEMA = """
CREATE TABLE "group" (id INTEGER PRIMARY KEY AUTOINCREMENT, enabled BOOLEAN NOT NULL DEFAULT 1,
    name TEXT UNIQUE NOT NULL, date_added INTEGER NOT NULL DEFAULT (cast(strftime('%s', 'now') as int)),
    date_modified INTEGER NOT NULL DEFAULT (cast(strftime('%s', 'now') as int)), description TEXT);
CREATE TABLE domainlist (id INTEGER PRIMARY KEY AUTOINCREMENT, type INTEGER NOT NULL DEFAULT 0,
    domain TEXT NOT NULL, enabled BOOLEAN NOT NULL DEFAULT 1,
    date_added INTEGER NOT NULL DEFAULT (cast(strftime('%s', 'now') as int)),
    date_modified INTEGER NOT NULL DEFAULT (cast(strftime('%s', 'now') as int)),
    comment TEXT, UNIQUE(domain, type));
CREATE TABLE domainlist_by_group (domainlist_id INTEGER NOT NULL REFERENCES domainlist (id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES "group" (id) ON DELETE CASCADE,
    PRIMARY KEY (domainlist_id, group_id)) WITHOUT ROWID;
CREATE TRIGGER tr_domainlist_delete AFTER DELETE ON domainlist
    BEGIN DELETE FROM domainlist_by_group WHERE domainlist_id = OLD.id; END;
CREATE TRIGGER tr_domainlist_add AFTER INSERT ON domainlist
    BEGIN INSERT INTO domainlist_by_group (domainlist_id, group_id) VALUES (NEW.id, 0); END;
INSERT INTO "group" (id, enabled, name) VALUES (0, 1, 'Default'), (1, 1, 'Kids');
"""


UPDATER = ("pihole", "-up")
CHECKER = ("pihole", "updatechecker")
# /etc/pihole/versions of a live Pi-hole v6 that is fully up to date.
VERSIONS = {
    "CORE_VERSION": "v6.6", "CORE_BRANCH": "master", "CORE_HASH": "f7c0220e",
    "GITHUB_CORE_VERSION": "v6.6", "GITHUB_CORE_HASH": "f7c0220e",
    "WEB_VERSION": "v6.6.1", "WEB_BRANCH": "master", "WEB_HASH": "fb699c4e",
    "GITHUB_WEB_VERSION": "v6.6.1", "GITHUB_WEB_HASH": "fb699c4e",
    "FTL_VERSION": "v6.9", "FTL_BRANCH": "master", "FTL_HASH": "2a0fcb74",
    "GITHUB_FTL_VERSION": "v6.9", "GITHUB_FTL_HASH": "2a0fcb74",
}


class AdminTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.gravity = root / "gravity.db"
        self.queries = root / "pihole-FTL.db"
        with sqlite3.connect(self.gravity) as conn:
            conn.executescript("CREATE TABLE info (property TEXT PRIMARY KEY, value TEXT);" + GRAVITY_SCHEMA)
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
    def check(self, values=None, root=True, answer="n", installs=None, press_ctrl_c=False,
              refreshes=True, **changes):
        """Run the update check on a versions file; `installs` is what 'pihole -up' changes in it."""
        values = dict(VERSIONS if values is None else values, **changes)
        path = Path(self.tmp.name, "versions")

        def write():
            fresh = path.with_suffix(".new")
            fresh.write_text("".join(f"{key}={value}\n" for key, value in values.items()))
            os.replace(fresh, path)

        def run(argv, **_kwargs):
            self.commands.append(tuple(argv))
            if tuple(argv) == CHECKER and refreshes:
                write()
            if tuple(argv) == UPDATER:
                if press_ctrl_c:
                    signal.getsignal(signal.SIGINT)(signal.SIGINT, None)
                if installs is not None:
                    values.update(installs)
                    write()
            return subprocess.CompletedProcess(argv, 0, "", "")

        write()
        self.commands = []
        reply = {"side_effect": EOFError} if answer is None else {"return_value": answer}
        with patch.object(pihole_admin, "VERSIONS_FILE", str(path)), \
                patch.object(pihole_admin.subprocess, "run", run), \
                patch.object(pihole_admin.os, "geteuid", return_value=0 if root else 1000), \
                patch("builtins.input", **reply), \
                self.assertLogs(LOGGER, "INFO") as logs:
            self.admin.check_for_updates()
        return "\n".join(logs.output)

    def test_up_to_date_offers_nothing(self):
        out = self.check()
        self.assertIn("Core: installed v6.6, latest v6.6 (up to date)", out)
        self.assertIn("Pi-hole is up to date.", out)
        self.assertEqual(self.commands, [CHECKER])

    def test_a_web_or_ftl_release_is_noticed(self):
        for changes, found in (({"GITHUB_WEB_VERSION": "v6.7"}, "Update available: Web v6.7"),
                               ({"GITHUB_FTL_VERSION": "v6.10"}, "Update available: FTL v6.10"),
                               ({"GITHUB_CORE_VERSION": "v6.6.1"}, "Update available: Core v6.6.1")):
            with self.subTest(changes=changes):
                out = self.check(**changes)
                self.assertIn(found, out)
                self.assertIn("Update skipped by user.", out)
                self.assertNotIn(UPDATER, self.commands)

    def test_installed_ahead_of_the_latest_release_is_not_an_update(self):
        out = self.check(CORE_VERSION="v6.7", FTL_VERSION="v6.9-4-gabc1234")
        self.assertIn("Pi-hole is up to date.", out)

    def test_latest_version_not_looked_up_offers_nothing(self):
        for changes in ({"GITHUB_CORE_VERSION": "null"}, {"GITHUB_CORE_VERSION": ""}, {"CORE_VERSION": "null"}):
            with self.subTest(changes=changes):
                out = self.check(GITHUB_FTL_VERSION="v6.10", answer="y", **changes)
                self.assertIn("Cannot compare versions for Core", out)
                self.assertNotIn(UPDATER, self.commands)

    def test_yes_updates_and_confirms_the_new_version(self):
        out = self.check(GITHUB_FTL_VERSION="v6.10", answer="y", installs={"FTL_VERSION": "v6.10"})
        self.assertEqual(self.commands, [CHECKER, UPDATER])
        self.assertIn("Update finished. Installed now: FTL v6.10", out)

    def test_update_that_changes_nothing_is_reported_as_failed(self):
        out = self.check(GITHUB_FTL_VERSION="v6.10", GITHUB_WEB_VERSION="v6.7", answer="y",
                         installs={"WEB_VERSION": "v6.7"})
        self.assertIn("ERROR:PiholeDBAdmin:Pi-hole update failed: FTL not updated.", out)
        self.assertNotIn("Update finished", out)

    def test_closed_input_skips_the_update(self):
        out = self.check(GITHUB_CORE_VERSION="v6.7", answer=None)
        self.assertIn("No answer, so Pi-hole was not updated.", out)
        self.assertNotIn(UPDATER, self.commands)

    def test_without_root_it_reads_the_saved_versions_and_names_the_command(self):
        out = self.check(GITHUB_CORE_VERSION="v6.7", root=False, answer="y")
        self.assertIn("Run with sudo for a fresh check.", out)
        self.assertIn("Updating needs root. Run: sudo pihole -up", out)
        self.assertEqual(self.commands, [])

    def test_docker_install_is_pointed_at_the_image(self):
        for changes in ({"GITHUB_CORE_VERSION": "v6.7"}, {}):
            with self.subTest(changes=changes):
                out = self.check(DOCKER_VERSION="2026.11.0", answer="y", **changes)
                self.assertIn("runs in Docker", out)
                self.assertNotIn("Pi-hole is up to date.", out)
                self.assertNotIn(UPDATER, self.commands)
        out = self.check(DOCKER_VERSION="2026.11.0", GITHUB_CORE_VERSION="null")
        self.assertIn("ERROR:PiholeDBAdmin:Cannot compare versions for Core", out)

    def test_pihole_v5_file_without_web_interface_or_hashes(self):
        # The keys Pi-hole v5.13 writes when the web interface is not installed.
        v5 = {"CORE_VERSION": "v5.18.2", "CORE_BRANCH": "master", "GITHUB_CORE_VERSION": "v5.18.3",
              "FTL_VERSION": "v5.25.2", "FTL_BRANCH": "master", "GITHUB_FTL_VERSION": "v5.25.2"}
        out = self.check(v5)
        self.assertIn("Update available: Core v5.18.3", out)
        self.assertNotIn("Web:", out)

    def test_other_branch_compares_commit_hashes(self):
        out = self.check(FTL_BRANCH="development", FTL_HASH="aaaaaaaa", GITHUB_FTL_HASH="bbbbbbbb",
                         GITHUB_FTL_VERSION="null", answer="y", installs={"FTL_HASH": "bbbbbbbb"})
        self.assertIn("FTL: installed development aaaaaaaa, latest bbbbbbbb (update available)", out)
        self.assertIn("Update finished. Installed now: FTL development bbbbbbbb", out)
        out = self.check(FTL_BRANCH="development", GITHUB_FTL_VERSION="null")
        self.assertIn("Pi-hole is up to date.", out)

    def test_other_branch_that_moved_on_during_the_update_still_counts(self):
        out = self.check(FTL_BRANCH="development", FTL_HASH="aaaaaaaa", GITHUB_FTL_HASH="bbbbbbbb", answer="y",
                         installs={"FTL_HASH": "cccccccc", "GITHUB_FTL_HASH": "cccccccc"})
        self.assertIn("Update finished. Installed now: FTL development cccccccc", out)

    def test_other_branch_on_a_commit_nobody_offered_is_reported_as_failed(self):
        out = self.check(FTL_BRANCH="development", FTL_HASH="aaaaaaaa", GITHUB_FTL_HASH="bbbbbbbb", answer="y",
                         installs={"FTL_HASH": "cccccccc"})
        self.assertIn("Pi-hole update failed: FTL not updated.", out)

    def test_hashes_of_different_lengths_for_one_commit_are_not_an_update(self):
        # Pi-hole v5.14 records 7 characters of the installed hash and 8 of the latest.
        out = self.check(CORE_BRANCH="development", CORE_HASH="abcdef1", GITHUB_CORE_HASH="abcdef12", answer="y")
        self.assertIn("Pi-hole is up to date.", out)
        self.assertNotIn(UPDATER, self.commands)

    def test_bare_commit_hash_in_place_of_a_version_offers_nothing(self):
        out = self.check(CORE_VERSION="8badf00", GITHUB_CORE_VERSION="v6.7", answer="y")
        self.assertIn("Cannot compare versions for Core", out)
        self.assertNotIn(UPDATER, self.commands)

    def test_record_without_ftl_is_refused(self):
        core_only = {"CORE_VERSION": "v6.6", "CORE_BRANCH": "master", "GITHUB_CORE_VERSION": "v6.6"}
        out = self.check(core_only)
        self.assertIn("has no version for FTL.", out)
        self.assertNotIn("up to date", out)

    def test_versions_that_were_not_refreshed_are_not_trusted(self):
        out = self.check(GITHUB_CORE_VERSION="v6.7", answer="y", refreshes=False)
        self.assertIn("did not rewrite", out)
        self.assertEqual(self.commands, [CHECKER])

    def test_ctrl_c_is_left_to_the_updater_then_ends_the_script(self):
        before = signal.getsignal(signal.SIGINT)
        # Whether or not the update still went through, Ctrl+C ends the script afterwards,
        # so an option given after --check-updates never runs.
        for installs in (None, {"CORE_VERSION": "v6.7"}):
            with self.subTest(installs=installs), self.assertRaises(KeyboardInterrupt):
                self.check(GITHUB_CORE_VERSION="v6.7", answer="y", press_ctrl_c=True, installs=installs)
            self.assertEqual(self.commands, [CHECKER, UPDATER])
            self.assertIs(signal.getsignal(signal.SIGINT), before)

    def test_ctrl_c_while_the_updater_fails_to_start_still_ends_the_script(self):
        def run(_argv, **_kwargs):
            signal.getsignal(signal.SIGINT)(signal.SIGINT, None)
            raise PermissionError("denied")

        with patch.object(pihole_admin.subprocess, "run", run), self.assertLogs(LOGGER, "ERROR") as logs, \
                self.assertRaises(KeyboardInterrupt):
            self.admin.update_pihole([])
        self.assertIn("Could not run 'pihole -up': denied", "\n".join(logs.output))

    def test_missing_versions_file_is_reported(self):
        with patch.object(pihole_admin, "VERSIONS_FILE", str(Path(self.tmp.name, "missing"))), \
                patch.object(pihole_admin.os, "geteuid", return_value=1000), \
                self.assertLogs(LOGGER, "ERROR") as logs:
            self.admin.check_for_updates()
        self.assertIn("Could not read Pi-hole's versions", "\n".join(logs.output))

    def test_missing_pihole_command_is_reported(self):
        with patch.object(pihole_admin.subprocess, "run", side_effect=FileNotFoundError), \
                patch.object(pihole_admin.os, "geteuid", return_value=0), \
                self.assertLogs(LOGGER, "ERROR") as logs:
            self.admin.check_for_updates()
        self.assertIn("Pi-hole command not found", "\n".join(logs.output))


class VersionCompareTests(unittest.TestCase):
    def state(self, installed, latest):
        return pihole_admin.Component("Core", installed, latest, "master", "a", "a").state

    def test_versions_compare_as_numbers(self):
        for installed, latest, expected in (
                ("v6.9", "v6.10", pihole_admin.UPDATE_AVAILABLE), ("v6.10", "v6.9", pihole_admin.UP_TO_DATE),
                ("v6.6", "v6.6.1", pihole_admin.UPDATE_AVAILABLE), ("v6.6", "v6.6.0", pihole_admin.UP_TO_DATE),
                ("v5.18.4", "v6.0", pihole_admin.UPDATE_AVAILABLE), ("", "v6.6", pihole_admin.UNKNOWN),
                ("v6.6-3-gabc1234", "v6.6", pihole_admin.UP_TO_DATE), ("8badf00", "v6.7", pihole_admin.UNKNOWN),
                # Pi-hole v5.14 records `git describe --long --dirty --tags`.
                ("v5.14-0-gabcdef1-dirty", "v5.15", pihole_admin.UPDATE_AVAILABLE),
                ("6.6", "v6.6", pihole_admin.UNKNOWN), ("v6.6", "N/A", pihole_admin.UNKNOWN)):
            with self.subTest(installed=installed, latest=latest):
                self.assertEqual(self.state(installed, latest), expected)


class CommandFailureTests(AdminTestCase):
    def test_gravity_update_that_cannot_start_is_reported(self):
        with patch.object(pihole_admin.subprocess, "Popen", side_effect=PermissionError("denied")), \
                self.assertLogs(LOGGER, "ERROR") as logs:
            self.admin.update_gravity()
        self.assertIn("Could not run 'pihole -g': denied", "\n".join(logs.output))

    def test_pihole_update_that_cannot_start_is_reported(self):
        with patch.object(pihole_admin.subprocess, "run", side_effect=PermissionError("denied")), \
                self.assertLogs(LOGGER, "ERROR") as logs:
            self.admin.update_pihole([])
        self.assertIn("Could not run 'pihole -up': denied", "\n".join(logs.output))


class PathTests(AdminTestCase):
    def test_cron_path_gains_the_folders_pihole_needs(self):
        with patch.dict(os.environ, {"PATH": "/usr/bin:/bin"}):
            pihole_admin.extend_path()
            self.assertEqual(os.environ["PATH"], "/usr/bin:/bin:/usr/sbin:/usr/local/bin")
            pihole_admin.extend_path()
            self.assertEqual(os.environ["PATH"], "/usr/bin:/bin:/usr/sbin:/usr/local/bin")

    def test_main_extends_the_path_before_it_runs_a_command(self):
        seen = []

        def admin():
            seen.append(os.environ["PATH"])
            return self.admin

        with patch.object(sys, "argv", ["pihole_admin.py", "--clean", "30"]), \
                patch.object(pihole_admin, "PiholeDBAdmin", admin), \
                patch.dict(os.environ, {"PATH": "/usr/bin:/bin"}), self.assertLogs(LOGGER, "INFO"):
            pihole_admin.main()
        self.assertEqual(seen, ["/usr/bin:/bin:/usr/sbin:/usr/local/bin"])


class ExitCodeTests(AdminTestCase):
    def run_main(self, *argv):
        with patch.object(sys, "argv", ["pihole_admin.py", *argv]), \
                patch.object(pihole_admin, "PiholeDBAdmin", return_value=self.admin), \
                patch.dict(os.environ), self.assertLogs(LOGGER, "INFO"):
            return pihole_admin.main()

    def test_a_failed_command_exits_one(self):
        self.assertEqual(self.run_main("--advanced-query", "SELECT no_such_column FROM queries"), 1)

    def test_one_failure_among_several_commands_exits_one(self):
        self.assertEqual(self.run_main("--clean", "30", "--advanced-query", "SELECT nope"), 1)

    def test_success_exits_zero(self):
        self.assertEqual(self.run_main("--clean", "30"), 0)

    def test_the_error_counter_is_detached_afterwards(self):
        # Not through run_main: assertLogs swaps the handler list and would hide a leftover.
        with patch.object(sys, "argv", ["pihole_admin.py", "--advanced-query", "SELECT nope"]), \
                patch.object(pihole_admin, "PiholeDBAdmin", return_value=self.admin), \
                patch.dict(os.environ), patch.object(self.admin.logger, "disabled", True):
            pihole_admin.main()
        self.assertFalse(any(isinstance(handler, pihole_admin.ErrorCounter)
                             for handler in self.admin.logger.handlers))
        self.assertEqual(self.run_main("--clean", "30"), 0)

    def test_run_passes_the_exit_code_on(self):
        with patch.object(pihole_admin, "main", return_value=1), self.assertRaises(SystemExit) as caught:
            pihole_admin.run()
        self.assertEqual(caught.exception.code, 1)


class DatabaseTests(AdminTestCase):
    def test_statistic_whose_query_fails_is_an_error(self):
        # The test database has no gravity table, so that count cannot be made.
        with self.assertLogs(LOGGER, "ERROR") as logs:
            stats = self.admin.get_statistics()
        self.assertIn("Query failed: SELECT COUNT(*) FROM gravity", "\n".join(logs.output))
        self.assertEqual(stats["total_domains"], 0)

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


class DuplicateTests(AdminTestCase):
    def add(self, list_type, domain, enabled=1, comment=None, groups=None):
        with sqlite3.connect(self.gravity) as conn:
            row_id = conn.execute("INSERT INTO domainlist (type, domain, enabled, comment) VALUES (?, ?, ?, ?)",
                                  (list_type, domain, enabled, comment)).lastrowid
            if groups is not None:
                conn.execute("DELETE FROM domainlist_by_group WHERE domainlist_id = ?", (row_id,))
                conn.executemany("INSERT INTO domainlist_by_group VALUES (?, ?)", [(row_id, g) for g in groups])
        conn.close()
        return row_id

    def rows(self):
        return self.run_sql(self.gravity, "SELECT id, type, domain FROM domainlist ORDER BY id")

    def plan(self):
        with self.assertLogs(LOGGER, "INFO"):
            return self.admin.find_duplicates()

    def removed_ids(self, plan):
        return [(r.entry.id, r.keeper.id) for r in plan.removals]

    def test_www_pairs_are_not_duplicates(self):
        self.add(0, "g2a.com")
        self.add(0, "www.g2a.com")
        plan = self.plan()
        self.assertEqual((plan.removals, plan.overlaps), ([], []))

    def test_capitalized_copy_goes_and_the_lowercase_entry_stays(self):
        upper = self.add(1, "Ads.Example.com", comment="old", groups=[0, 1])
        lower = self.add(1, "ads.example.com", enabled=0)
        self.assertEqual(self.removed_ids(self.plan()), [(upper, lower)])

    def test_all_capitalized_copies_keep_the_oldest(self):
        first = self.add(1, "ADS.example.com")
        second = self.add(1, "Ads.example.com")
        self.assertEqual(self.removed_ids(self.plan()), [(second, first)])

    def test_regex_and_non_ascii_entries_are_left_alone(self):
        self.add(3, r"^\w+\.example$")
        self.add(3, r"^\W+\.example$")
        self.add(3, "^a\\.example$;querytype=A")
        self.add(3, "^a\\.example$;QUERYTYPE=A")
        self.add(1, "bücher.example")
        self.add(1, "BÜCHER.example")
        self.assertEqual(self.plan().removals, [])

    def test_allow_and_deny_overlap_is_reported_but_kept(self):
        allow = self.add(0, "Example.com")
        deny = self.add(1, "example.com")
        regex_allow = self.add(2, "^x$")
        regex_deny = self.add(3, "^x$")
        plan = self.plan()
        self.assertEqual(plan.removals, [])
        self.assertEqual([(a.id, d.id) for a, d in plan.overlaps], [(allow, deny), (regex_allow, regex_deny)])

    def test_capitalized_copy_on_an_overlap_still_goes(self):
        upper = self.add(0, "Example.com")
        lower = self.add(0, "example.com")
        deny = self.add(1, "example.com")
        asked, out = self.run_command(["n", "y"])
        self.assertEqual(asked.call_count, 2)
        self.assertIn("this alone removes nothing", out)
        self.assertIn(f"remove #{upper} Example.com", out)
        self.assertEqual([row[0] for row in self.rows()], [lower, deny])

    def test_preview_reads_one_snapshot_and_releases_it(self):
        self.add(1, "Ads.example.com")
        self.add(1, "ads.example.com")
        seen = []
        original = pihole_admin.read_domainlist

        def checked(conn):
            seen.append(conn.in_transaction)
            return original(conn)

        with patch.object(pihole_admin, "read_domainlist", checked):
            self.plan()
        self.assertEqual(seen, [True])
        with sqlite3.connect(self.gravity, isolation_level=None, timeout=0) as writer:
            writer.execute("BEGIN IMMEDIATE")
            writer.execute("ROLLBACK")
        writer.close()

    def remove(self, plan):
        with self.assertLogs(LOGGER, "INFO"):
            return self.admin.remove_duplicates(plan)

    def test_removal_deletes_the_row_and_its_group_links(self):
        upper = self.add(1, "Ads.example.com", groups=[0, 1])
        lower = self.add(1, "ads.example.com")
        removed, skipped = self.remove(self.plan())
        self.assertEqual(([e.id for e in removed], skipped), ([upper], []))
        self.assertEqual(self.rows(), [(lower, 1, "ads.example.com")])
        self.assertEqual(self.run_sql(self.gravity, "SELECT domainlist_id FROM domainlist_by_group"), [(lower,)])

    def test_entries_changed_after_they_were_shown_are_skipped(self):
        changes = (
            "UPDATE domainlist SET domain = 'ADS.example.com' WHERE id = {upper}",
            "UPDATE domainlist SET enabled = 0 WHERE id = {upper}",
            "UPDATE domainlist SET comment = 'new' WHERE id = {upper}",
            "INSERT INTO domainlist_by_group VALUES ({upper}, 1)",
            "UPDATE domainlist SET comment = 'new' WHERE id = {lower}",
            "DELETE FROM domainlist WHERE id = {lower}",
        )
        for change in changes:
            with self.subTest(change=change):
                self.run_sql(self.gravity, "DELETE FROM domainlist")
                upper = self.add(1, "Ads.example.com")
                lower = self.add(1, "ads.example.com")
                plan = self.plan()
                self.run_sql(self.gravity, change.format(upper=upper, lower=lower))
                before = self.rows()
                removed, skipped = self.remove(plan)
                self.assertEqual(([e.id for e in skipped], removed), ([upper], []))
                self.assertEqual(self.rows(), before)

    def test_a_failed_removal_changes_nothing(self):
        self.add(1, "Ads.example.com")
        self.add(1, "ADS.example.com")
        self.add(1, "ads.example.com")
        plan = self.plan()
        self.run_sql(self.gravity, "CREATE TRIGGER fail_second BEFORE DELETE ON domainlist"
                                   " WHEN OLD.domain = 'ADS.example.com' BEGIN SELECT RAISE(ABORT, 'boom'); END")
        before = (self.rows(), self.run_sql(self.gravity, "SELECT * FROM domainlist_by_group ORDER BY 1"))
        with self.assertLogs(LOGGER, "ERROR") as logs:
            self.assertIsNone(self.admin.remove_duplicates(plan))
        self.assertIn("Nothing was removed", "\n".join(logs.output))
        self.assertEqual((self.rows(), self.run_sql(self.gravity, "SELECT * FROM domainlist_by_group ORDER BY 1")),
                         before)

    def run_command(self, answer=None, assume_yes=False, script_dir=None):
        if answer is None:
            reply = {"side_effect": EOFError}
        elif isinstance(answer, list):
            reply = {"side_effect": answer}
        else:
            reply = {"return_value": answer}
        script = Path(script_dir or self.tmp.name, "pihole_admin.py")
        out = io.StringIO()
        with patch("builtins.input", **reply) as asked, patch.object(pihole_admin, "__file__", str(script)), \
                redirect_stdout(out), self.assertLogs(LOGGER, "INFO") as logs:
            pihole_admin.remove_duplicates(self.admin, assume_yes)
        return asked, out.getvalue() + "\n".join(logs.output)

    def two_copies(self):
        self.run_sql(self.gravity, "DELETE FROM domainlist")
        self.add(1, "Ads.example.com")
        self.add(1, "ads.example.com")

    def test_list_can_be_saved_before_anything_is_removed(self):
        self.two_copies()
        saved = Path(self.tmp.name, "duplicate-domains.txt")
        asked, out = self.run_command(["y", "n"])
        self.assertEqual(asked.call_count, 2)
        self.assertIn(f"Saved the list to {saved}", out)
        self.assertIn("remove #1 Ads.example.com", saved.read_text())
        self.assertIn("Nothing was removed.", out)
        self.assertEqual(len(self.rows()), 2)

    def test_unsaved_list_still_lets_you_remove(self):
        self.two_copies()
        asked, out = self.run_command(["y", "y"], script_dir=Path(self.tmp.name, "missing"))
        self.assertEqual(asked.call_count, 2)
        self.assertIn("ERROR:PiholeDBAdmin:Could not save the list", out)
        self.assertIn("Removed 1 entries.", out)

    def test_yes_neither_asks_nor_saves(self):
        self.two_copies()
        asked, _out = self.run_command(assume_yes=True)
        asked.assert_not_called()
        self.assertFalse(Path(self.tmp.name, "duplicate-domains.txt").exists())
        self.assertEqual(len(self.rows()), 1)

    def remove_with_failure(self, fail_on):
        """Run remove_duplicates on a connection whose statement `fail_on` raises."""
        real_connect = sqlite3.connect
        deletes = []

        class FailingConnection(sqlite3.Connection):
            def execute(self, sql, *args):
                if sql.startswith("DELETE"):
                    deletes.append(sql)
                if fail_on == "COMMIT" and sql == "COMMIT":
                    raise sqlite3.OperationalError("disk I/O error")
                if fail_on == "second DELETE" and len(deletes) == 2 and sql.startswith("DELETE"):
                    raise KeyboardInterrupt
                return super().execute(sql, *args)

        def connect(*args, **kwargs):
            return real_connect(*args, factory=FailingConnection, **kwargs)

        plan = self.plan()
        with patch.object(pihole_admin.sqlite3, "connect", connect):
            return self.admin.remove_duplicates(plan)

    def three_copies(self):
        self.add(1, "Ads.example.com")
        self.add(1, "ADS.example.com")
        self.add(1, "ads.example.com")
        return (self.rows(), self.run_sql(self.gravity, "SELECT * FROM domainlist_by_group ORDER BY 1"))

    def test_failed_commit_changes_nothing(self):
        before = self.three_copies()
        with self.assertLogs(LOGGER, "ERROR") as logs:
            self.assertIsNone(self.remove_with_failure("COMMIT"))
        self.assertIn("Nothing was removed. Error removing duplicate entries: disk I/O error",
                      "\n".join(logs.output))
        self.assertEqual((self.rows(), self.run_sql(self.gravity, "SELECT * FROM domainlist_by_group ORDER BY 1")),
                         before)

    def test_ctrl_c_during_removal_changes_nothing(self):
        before = self.three_copies()
        with self.assertRaises(KeyboardInterrupt):
            self.remove_with_failure("second DELETE")
        self.assertEqual((self.rows(), self.run_sql(self.gravity, "SELECT * FROM domainlist_by_group ORDER BY 1")),
                         before)

    def test_command_asks_before_removing(self):
        for answer, assume_yes, kept in ((None, False, 2), ("n", False, 2), ("y", False, 1), (None, True, 1)):
            with self.subTest(answer=answer, assume_yes=assume_yes):
                self.run_sql(self.gravity, "DELETE FROM domainlist")
                self.add(1, "Ads.example.com")
                self.add(1, "ads.example.com")
                asked, out = self.run_command(answer, assume_yes)
                self.assertEqual(len(self.rows()), kept)
                self.assertEqual(asked.called, not assume_yes)
                self.assertIn("remove #", out)
                if answer is None and not assume_yes:
                    self.assertIn("Add --yes to remove without asking.", out)
                if kept == 1:
                    self.assertIn("Removed 1 entries.", out)

    def test_command_with_nothing_to_remove_does_not_ask(self):
        self.add(0, "www.example.com")
        self.add(0, "example.com")
        asked, out = self.run_command("y")
        asked.assert_not_called()
        self.assertIn("No duplicate entries found.", out)
        self.assertEqual(len(self.rows()), 2)


class CancelTests(unittest.TestCase):
    def test_ctrl_c_exits_130_with_a_short_message(self):
        err = io.StringIO()
        with patch.object(pihole_admin, "main", side_effect=KeyboardInterrupt), redirect_stderr(err), \
                self.assertRaises(SystemExit) as caught:
            pihole_admin.run()
        self.assertEqual(caught.exception.code, 130)
        self.assertEqual(err.getvalue(), "\nCancelled.\n")


class ListEditTests(AdminTestCase):
    def test_www_stays_part_of_the_name(self):
        with self.assertLogs(LOGGER, "INFO"):
            self.admin.add_domains_to_list(["HTTPS://WWW.Example.com/", "example.com"], 1)
        self.assertEqual(self.run_sql(self.gravity, "SELECT domain FROM domainlist ORDER BY id"),
                         [("www.example.com",), ("example.com",)])
        with self.assertLogs(LOGGER, "INFO"):
            self.admin.remove_domains_from_list(["www.example.com"], 1)
        self.assertEqual(self.run_sql(self.gravity, "SELECT domain FROM domainlist"), [("example.com",)])


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
