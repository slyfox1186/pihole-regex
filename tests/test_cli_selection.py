"""Exercise CLI selections against disposable databases without contacting Pi-hole."""

import io
import sqlite3
import tempfile
import unittest
from contextlib import ExitStack, closing, redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from scripts import adlist, pi


class AdlistSelectionTests(unittest.TestCase):
    def setUp(self):
        self.source = [f"https://example.test/{name}" for name in ("off", "on", "manual", "new")]
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.serial = 0

    def database(self, version=6, empty=False):
        self.serial += 1
        path = Path(self.temp.name) / f"gravity-{self.serial}.db"
        with closing(sqlite3.connect(path)) as db, db:
            type_column = ", type INTEGER NOT NULL DEFAULT 0" if version == 6 else ""
            db.execute(
                "CREATE TABLE adlist (id INTEGER PRIMARY KEY, address TEXT UNIQUE, "
                "enabled INTEGER, comment TEXT, date_added INTEGER DEFAULT 0, "
                f"date_modified INTEGER DEFAULT 0{type_column})"
            )
            if not empty:
                db.executemany(
                    "INSERT INTO adlist (address, enabled, comment) VALUES (?, ?, ?)",
                    [
                        (self.source[0], 0, adlist.COMMENT),
                        (self.source[1], 1, adlist.COMMENT),
                        (self.source[2], 0, "added manually"),
                        ("https://example.test/retired-off", 0, adlist.COMMENT),
                        ("https://example.test/retired-on", 1, adlist.COMMENT),
                        ("https://example.test/foreign", 1, "added manually"),
                    ],
                )
                if version == 6:
                    db.execute(
                        "INSERT INTO adlist (address, enabled, comment, type) VALUES (?, 0, ?, 1)",
                        ("https://example.test/allowlist", adlist.COMMENT),
                    )
        return path

    def snapshot(self, path):
        with closing(sqlite3.connect(path)) as db:
            return db.execute("SELECT * FROM adlist ORDER BY id").fetchall()

    def run_cli(self, path, *items, online=True, yes=True):
        argv = [*items, "--database", str(path), "--no-gravity", "--no-color"]
        if yes:
            argv.append("--yes")
        output = io.StringIO()
        with ExitStack() as stack:
            fetch = stack.enter_context(patch.object(adlist, "fetch_source", return_value=self.source))
            stack.enter_context(patch.object(
                adlist.subprocess, "run", side_effect=AssertionError("Unexpected subprocess")))
            stack.enter_context(patch.object(adlist.sys.stdin, "isatty", return_value=False))
            stack.enter_context(redirect_stdout(output))
            stack.enter_context(redirect_stderr(output))
            if not online:
                fetch.side_effect = adlist.AppError("Source unavailable")
            try:
                result = adlist.main(argv)
            except SystemExit as exc:
                self.fail(f"CLI rejected {items}: exit {exc.code}\n{output.getvalue()}")
        self.assertEqual(result, adlist.EXIT_OK)
        return output.getvalue()

    def test_toggle_all_preserves_manual_and_allowlist_rows(self):
        for version in (5, 6):
            for flag, enabled in (("-e", 1), ("--enable", 1), ("-d", 0), ("--disable", 0)):
                for selection in ([], ["all"], ["ALL"]):
                    with self.subTest(version=version, flag=flag, selection=selection):
                        path = self.database(version)
                        before = self.snapshot(path)
                        self.run_cli(path, flag, *selection)
                        expected = [
                            (*row[:2], enabled, *row[3:]) if row[0] in (1, 2, 4, 5) else row
                            for row in before
                        ]
                        self.assertEqual(self.snapshot(path), expected)

    def test_remove_all_requires_confirmation_and_preserves_unmanaged_rows(self):
        for flag in ("-r", "--remove", "--remove-all"):
            for selection in ([[], ["all"], ["ALL"]] if flag != "--remove-all" else [[]]):
                with self.subTest(flag=flag, selection=selection):
                    path = self.database()
                    before = self.snapshot(path)
                    output = self.run_cli(path, flag, *selection, yes=False)
                    self.assertIn("Cancelled", output)
                    self.assertEqual(self.snapshot(path), before)
                    self.run_cli(path, flag, *selection)
                    self.assertEqual(self.snapshot(path), [r for r in before if r[0] in (3, 6, 7)])

    def test_add_all_only_adds_missing_source_lists(self):
        for flag in ("-a", "--add"):
            for selection in ([], ["all"], ["ALL"]):
                with self.subTest(flag=flag, selection=selection):
                    path = self.database()
                    before = self.snapshot(path)
                    self.run_cli(path, flag, *selection)
                    after = self.snapshot(path)
                    self.assertEqual(after[:len(before)], before)
                    self.assertEqual(len(after), len(before) + 1)
                    self.assertEqual(after[-1][1:4], (self.source[3], 1, adlist.COMMENT))

    def test_all_installed_actions_work_offline(self):
        for flag in ("--enable", "--disable", "--remove"):
            for selection in ([], ["all"]):
                with self.subTest(flag=flag, selection=selection):
                    path = self.database()
                    self.run_cli(path, flag, *selection, online=False)
                    rows = self.snapshot(path)
                    managed = [row for row in rows if row[0] in (1, 2, 4, 5)]
                    if flag == "--remove":
                        self.assertEqual(managed, [])
                    else:
                        self.assertEqual([r[2] for r in managed], [int(flag == "--enable")] * 4)

    def test_explicit_selections_and_repeated_flags_stay_narrow(self):
        for selection, changed in (
            (["--disable", "2"], {2}), (["-d", "2,6"], {2, 5}),
            (["-d", "2 6"], {2, 5}),
            (["-d", "2", "6"], {2, 5}), (["-d", "2", "-d", "6"], {2, 5}),
            (["-d", "-d", "2"], {2}), (["-d", "2", "-d"], {2}),
            (["-d", self.source[1]], {2}),
        ):
            with self.subTest(selection=selection):
                path = self.database()
                before = self.snapshot(path)
                self.run_cli(path, *selection)
                expected = [(*r[:2], 0, *r[3:]) if r[0] in changed else r for r in before]
                self.assertEqual(self.snapshot(path), expected)

    def test_explicit_add_and_remove_stay_narrow(self):
        path = self.database(empty=True)
        self.run_cli(path, "--add", "2")
        self.assertEqual([row[1] for row in self.snapshot(path)], [self.source[1]])
        path = self.database()
        before = self.snapshot(path)
        self.run_cli(path, "--remove", "2", yes=False)
        self.assertEqual(self.snapshot(path), [row for row in before if row[0] != 2])

    def test_invalid_selections_never_change_the_database(self):
        for flag in ("--enable", "--disable", "--remove", "--add"):
            for selection in ([""], [" "], [" , "], ["2", "999"], ["all", "999"], ["2", "all"]):
                with self.subTest(flag=flag, selection=selection):
                    path = self.database()
                    before = self.snapshot(path)
                    with self.assertRaises(adlist.AppError):
                        self.run_cli(path, flag, *selection)
                    self.assertEqual(self.snapshot(path), before)

    def test_manual_selection_is_rejected_without_partial_changes(self):
        for flag in ("--enable", "--disable", "--remove"):
            with self.subTest(flag=flag):
                path = self.database()
                before = self.snapshot(path)
                with self.assertRaises(adlist.AppError):
                    self.run_cli(path, flag, "2,3")
                self.assertEqual(self.snapshot(path), before)

    def test_offline_add_and_number_selections_fail_without_changes(self):
        for selection in (["--add"], ["--add", "all"], ["--disable", "2"]):
            with self.subTest(selection=selection):
                path = self.database()
                before = self.snapshot(path)
                with self.assertRaises(adlist.AppError):
                    self.run_cli(path, *selection, online=False)
                self.assertEqual(self.snapshot(path), before)

    def test_offline_url_selection_stays_narrow(self):
        path = self.database()
        before = self.snapshot(path)
        self.run_cli(path, "--disable", self.source[1], online=False)
        self.assertEqual(self.snapshot(path), [(*r[:2], 0, *r[3:]) if r[0] == 2 else r for r in before])

    def test_dry_run_all_never_changes_database(self):
        for flag in ("--enable", "--disable", "--remove", "--add"):
            with self.subTest(flag=flag):
                path = self.database()
                before = self.snapshot(path)
                self.assertIn("Dry run", self.run_cli(path, flag, "--dry-run"))
                self.assertEqual(self.snapshot(path), before)

    def test_empty_database_all_is_safe(self):
        for flag in ("--enable", "--disable", "--remove"):
            with self.subTest(flag=flag):
                path = self.database(empty=True)
                self.assertIn("Nothing to change", self.run_cli(path, flag))
                self.assertEqual(self.snapshot(path), [])

    def test_plain_sync_still_adds_missing_and_removes_retired_lists(self):
        path = self.database()
        self.run_cli(path)
        rows = self.snapshot(path)
        self.assertEqual({row[0] for row in rows if row[0] < 8}, {1, 2, 3, 6, 7})
        self.assertEqual(rows[-1][1], self.source[3])

    def test_conflicting_actions_and_missing_database_path_are_usage_errors(self):
        for argv in (["--enable", "--disable"], ["--remove", "--add"],
                     ["--database"], ["--remove-all", "4"]):
            with self.subTest(argv=argv), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    adlist.build_parser().parse_args(argv)
                self.assertEqual(raised.exception.code, adlist.EXIT_USAGE)


class DomainListSelectionTests(unittest.TestCase):
    def test_existing_all_defaults_and_explicit_selections(self):
        for flag, command in (("--add", "cmd_add"), ("--remove", "cmd_remove"), ("--list", "cmd_list")):
            for selection, expected in (([], list(pi.KINDS)), (["all"], list(pi.KINDS)),
                                        (["ed,rd"], [pi.KINDS[1], pi.KINDS[3]])):
                with self.subTest(flag=flag, selection=selection):
                    with patch.object(pi, command, return_value=pi.EXIT_OK) as handler:
                        self.assertEqual(pi.main([flag, *selection]), pi.EXIT_OK)
                    self.assertEqual(handler.call_args.args[1], expected)

    def test_search_restore_and_database_still_require_values(self):
        for flag in ("--search", "--restore", "--database"):
            with self.subTest(flag=flag), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    pi.build_parser().parse_args([flag])
                self.assertEqual(raised.exception.code, pi.EXIT_USAGE)



class PiCommentRefreshTests(unittest.TestCase):
    """--add brings this script's comments in line with the repository and leaves the user's alone."""

    def test_add_updates_outdated_tagged_comments_only(self):
        kind = pi.KINDS[0]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "gravity.db"
            with closing(sqlite3.connect(path)) as db, db:
                db.execute("CREATE TABLE domainlist (id INTEGER PRIMARY KEY, type INTEGER, domain TEXT, "
                           "enabled INTEGER, comment TEXT, date_added INTEGER, date_modified INTEGER)")
                db.executemany("INSERT INTO domainlist (type, domain, enabled, comment) VALUES (?, ?, 1, ?)", [
                    (kind.type, "old.example.com", f"{kind.tag} - Misc"),
                    (kind.type, "same.example.com", f"{kind.tag} - Current note"),
                    (kind.type, "blank.example.com", ""),
                    (kind.type, "mine.example.com", "my own note"),
                ])
            source = [pi.SourceEntry("old.example.com", "Corrected note"),
                      pi.SourceEntry("same.example.com", "Current note"),
                      pi.SourceEntry("blank.example.com", "Filled in"),
                      pi.SourceEntry("mine.example.com", "Repository note")]
            with patch.object(pi, "fetch_sources", return_value={kind.type: source}), \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                code = pi.main(["--add", kind.key, "--yes", "--no-reload", "--database", str(path)])
            self.assertEqual(code, pi.EXIT_OK)
            with closing(sqlite3.connect(path)) as db:
                comments = dict(db.execute("SELECT domain, comment FROM domainlist"))
            self.assertEqual(comments, {
                "old.example.com": f"{kind.tag} - Corrected note",
                "same.example.com": f"{kind.tag} - Current note",
                "blank.example.com": f"{kind.tag} - Filled in",
                "mine.example.com": "my own note",
            })
            with patch.object(pi, "fetch_sources", return_value={kind.type: source}), \
                    redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()):
                self.assertEqual(pi.main(["--add", kind.key, "--yes", "--no-reload", "--database", str(path)]),
                                 pi.EXIT_OK)
            self.assertIn("Nothing to change", out.getvalue())

    def test_comment_changed_after_planning_is_kept(self):
        kind = pi.KINDS[0]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "gravity.db"
            with closing(sqlite3.connect(path)) as db, db:
                db.execute("CREATE TABLE domainlist (id INTEGER PRIMARY KEY, type INTEGER, domain TEXT, "
                           "enabled INTEGER, comment TEXT, date_added INTEGER, date_modified INTEGER)")
                db.execute("INSERT INTO domainlist (id, type, domain, enabled, comment) VALUES (1, ?, ?, 1, ?)",
                           (kind.type, "old.example.com", f"{kind.tag} - Misc"))
            row = pi.Row(1, kind.type, "old.example.com", True, f"{kind.tag} - Misc", 0)
            plan = pi.Plan({}, {}, {kind.type: [(row, pi.SourceEntry("old.example.com", "Corrected note"))]})
            with closing(sqlite3.connect(path)) as db, db:
                db.execute("UPDATE domainlist SET comment = 'edited in Pi-hole' WHERE id = 1")
            database = pi.PiholeDB(str(path), write=True)
            try:
                self.assertEqual(pi.apply_plan(database, plan), (0, 0, 0))
            finally:
                database.close()
            with closing(sqlite3.connect(path)) as db:
                self.assertEqual(db.execute("SELECT comment FROM domainlist").fetchone()[0], "edited in Pi-hole")

    def test_removal_skips_entry_edited_after_planning(self):
        kind = pi.KINDS[0]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "gravity.db"
            with closing(sqlite3.connect(path)) as db, db:
                db.execute("CREATE TABLE domainlist (id INTEGER PRIMARY KEY, type INTEGER, domain TEXT, "
                           "enabled INTEGER, comment TEXT, date_added INTEGER, date_modified INTEGER)")
                db.executemany("INSERT INTO domainlist (id, type, domain, enabled, comment) VALUES (?, ?, ?, 1, ?)",
                               [(1, kind.type, "kept.example.com", f"{kind.tag} - Old"),
                                (2, kind.type, "gone.example.com", f"{kind.tag} - Old")])
            rows = [pi.Row(1, kind.type, "kept.example.com", True, f"{kind.tag} - Old", 0),
                    pi.Row(2, kind.type, "gone.example.com", True, f"{kind.tag} - Old", 0)]
            plan = pi.Plan({}, {kind.type: rows})
            with closing(sqlite3.connect(path)) as db, db:
                db.execute("UPDATE domainlist SET comment = 'my own note' WHERE id = 1")
            database = pi.PiholeDB(str(path), write=True)
            try:
                self.assertEqual(pi.apply_plan(database, plan), (0, 1, 0))
            finally:
                database.close()
            with closing(sqlite3.connect(path)) as db:
                self.assertEqual(db.execute("SELECT domain, comment FROM domainlist").fetchall(),
                                 [("kept.example.com", "my own note")])


if __name__ == "__main__":
    unittest.main()
