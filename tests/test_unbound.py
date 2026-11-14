"""Exercise unbound.py's install, undo and remove paths against a fake system.

Nothing here touches apt, dpkg, systemd, Pi-hole or the network: FakeSystem keeps
packages, services and Pi-hole's upstream list in memory and files in a temporary
directory.
"""

import io
import itertools
import json
import os
import signal
import struct
import sys
import tempfile
import time
import unittest
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from unittest.mock import patch

from scripts import unbound as ub

DEBIAN = 'PRETTY_NAME="Debian GNU/Linux 13 (trixie)"\nNAME="Debian GNU/Linux"\nID=debian\n'
RESOLVCONF = "# openresolv\nresolv_conf=/etc/resolv.conf\nunbound_conf=/etc/unbound/unbound.conf.d/resolvconf_resolvers.conf\n"
OLD = ["8.8.8.8", "8.8.4.4"]


PUBLIC = "162.244.93.14"


def a_record(address=PUBLIC):
    return ub.Record(ub.TYPE_A, bytes(int(p) for p in address.split(".")))


class FakeSystem(ub.System):
    def __init__(self, root, os_release=DEBIAN):
        super().__init__(root)
        self.commands = []
        self.packages = {}                      # name -> dpkg status abbreviation
        self.units = {"pihole-FTL": [True, True]}   # unit -> [enabled, active]
        self.upstreams = list(OLD)
        self.working = {"8.8.8.8", "8.8.4.4", "9.9.9.9", "149.112.112.112"}
        self.tools = {"apt-get", "dpkg-query", "systemctl", "pihole-FTL"}
        self.busy_ports = set()
        self.intercepted = False
        self.dnssec_broken = False
        self.dpkg_fatal = False
        self.apt_install_code = 0
        self.cancel_during = None               # "install" raises Cancelled inside apt
        self.refuse_upstreams = None            # a list pihole-FTL refuses to set
        self.fail_systemctl = set()             # actions that fail, such as "stop"
        self.purge_extra = []
        self.installs = []
        self.deps = ["libfoo"]                  # pulled in by apt along with unbound
        self.sneak_in = []                      # installed by someone else just before apt runs
        self.sysctl_fails = False
        self.block_off_unbound = None           # address Pi-hole returns locally when not on unbound
        self.unbound_servfail = False
        self.local = ["192.168.1.50"]
        self.query_logging = True
        self.write("/etc/os-release", os_release)
        self.path("/run/systemd/system").mkdir(parents=True)
        self.write(ub.RMEM_PROC, "212992\n")

    # helpers ---------------------------------------------------------------
    def write(self, name, text):
        path = self.path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def unbound_running(self):
        return self.units.get("unbound.service", [False, False])[1]

    def mutations(self):
        """Commands that change the system (cache flushes and reads are left out)."""
        return [c for c in self.commands
                if (c[0] in ("apt-get", "sysctl") and "-s" not in c)
                or c[:2] == ["dpkg", "--purge"]
                or (c[:2] == ["pihole-FTL", "--config"] and len(c) == 4)
                or (c[0] == "systemctl" and c[1] in ("enable", "disable", "restart", "start", "stop"))]

    # System overrides --------------------------------------------------------
    def which(self, name):
        return name in self.tools

    def is_root(self):
        return True

    def sleep(self, seconds):
        del seconds

    def resolves(self, name):
        del name
        return True

    def can_bind(self, port, *, tcp):
        if port == ub.PORT and self.unbound_running():
            return False
        return (port, "tcp" if tcp else "udp") not in self.busy_ports

    def run(self, cmd, *, env=None):
        del env
        self.commands.append(list(cmd))
        tool = cmd[0]
        if tool == "pihole-FTL":
            return self.ftl(cmd[1:])
        if tool.endswith("pihole") and cmd[1:] == ["reloaddns"]:
            return ub.Result(0)
        if cmd == ["dpkg", "--print-architecture"]:
            return ub.Result(0, "amd64\n")
        if cmd[:2] == ["ip", "-j"]:
            return ub.Result(0, json.dumps([{"addr_info": [{"local": a} for a in self.local]}]))
        if tool == "dpkg-query":
            return self.dpkg_query(cmd)
        if tool == "apt-get" and "-s" in cmd:
            return self.apt_simulate(cmd)
        if tool == "systemctl":
            return self.systemctl(cmd[1:])
        if tool == "unbound-checkconf":
            return ub.Result(0, "unbound-checkconf: no errors")
        if tool == "sysctl":
            if self.sysctl_fails:
                return ub.Result(255, "", "sysctl: permission denied on key net.core.rmem_max")
            self.write(ub.RMEM_PROC, cmd[-1].split("=", 1)[1] + "\n")
            return ub.Result(0, cmd[-1])
        return ub.Result(127, "", f"{tool}: not faked")

    def dpkg_query(self, cmd):
        if self.dpkg_fatal:
            return ub.Result(2, "", "dpkg-query: error: database is locked")
        fmt = next(c for c in cmd if c.startswith("-f="))
        names = [c for c in cmd[2:] if not c.startswith("-")]
        if "Version" in fmt:
            return ub.Result(0, "1.24.2-1" if names[0] in self.packages else "")
        lines = [f"{n}\t{self.packages[n]} " for n in names if n in self.packages]
        return ub.Result(0 if len(lines) == len(names) else 1, "".join(line + "\n" for line in lines))

    def apt_simulate(self, cmd):
        action = "install" if "install" in cmd else "purge"
        names = cmd[cmd.index(action) + 1:]
        if action == "install":
            wanted = [n for n in names + self.deps if n not in self.packages]
            return ub.Result(0, "".join(f"Inst {n} (1.0 Debian:13 [all])\n" for n in wanted))
        return ub.Result(0, "".join(f"Purg {n} [1.0]\n" for n in names + self.purge_extra))

    def ftl(self, args):
        if args == ["--version"]:
            return ub.Result(0, "v6.9\n")
        if args == ["--config", "dns.upstreams"]:
            return ub.Result(0, "[ " + ", ".join(self.upstreams) + " ]\n" if self.upstreams else "[]\n")
        if args == ["--config", "dns.queryLogging"]:
            return ub.Result(0, "true\n" if self.query_logging else "false\n")
        if args == ["--config", "files.log.dnsmasq"]:
            return ub.Result(0, ub.DEFAULT_PIHOLE_LOG + "\n")
        if args[:2] == ["--config", "dns.upstreams"]:
            value = json.loads(args[2])
            if value == self.refuse_upstreams:
                return ub.Result(1, "", "refused")
            self.upstreams = value
            return ub.Result(0, args[2])
        return ub.Result(1, "", "unknown")

    def systemctl(self, args):
        action, unit = args[0], args[-1]
        if action == "list-unit-files":
            return ub.Result(0, f"{unit} enabled enabled\n" if unit in self.units else "")
        state = self.units.get(unit)
        if action == "is-enabled":
            return ub.Result(0 if state and state[0] else 1)
        if action == "is-active":
            return ub.Result(0 if state and state[1] else 3)
        if action in self.fail_systemctl:
            return ub.Result(1, "", f"Failed to {action} {unit}.")
        if state is None:
            return ub.Result(5, "", f"Unit {unit} not found.")
        if action == "enable":
            state[0] = True
        elif action == "disable":
            state[0] = False
            if "--now" in args:
                state[1] = False
        elif action in ("restart", "start"):
            state[1] = True
        elif action == "stop":
            state[1] = False
        return ub.Result(0)

    def run_protected(self, cmd, *, env=None):
        del env
        self.commands.append(list(cmd))
        if "update" in cmd:
            return ub.Result(0)
        if cmd[:2] == ["dpkg", "--purge"]:
            for name in cmd[2:]:
                self.packages.pop(name, None)
            if "unbound" in cmd[2:]:
                self.units.pop("unbound.service", None)
                self.units.pop(ub.RESOLVCONF_SERVICE, None)
            return ub.Result(0)
        if "install" in cmd:
            for name in self.sneak_in:
                self.packages[name] = "ii"
            names = [c for c in cmd if c in ub.PACKAGES]
            self.installs.append(names)
            new = [n for n in names + self.deps if n not in self.packages]
            for name in new:
                self.packages[name] = "ii"
            self.units["unbound.service"] = [True, True]
            self.units[ub.RESOLVCONF_SERVICE] = [True, True]
            self.write(ub.RESOLVCONF_SNIPPET, "forward-zone:\n")
            if self.cancel_during == "install":
                # Ctrl+C while apt runs: the real handler only marks it pending.
                ub._HOLD["pending"] = True
            history = self.path(ub.APT_HISTORY)
            history.parent.mkdir(parents=True, exist_ok=True)
            with history.open("a", encoding="utf-8") as handle:
                handle.write(f"\nStart-Date: {time.strftime('%Y-%m-%d  %H:%M:%S')}\nCommandline: {' '.join(cmd)}\n"
                             "Install: " + ", ".join(f"{n}:amd64 (1.0, automatic)" for n in new) + "\n"
                             f"End-Date: {time.strftime('%Y-%m-%d  %H:%M:%S')}\n")
            out = "The following NEW packages will be installed:\n  " + " ".join(new) + "\n0 upgraded\n"
            return ub.Result(self.apt_install_code, out)
        return ub.Result(1)

    def ask(self, server, name, qtype, *, port=53, qclass=ub.CLASS_IN, recursion=True, ad=False,
            tcp=False, timeout=3.0, tries=2):
        del recursion, tcp, timeout, tries
        if server == ub.ROOT_V4:
            if qclass == ub.CLASS_CH:
                text = b"ISP-PROXY" if self.intercepted else b"ATLAS"
                return ub.Reply(0, ub.FLAG_QR | ub.FLAG_AA, [ub.Record(ub.TYPE_TXT, bytes([len(text)]) + text)])
            flags = ub.FLAG_QR | (ub.FLAG_RA if self.intercepted else ub.FLAG_AA)
            return ub.Reply(0, flags, [ub.Record(ub.TYPE_NS, b"\x01a\x00")])
        if server == ub.ROOT_V6:
            raise ub.DNSError("network unreachable")
        if server == "127.0.0.1" and port == ub.PORT:
            return self.unbound_answer(name, ad)
        if server == "127.0.0.1" and port == 53:
            return self.pihole_answer(name)
        if server in self.working:
            return ub.Reply(0, ub.FLAG_QR | ub.FLAG_RA, [a_record()])
        raise ub.DNSError("timed out")

    def unbound_answer(self, name, ad):
        if not self.unbound_running():
            raise ub.DNSError("connection refused")
        if self.unbound_servfail:
            return ub.Reply(ub.RCODE_SERVFAIL, ub.FLAG_QR | ub.FLAG_RA)
        if name == "fail01.dnssec.works":
            if self.dnssec_broken:
                return ub.Reply(0, ub.FLAG_QR | ub.FLAG_RA, [a_record()])
            return ub.Reply(ub.RCODE_SERVFAIL, ub.FLAG_QR | ub.FLAG_RA)
        flags = ub.FLAG_QR | ub.FLAG_RA | (ub.FLAG_AD if ad and not self.dnssec_broken else 0)
        return ub.Reply(0, flags, [a_record()])

    def pihole_answer(self, name):
        if self.block_off_unbound and not any(ub.points_at_unbound(u) for u in self.upstreams):
            return ub.Reply(0, ub.FLAG_QR | ub.FLAG_RA, [a_record(self.block_off_unbound)])
        for upstream in self.upstreams:
            if ub.points_at_unbound(upstream):
                ok = self.unbound_running()
            else:
                ok = ub.split_upstream(upstream)[0] in self.working
            if ok:
                if self.query_logging:
                    log = self.path(ub.DEFAULT_PIHOLE_LOG)
                    log.parent.mkdir(parents=True, exist_ok=True)
                    with log.open("a", encoding="utf-8") as handle:
                        handle.write(f"Nov 14 dnsmasq[1]: forwarded {name} to {upstream}\n")
                return ub.Reply(0, ub.FLAG_QR | ub.FLAG_RA, [a_record()])
        raise ub.DNSError("timed out")


class Base(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.sys = FakeSystem(temp.name)
        self.sys.write(ub.RESOLVCONF_CONF, RESOLVCONF)
        clock = itertools.count(step=5.0)
        stack = ExitStack()
        self.addCleanup(stack.close)
        # A fake clock so the "wait until Pi-hole forwards" loops end at once in failing cases.
        stack.enter_context(patch.object(ub.time, "monotonic", side_effect=lambda: next(clock)))
        self.out = io.StringIO()
        self.err = io.StringIO()

    def cli(self, *argv):
        with redirect_stdout(self.out), redirect_stderr(self.err):
            return ub.cli([*argv, "--no-color"], self.sys)

    def state(self):
        path = self.sys.path(ub.STATE_FILE)
        return json.loads(path.read_text()) if path.exists() else None

    def install(self):
        self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_OK, self.err.getvalue())

    def purged(self):
        return [c for c in self.sys.commands if c[:2] == ["dpkg", "--purge"]]


class OSCheckTests(Base):
    def check(self, release, expected):
        self.sys.write("/etc/os-release", release)
        self.assertEqual(self.cli("--status"), expected, self.err.getvalue())

    def test_debian_family_passes(self):
        for release in (DEBIAN, "ID=ubuntu\nID_LIKE=debian\n", 'ID=raspbian\nID_LIKE="debian"\n',
                        'ID=linuxmint\nID_LIKE="ubuntu debian"\n'):
            with self.subTest(release=release):
                self.check(release, ub.EXIT_OK)

    def test_other_systems_exit_1_and_run_nothing(self):
        for release in ('ID=fedora\nID_LIKE="rhel centos fedora"\nPRETTY_NAME="Fedora Linux 43"\n',
                        "ID=alpine\n", "ID=arch\n", "ID=foo\nID_LIKE=notdebian\n"):
            with self.subTest(release=release):
                self.sys.commands.clear()
                self.check(release, ub.EXIT_ERROR)
                self.assertEqual(self.sys.commands, [])
                self.assertIn("only Debian-based", self.err.getvalue())

    def test_missing_os_release_exits_1(self):
        self.sys.path("/etc/os-release").unlink()
        self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
        self.assertEqual(self.sys.commands, [])

    def test_missing_apt_exits_1(self):
        self.sys.tools.discard("apt-get")
        self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_ERROR)
        self.assertEqual(self.sys.commands, [])

    def test_os_check_comes_before_option_checks(self):
        self.sys.write("/etc/os-release", "ID=alpine\n")
        self.assertEqual(self.cli("--remove", "--upstream", "nonsense"), ub.EXIT_ERROR)
        self.assertIn("only Debian-based", self.err.getvalue())

    def test_no_systemd_or_pihole_exits_1(self):
        self.sys.path("/run/systemd/system").rmdir()
        self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
        self.assertIn("systemd", self.err.getvalue())
        self.sys.path("/run/systemd/system").mkdir()
        self.sys.tools.discard("pihole-FTL")
        self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
        self.assertEqual(self.sys.mutations(), [])


class DNSMessageTests(unittest.TestCase):
    def reply(self, qid=7, name="pi-hole.net", flags=0x8180, answers=b"", ancount=1, question=None, qtype=1):
        question = question if question is not None else ub.encode_name(name) + struct.pack(">HH", qtype, 1)
        return struct.pack(">HHHHHH", qid, flags, 1, ancount, 0, 0) + question + answers

    def test_query_layout(self):
        packet = ub.build_query(0x1234, "dnssec.works", ub.TYPE_A, recursion=True, ad=True)
        qid, flags, qd = struct.unpack(">HHH", packet[:6])
        self.assertEqual((qid, qd), (0x1234, 1))
        self.assertTrue(flags & ub.FLAG_RD and flags & ub.FLAG_AD)
        self.assertEqual(packet[12:], b"\x06dnssec\x05works\x00\x00\x01\x00\x01")
        self.assertEqual(ub.build_query(1, ".", ub.TYPE_NS, recursion=False)[12:], b"\x00\x00\x02\x00\x01")

    def test_parses_compressed_answer(self):
        answer = b"\xc0\x0c" + struct.pack(">HHIH", 1, 1, 60, 4) + bytes([203, 0, 113, 7])
        reply = ub.parse_reply(self.reply(answers=answer), 7, "pi-hole.net", 1, 1)
        self.assertEqual(reply.addresses(), ["203.0.113.7"])
        self.assertTrue(reply.flag(ub.FLAG_RA))

    def test_follows_cname_and_ignores_unrelated_records(self):
        cname = b"\xc0\x0c" + struct.pack(">HHIH", 5, 1, 60, 6) + b"\x03cdn\xc0\x0c"   # pi-hole.net -> cdn.pi-hole.net
        target = b"\xc0\x29" + struct.pack(">HHIH", 1, 1, 60, 4) + bytes([198, 51, 100, 1])
        stray = ub.encode_name("other.example") + struct.pack(">HHIH", 1, 1, 60, 4) + bytes([192, 0, 2, 9])
        chaos = b"\xc0\x0c" + struct.pack(">HHIH", 1, 3, 60, 4) + bytes([192, 0, 2, 10])
        data = self.reply(answers=cname + target + stray + chaos, ancount=4)
        reply = ub.parse_reply(data, 7, "pi-hole.net", 1, 1)
        self.assertEqual(reply.addresses(), ["198.51.100.1"])

    def test_chaos_cname_does_not_extend_the_chain(self):
        cname = b"\xc0\x0c" + struct.pack(">HHIH", 5, 3, 60, 6) + b"\x03cdn\xc0\x0c"
        target = b"\xc0\x29" + struct.pack(">HHIH", 1, 1, 60, 4) + bytes([198, 51, 100, 1])
        reply = ub.parse_reply(self.reply(answers=cname + target, ancount=2), 7, "pi-hole.net", 1, 1)
        self.assertEqual(reply.addresses(), [])

    def test_txt_and_chaos(self):
        text = b"\x05ATLAS"
        answer = b"\xc0\x0c" + struct.pack(">HHIH", 16, 3, 0, len(text)) + text
        question = ub.encode_name("version.bind") + struct.pack(">HH", 16, 3)
        reply = ub.parse_reply(self.reply(answers=answer, question=question), 7, "version.bind", 16, 3)
        self.assertEqual(reply.texts(), ["ATLAS"])

    def test_truncated_reply_handling(self):
        data = self.reply(flags=0x8380, answers=b"\xc0\x0c\x00", ancount=1)   # TC set, answer cut off
        reply = ub.parse_reply(data, 7, "pi-hole.net", 1, 1, allow_truncated=True)
        self.assertTrue(reply.flag(ub.FLAG_TC))
        self.assertEqual(reply.answers, [])
        with self.assertRaises(ub.DNSError):
            ub.parse_reply(data, 7, "pi-hole.net", 1, 1)

    def test_rejects_bad_replies(self):
        good = b"\xc0\x0c" + struct.pack(">HHIH", 1, 1, 60, 4) + bytes(4)
        short_a = b"\xc0\x0c" + struct.pack(">HHIH", 1, 1, 60, 1) + b"\x7f"
        txt_overrun = b"\xc0\x0c" + struct.pack(">HHIH", 16, 1, 0, 3) + b"\x09ab"
        txt_question = ub.encode_name("pi-hole.net") + struct.pack(">HH", 16, 1)
        cases = {
            "wrong id": (self.reply(qid=8, answers=good), "pi-hole.net", 1),
            "not a reply": (self.reply(flags=0x0100, answers=good), "pi-hole.net", 1),
            "other opcode": (self.reply(flags=0x8980, answers=good), "pi-hole.net", 1),
            "other question": (self.reply(answers=good), "example.com", 1),
            "truncated header": (b"\x00\x07\x81", "pi-hole.net", 1),
            "truncated record": (self.reply(answers=good[:-2]), "pi-hole.net", 1),
            "pointer loop": (self.reply(answers=b"\xc0\x1d" + good[2:]), "pi-hole.net", 1),
            "self pointer": (self.reply(question=b"\xc0\x0c" + struct.pack(">HH", 1, 1)), "pi-hole.net", 1),
            "short A record": (self.reply(answers=short_a), "pi-hole.net", 1),
            "TXT overrun": (self.reply(answers=txt_overrun, question=txt_question), "pi-hole.net", 16),
            "empty CNAME": (self.reply(answers=b"\xc0\x0c" + struct.pack(">HHIH", 5, 1, 60, 0) + good, ancount=2),
                            "pi-hole.net", 1),
        }
        for label, (data, name, qtype) in cases.items():
            with self.subTest(label), self.assertRaises(ub.DNSError):
                ub.parse_reply(data, 7, name, qtype, 1)

    def test_recv_exact_handles_short_reads_and_close(self):
        class Sock:
            def __init__(self, chunks):
                self.chunks = list(chunks)

            def recv(self, size):
                return self.chunks.pop(0)[:size] if self.chunks else b""

        self.assertEqual(ub.recv_exact(Sock([b"ab", b"c", b"de"]), 5), b"abcde")
        with self.assertRaises(ub.DNSError):
            ub.recv_exact(Sock([b"ab"]), 5)


class ParsingTests(unittest.TestCase):
    def test_pihole_upstream_output(self):
        self.assertEqual(ub.parse_upstreams("[ 127.0.0.1#5335 ]\n"), ["127.0.0.1#5335"])
        self.assertEqual(ub.parse_upstreams("[ 8.8.8.8, 8.8.4.4 ]"), ["8.8.8.8", "8.8.4.4"])
        self.assertEqual(ub.parse_upstreams("[]"), [])
        self.assertEqual(ub.parse_upstreams('[ "9.9.9.9" ]'), ["9.9.9.9"])
        with self.assertRaises(ub.AppError):
            ub.parse_upstreams("error: unknown key")

    def test_unbound_references_in_every_spelling(self):
        for item in ("127.0.0.1#5335", "localhost#5335", "LOCALHOST#5335", "::1#5335", "127.0.1.1#5335",
                     "[::1]#5335", "0.0.0.0#5335"):
            with self.subTest(item=item):
                self.assertTrue(ub.points_at_unbound(item))
        for item in ("127.0.0.1#5053", "9.9.9.9", "192.168.1.2#5335"):
            with self.subTest(item=item):
                self.assertFalse(ub.points_at_unbound(item))

    def test_only_public_addresses_count_as_answers(self):
        for address in ("0.0.0.0", "::", "127.0.0.1", "192.168.1.50", "10.0.0.2", "fe80::1", "not-an-ip"):
            with self.subTest(address=address):
                self.assertFalse(ub.usable(address))
        for address in ("162.244.93.14", "2606:4700::6810:84e5"):
            with self.subTest(address=address):
                self.assertTrue(ub.usable(address))

    def test_upstream_option(self):
        self.assertEqual(ub.parse_upstream_option("9.9.9.9, 149.112.112.112"), ["9.9.9.9", "149.112.112.112"])
        self.assertEqual(ub.parse_upstream_option("127.0.0.1#5053 2620:fe::fe"), ["127.0.0.1#5053", "2620:fe::fe"])
        for bad in ("dns.quad9.net", "9.9.9.9#0", "9.9.9.9#70000", "127.0.0.1#5335", "127.0.0.1",
                    "::1#53", "0.0.0.0", "localhost#5335", ""):
            with self.subTest(bad=bad), self.assertRaises(ub.AppError):
                ub.parse_upstream_option(bad)

    def test_config(self):
        on, off = ub.render_config(True), ub.render_config(False)
        self.assertIn("do-ip6: yes", on)
        self.assertIn("do-ip6: no", off)
        for text in (on, off):
            self.assertTrue(text.startswith(ub.MARKER))
            self.assertIn("port: 5335", text)
            self.assertIn('root-hints: "/usr/share/dns/root.hints"', text)
            self.assertIn("so-rcvbuf: 1m", text)

    def test_sysctl_edit_keeps_other_settings(self):
        self.assertEqual(ub.set_sysctl_line("", 1048576), "net.core.rmem_max=1048576\n")
        self.assertEqual(ub.set_sysctl_line("vm.swappiness=10", 1048576),
                         "vm.swappiness=10\nnet.core.rmem_max=1048576\n")
        self.assertEqual(ub.set_sysctl_line("a=1\n net.core.rmem_max = 5\nb=2\n", 1048576),
                         "a=1\nnet.core.rmem_max=1048576\nb=2\n")

    def test_apt_history(self):
        cmd = "apt-get -o DPkg::Lock::Timeout=300 install -y --no-remove -o Dpkg::Options::=--force-confold unbound"
        text = ("Start-Date: 2026-11-14  01:00:11\nCommandline: apt-get dist-upgrade\nInstall: other:amd64 (1)\n\n"
                f"Start-Date: 2026-11-14  07:02:20\nCommandline: {cmd}\n"
                "Install: unbound:amd64 (1.26.2-0+deb13u1), libfoo:amd64 (2.1, automatic)\nEnd-Date: x\n")
        since = time.mktime(time.strptime("2026-11-14  07:02:00", "%Y-%m-%d  %H:%M:%S"))
        self.assertEqual(ub.history_installs(text, cmd, since), ["unbound:amd64", "libfoo:amd64"])
        self.assertIsNone(ub.history_installs(text, cmd, since + 3600))
        self.assertIsNone(ub.history_installs(text, cmd + " extra", since))

    def test_apt_simulation(self):
        text = ("NOTE: This is only a simulation!\nInst libfoo [1.0] (1.1 Debian:13 [amd64])\n"
                "Inst unbound (1.24 Debian:13 [amd64])\nConf unbound (1.24 Debian:13 [amd64])\n"
                "Remv oldpkg [2.0]\nPurg other [3.0]\n")
        self.assertEqual(ub.parse_apt_simulation(text), (["unbound"], ["libfoo"], ["oldpkg", "other"]))


class PackageTests(Base):
    def test_architecture_is_kept_for_foreign_packages(self):
        box = ub.Box(self.sys)
        self.sys.packages.update({"libfoo:armhf": "ii", "unbound": "rc"})
        self.assertEqual(box.present(["libfoo:armhf", "unbound:amd64", "missing"]), ["libfoo:armhf", "unbound"])
        self.assertFalse(box.installed("unbound"))

    def test_unreadable_dpkg_database_is_an_error(self):
        self.sys.dpkg_fatal = True
        with self.assertRaises(ub.AppError):
            ub.Box(self.sys).present(["unbound"])


class RunProtectedTests(unittest.TestCase):
    def test_child_finishes_when_output_breaks(self):
        class Broken(io.StringIO):
            def write(self, text):
                raise BrokenPipeError("terminal closed")

            def flush(self):
                raise BrokenPipeError("terminal closed")

        cmd = [sys.executable, "-c", "import time\nfor i in range(3): print('line', i, flush=True); time.sleep(0.05)"]
        with patch.object(sys, "stdout", Broken()):
            result = ub.System().run_protected(cmd)
        self.assertEqual(result.code, 0)
        self.assertEqual(result.out.splitlines(), ["line 0", "line 1", "line 2"])


class InterruptTests(unittest.TestCase):
    def test_signal_is_held_then_delivered(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(ub.Cancelled), ub.uninterruptible("testing."):
            os.kill(os.getpid(), signal.SIGTERM)
            with ub.uninterruptible("nested."):
                pass
            ran_after_signal = True
        self.assertTrue(ran_after_signal)

    def test_handlers_are_restored(self):
        before = (signal.getsignal(signal.SIGINT), signal.getsignal(signal.SIGTERM))
        with ub.uninterruptible("testing."), ub.uninterruptible("nested."):
            self.assertIs(signal.getsignal(signal.SIGTERM), ub._hold_signal)
        self.assertEqual((signal.getsignal(signal.SIGINT), signal.getsignal(signal.SIGTERM)), before)

    def test_failure_inside_wins_and_pending_is_cleared(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(ub.AppError), ub.uninterruptible("testing."):
            os.kill(os.getpid(), signal.SIGTERM)
            raise ub.AppError("step failed")
        with ub.uninterruptible("again."):
            pass  # no stale cancel left over from the block above


class InstallTests(Base):
    def test_fresh_install(self):
        self.install()
        self.assertEqual(self.sys.upstreams, [ub.UNBOUND_UPSTREAM])
        self.assertEqual(set(self.sys.packages), {*ub.PACKAGES, "libfoo"})
        state = self.state()
        self.assertEqual(state["status"], "installed")
        self.assertEqual(state["changes"][-1], {"kind": "upstreams", "done": True, "old": OLD})
        self.assertIn("do-ip6: no", self.sys.path(ub.CONF_FILE).read_text())
        self.assertIn("#unbound_conf=", self.sys.path(ub.RESOLVCONF_CONF).read_text())
        self.assertFalse(self.sys.path(ub.RESOLVCONF_SNIPPET).exists())
        self.assertEqual(self.sys.units[ub.RESOLVCONF_SERVICE], [False, False])
        self.assertEqual(self.sys.path(ub.SYSCTL_FILE).read_text(), "net.core.rmem_max=1048576\n")
        self.assertEqual(self.sys.path(ub.RMEM_PROC).read_text().strip(), "1048576")
        self.assertIn("Pi-hole's log shows it forwarding to 127.0.0.1#5335", self.out.getvalue())

    def test_existing_dns_root_data_is_left_alone(self):
        self.sys.packages["dns-root-data"] = "ii"
        self.install()
        self.assertEqual(self.sys.installs, [["unbound"]])
        self.assertEqual(self.sys.packages, {"dns-root-data": "ii", "unbound": "ii", "libfoo": "ii"})
        self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_OK, self.err.getvalue())
        self.assertEqual(self.sys.packages, {"dns-root-data": "ii"})

    def test_nothing_changes_before_the_answer(self):
        with patch.object(ub, "confirm", return_value=False):
            self.assertEqual(self.cli("--install"), ub.EXIT_OK)
        self.assertEqual(self.sys.mutations(), [])
        self.assertIsNone(self.state())

    def test_query_logging_off_still_proves_unbound(self):
        self.sys.query_logging = False
        self.install()
        self.assertIn("query logging is off", self.out.getvalue())

    def test_second_install_reports_installed(self):
        self.install()
        before = list(self.sys.mutations())
        self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_OK)
        self.assertIn("already installed", self.out.getvalue())
        self.assertEqual(self.sys.mutations(), before)

    def test_dry_run_changes_nothing(self):
        self.assertEqual(self.cli("--install", "--dry-run"), ub.EXIT_OK)
        self.assertEqual(self.sys.mutations(), [])
        self.assertIsNone(self.state())
        self.assertFalse(self.sys.path(ub.CONF_FILE).exists())

    def test_refuses_existing_unbound_and_leftovers(self):
        for setup in ("package", "leftover", "etc"):
            with self.subTest(setup=setup):
                self.sys.packages.clear()
                if setup == "package":
                    self.sys.packages["unbound"] = "ii"
                elif setup == "leftover":
                    self.sys.packages["unbound"] = "rc"
                else:
                    self.sys.write("/etc/unbound/unbound.conf", "server:\n")
                self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
                self.assertIn("without this script", self.err.getvalue())
                self.assertEqual(self.sys.mutations(), [])
                self.assertIsNone(self.state())

    def test_refuses_busy_port_udp_or_tcp(self):
        for proto in ("udp", "tcp"):
            with self.subTest(proto=proto):
                self.sys.busy_ports = {(ub.PORT, proto)}
                self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
                self.assertIn(proto.upper(), self.err.getvalue())
                self.assertEqual(self.sys.mutations(), [])

    def test_intercepted_root_servers_stop_before_changes(self):
        self.sys.intercepted = True
        self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
        self.assertIn("root server", self.err.getvalue())
        self.assertEqual(self.sys.mutations(), [])
        self.assertIsNone(self.state())

    def test_pihole_not_resolving_stops_before_changes(self):
        self.sys.working.clear()
        self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
        self.assertEqual(self.sys.mutations(), [])

    def test_failed_dnssec_check_undoes_everything(self):
        self.sys.dnssec_broken = True
        self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
        self.assert_back_to_start()

    def test_failed_apt_install_undoes_everything(self):
        self.sys.apt_install_code = 100
        self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
        self.assert_back_to_start()

    def test_failed_enable_undoes_everything(self):
        self.sys.fail_systemctl = {"enable"}
        self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
        self.assertIn("systemctl enable", self.err.getvalue())
        self.assert_back_to_start()

    def test_cancel_during_apt_undoes_everything(self):
        self.sys.cancel_during = "install"
        self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_CANCELLED)
        self.assert_back_to_start()

    def test_cancel_after_pihole_switch_restores_upstreams(self):
        real = ub.Box.check_forwarding
        calls = []

        def cancel_first(box, expected, **kwargs):
            calls.append(expected)
            if len(calls) == 1:
                raise ub.Cancelled()
            return real(box, expected, **kwargs)

        with patch.object(ub.Box, "check_forwarding", cancel_first):
            self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_CANCELLED)
        self.assertEqual(calls[1], OLD)
        self.assert_back_to_start()

    def test_old_servers_dead_at_rollback_keeps_unbound(self):
        real = ub.Box.check_forwarding

        def fail_then_kill_old(box, expected, **kwargs):
            if expected == [ub.UNBOUND_UPSTREAM]:
                self.sys.working.clear()   # the old servers stop answering
                raise ub.AppError("forwarding not seen")
            return real(box, expected, **kwargs)

        with patch.object(ub.Box, "check_forwarding", fail_then_kill_old):
            self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
        self.assertEqual(self.sys.upstreams, [ub.UNBOUND_UPSTREAM])
        self.assertTrue(self.sys.unbound_running())
        self.assertIn("unbound", self.sys.packages)
        self.assertTrue(self.sys.path(ub.CONF_FILE).exists())
        self.assertEqual(self.state()["status"], "incomplete")
        self.assertEqual(self.purged(), [])

    def test_refused_upstream_restore_keeps_unbound(self):
        self.sys.refuse_upstreams = OLD
        with patch.object(ub.Box, "check_forwarding", side_effect=ub.AppError("forwarding not seen")):
            self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
        self.assertEqual(self.sys.upstreams, [ub.UNBOUND_UPSTREAM])
        self.assertTrue(self.sys.unbound_running())
        self.assertEqual(self.state()["status"], "incomplete")
        self.assertIn("--remove", self.err.getvalue())

    def test_purge_that_would_remove_more_is_refused_before_anything(self):
        self.sys.dnssec_broken = True
        self.sys.purge_extra = ["someones-app"]
        self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
        self.assertIn("someones-app", self.err.getvalue())
        self.assertIn("unbound", self.sys.packages)
        self.assertTrue(self.sys.path(ub.CONF_FILE).exists())
        self.assertEqual(self.state()["status"], "incomplete")
        self.assertEqual(self.purged(), [])

    def test_incomplete_state_blocks_install(self):
        ub.State(self.sys, {"version": 1, "status": "incomplete", "changes": []}).save()
        self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
        self.assertIn("--remove", self.err.getvalue())

    def test_invalid_state_changes_nothing(self):
        self.sys.write(ub.SYSCTL_FILE, "vm.swappiness=10\n")
        def record(*changes, version=1):
            return json.dumps({"version": version, "status": "installed", "changes": list(changes)})

        upstreams = {"kind": "upstreams", "done": True, "old": []}
        bad = ("{not json",
               json.dumps({"changes": [{"kind": "sysctl"}]}),
               record({"kind": "sysctl", "done": True}),
               record({"kind": "packages", "done": True, "owned": ["unbound; rm -rf /"]}),
               record(version=2),
               record(upstreams, upstreams),
               # The backup it names was never written, whether or not the change finished.
               record({"kind": "sysctl", "done": True, "old_value": 1, "skipped": False,
                       "backup": "/var/lib/pihole-unbound/backup/99-unbound.conf"}),
               record({"kind": "sysctl", "done": False, "old_value": 1, "skipped": False,
                       "backup": "/var/lib/pihole-unbound/backup/99-unbound.conf"}),
               record({"kind": "packages", "done": True, "owned": ["unbound"]}))
        for text in bad:
            with self.subTest(text=text):
                self.sys.write(ub.STATE_FILE, text)
                self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
                self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_ERROR)
                self.assertEqual(self.sys.mutations(), [])
                self.assertEqual(self.sys.path(ub.SYSCTL_FILE).read_text(), "vm.swappiness=10\n")

    def test_concurrent_run_is_refused(self):
        lock = ub.System(str(self.sys.root))
        with lock.lock():
            self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
        self.assertIn("in progress", self.err.getvalue())
        self.assertEqual(self.sys.mutations(), [])

    def test_package_installed_by_someone_else_is_not_owned(self):
        self.sys.sneak_in = ["libfoo"]
        self.install()
        self.assertEqual(self.state()["changes"][1]["owned"], ["unbound", "dns-root-data"])
        self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_OK, self.err.getvalue())
        self.assertEqual(self.sys.packages, {"libfoo": "ii"})

    def test_cancel_during_apt_keeps_apts_own_list(self):
        self.sys.sneak_in = ["libfoo"]
        self.sys.cancel_during = "install"
        self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_CANCELLED)
        self.assertEqual(self.sys.packages, {"libfoo": "ii"})
        self.assertIsNone(self.state())

    def crashed_after_apt(self, history):
        """A record as left by a power loss after apt finished but before its list was saved."""
        command = ("apt-get -o DPkg::Lock::Timeout=300 -o PiholeUnbound::Run=0123456789abcdef install -y "
                   "--no-remove -o Dpkg::Options::=--force-confold unbound")
        self.sys.packages.update({"unbound": "ii", "libfoo": "ii", "dns-root-data": "ii"})
        if history:
            logged = command if history is True else history
            self.sys.write(ub.APT_HISTORY, f"Start-Date: {time.strftime('%Y-%m-%d  %H:%M:%S')}\n"
                                           f"Commandline: {logged}\n"
                                           "Install: unbound:amd64 (1.0), libfoo:amd64 (1.0, automatic)\n")
        state = ub.State.new(self.sys)
        state.data["changes"] = [{"kind": "packages", "done": False, "planned": ["libfoo", "unbound"],
                                  "preexisting": [], "owned": [], "command": command}]
        state.save()

    def test_unsaved_apt_list_uses_apts_history(self):
        self.crashed_after_apt(history=True)
        self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_OK, self.err.getvalue())
        self.assertEqual(self.sys.packages, {"dns-root-data": "ii"})

    def test_same_command_from_another_run_is_not_ours(self):
        # The same apt command typed by someone else carries no marker, or a different one.
        tail = "install -y --no-remove -o Dpkg::Options::=--force-confold unbound"
        for other in (f"apt-get -o DPkg::Lock::Timeout=300 {tail}",
                      f"apt-get -o DPkg::Lock::Timeout=300 -o PiholeUnbound::Run=ffffffffffffffff {tail}"):
            with self.subTest(other=other):
                self.sys.commands.clear()
                self.sys.path(ub.STATE_FILE).unlink(missing_ok=True)
                self.crashed_after_apt(history=other)
                self.cli("--remove", "--yes")
                self.assertIn("unbound", self.sys.packages)
                self.assertEqual(self.purged(), [])

    def test_unsaved_apt_list_without_history_claims_nothing(self):
        # unbound could have been installed by another program in that moment, so it stays.
        self.crashed_after_apt(history=False)
        self.cli("--remove", "--yes")
        self.assertEqual(self.sys.packages, {"unbound": "ii", "libfoo": "ii", "dns-root-data": "ii"})
        self.assertIn("so they stay", self.err.getvalue())
        self.assertEqual(self.purged(), [])

    def test_unwritable_sysctl_is_skipped_and_removal_still_finishes(self):
        self.sys.sysctl_fails = True
        self.install()
        self.assertFalse(self.sys.path(ub.SYSCTL_FILE).exists())
        self.assertTrue(self.state()["changes"][3]["skipped"])
        self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_OK, self.err.getvalue())
        self.assertIsNone(self.state())

    def test_blocked_answer_at_rollback_keeps_unbound(self):
        real = ub.Box.check_forwarding

        def fail_then_block(box, expected, **kwargs):
            if expected == [ub.UNBOUND_UPSTREAM]:
                self.sys.working.clear()            # the old servers stop answering...
                self.sys.block_off_unbound = "0.0.0.0"   # ...and Pi-hole answers locally instead
                raise ub.AppError("forwarding not seen")
            return real(box, expected, **kwargs)

        with patch.object(ub.Box, "check_forwarding", fail_then_block):
            self.assertEqual(self.cli("--install", "--yes"), ub.EXIT_ERROR)
        self.assertEqual(self.sys.upstreams, [ub.UNBOUND_UPSTREAM])
        self.assertTrue(self.sys.unbound_running())
        self.assertEqual(self.purged(), [])

    def assert_back_to_start(self):
        self.assertEqual(self.sys.upstreams, OLD)
        self.assertEqual(self.sys.packages, {})
        self.assertFalse(self.sys.path(ub.CONF_FILE).exists())
        self.assertFalse(self.sys.path("/etc/unbound").exists())
        self.assertEqual(self.sys.path(ub.RESOLVCONF_CONF).read_text(), RESOLVCONF)
        self.assertFalse(self.sys.path(ub.SYSCTL_FILE).exists())
        self.assertEqual(self.sys.path(ub.RMEM_PROC).read_text().strip(), "212992")
        self.assertIsNone(self.state())
        self.assertFalse(self.sys.path(ub.STATE_DIR).exists())


class RemoveTests(Base):
    def test_remove_restores_everything(self):
        self.sys.write(ub.SYSCTL_FILE, "vm.swappiness=10\n")
        self.install()
        self.assertEqual(self.sys.path(ub.SYSCTL_FILE).read_text(), "vm.swappiness=10\nnet.core.rmem_max=1048576\n")
        self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_OK, self.err.getvalue())
        self.assertEqual(self.sys.upstreams, OLD)
        self.assertEqual(self.sys.packages, {})
        self.assertFalse(self.sys.path(ub.CONF_FILE).exists())
        self.assertFalse(self.sys.path("/etc/unbound").exists())
        self.assertEqual(self.sys.path(ub.RESOLVCONF_CONF).read_text(), RESOLVCONF)
        self.assertEqual(self.sys.path(ub.SYSCTL_FILE).read_text(), "vm.swappiness=10\n")
        self.assertEqual(self.sys.path(ub.RMEM_PROC).read_text().strip(), "212992")
        self.assertFalse(self.sys.path(ub.STATE_DIR).exists())
        self.assertIn("removed completely", self.out.getvalue())

    def test_second_remove_has_nothing_to_do(self):
        self.install()
        self.cli("--remove", "--yes")
        self.sys.commands.clear()
        self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_OK)
        self.assertIn("Nothing to remove", self.out.getvalue())
        self.assertEqual(self.sys.mutations(), [])

    def test_empty_saved_upstreams_need_a_choice(self):
        self.install()
        data = self.state()
        data["changes"][-1]["old"] = []   # Pi-hole had no upstream servers before the install
        ub.State(self.sys, data).save()
        before = list(self.sys.mutations())
        self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_ERROR)
        self.assertIn("--upstream", self.err.getvalue())
        self.assertEqual(self.sys.mutations(), before)
        self.assertEqual(self.cli("--remove", "--yes", "--upstream", "9.9.9.9"), ub.EXIT_OK, self.err.getvalue())
        self.assertEqual(self.sys.upstreams, ["9.9.9.9"])

    def test_self_referencing_upstreams_are_not_choices(self):
        self.sys.upstreams = ["localhost#5335"]
        self.sys.packages["unbound"] = "ii"
        self.sys.units["unbound.service"] = [True, True]
        self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_ERROR)
        self.assertIn("none was saved", self.err.getvalue())
        self.assertEqual(self.sys.mutations(), [])

    def test_failing_new_upstream_keeps_pihole_on_unbound(self):
        self.install()
        self.assertEqual(self.cli("--remove", "--yes", "--upstream", "192.0.2.1"), ub.EXIT_ERROR)
        self.assertEqual(self.sys.upstreams, [ub.UNBOUND_UPSTREAM])
        self.assertTrue(self.sys.unbound_running())
        self.assertIn("unbound", self.sys.packages)
        self.assertEqual(self.state()["status"], "installed")

    def test_upstream_pihole_cannot_use_is_put_back(self):
        self.install()
        real = FakeSystem.pihole_answer

        def only_unbound(fake, name):
            if fake.upstreams == ["203.0.113.9"]:
                raise ub.DNSError("timed out")
            return real(fake, name)

        self.sys.working.add("203.0.113.9")
        with patch.object(FakeSystem, "pihole_answer", only_unbound):
            self.assertEqual(self.cli("--remove", "--yes", "--upstream", "203.0.113.9"), ub.EXIT_ERROR)
        self.assertEqual(self.sys.upstreams, [ub.UNBOUND_UPSTREAM])
        self.assertTrue(self.sys.unbound_running())
        self.assertIn("unbound", self.sys.packages)
        self.assertEqual(self.purged(), [])

    def test_local_answer_is_not_proof(self):
        self.install()
        for logging, address in ((True, "0.0.0.0"), (False, "93.184.216.34")):
            with self.subTest(logging=logging):
                self.sys.query_logging = logging
                self.sys.block_off_unbound = address
                self.assertEqual(self.cli("--remove", "--yes", "--upstream", "9.9.9.9"), ub.EXIT_ERROR)
                self.assertEqual(self.sys.upstreams, [ub.UNBOUND_UPSTREAM])
                self.assertTrue(self.sys.unbound_running())
                self.assertEqual(self.purged(), [])

    def test_host_name_servers_cannot_be_proven_without_logging(self):
        self.install()
        self.sys.upstreams = [ub.UNBOUND_UPSTREAM, "dns.example"]
        self.sys.query_logging = False
        self.sys.block_off_unbound = "93.184.216.34"   # a local record with a public address
        self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_ERROR)
        self.assertIn("no IP address", self.err.getvalue())
        self.assertEqual(self.sys.upstreams, [ub.UNBOUND_UPSTREAM, "dns.example"])
        self.assertTrue(self.sys.unbound_running())
        self.assertEqual(self.purged(), [])

    def test_file_error_during_check_still_puts_pihole_back(self):
        self.install()
        with patch.object(ub.Box, "check_forwarding", side_effect=PermissionError("log not readable")):
            self.assertEqual(self.cli("--remove", "--yes", "--upstream", "9.9.9.9"), ub.EXIT_ERROR)
        self.assertEqual(self.sys.upstreams, [ub.UNBOUND_UPSTREAM])
        self.assertTrue(self.sys.unbound_running())
        self.assertIn("back on 127.0.0.1#5335", self.err.getvalue())

    def test_failed_unbound_start_still_restores_mixed_servers(self):
        self.install()
        self.sys.upstreams = [ub.UNBOUND_UPSTREAM, "149.112.112.112"]
        self.sys.fail_systemctl = {"start"}
        with patch.object(ub.Box, "check_forwarding", side_effect=ub.AppError("not seen")):
            self.assertEqual(self.cli("--remove", "--yes", "--upstream", "9.9.9.9"), ub.EXIT_ERROR)
        self.assertEqual(self.sys.upstreams, [ub.UNBOUND_UPSTREAM, "149.112.112.112"])
        self.assertIn("did not fully work", self.err.getvalue())
        self.assertEqual(self.purged(), [])

    def test_servfail_unbound_is_not_called_working(self):
        self.install()
        self.sys.unbound_servfail = True
        with patch.object(ub.Box, "check_forwarding", side_effect=ub.AppError("not seen")):
            self.assertEqual(self.cli("--remove", "--yes", "--upstream", "9.9.9.9"), ub.EXIT_ERROR)
        self.assertIn("did not fully work", self.err.getvalue())
        self.assertNotIn("nothing was removed", self.err.getvalue())

    def test_half_installed_unbound_without_unit_can_be_removed(self):
        self.install()
        self.sys.upstreams = list(OLD)
        self.sys.units.pop("unbound.service")
        self.sys.packages["unbound"] = "iH"
        self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_OK, self.err.getvalue())
        self.assertNotIn("unbound", self.sys.packages)

    def test_upstream_option_is_honored_for_unrecognized_setups(self):
        self.sys.packages["unbound"] = "ii"
        self.sys.units["unbound.service"] = [True, True]
        self.sys.upstreams = ["192.168.1.2#5335"]
        self.assertEqual(self.cli("--remove", "--yes", "--upstream", "9.9.9.9"), ub.EXIT_OK, self.err.getvalue())
        self.assertEqual(self.sys.upstreams, ["9.9.9.9"])

    def test_this_machines_address_is_rejected(self):
        self.install()
        self.assertEqual(self.cli("--remove", "--yes", "--upstream", "192.168.1.50"), ub.EXIT_ERROR)
        self.assertIn("is this machine", self.err.getvalue())
        self.assertEqual(self.sys.upstreams, [ub.UNBOUND_UPSTREAM])

    def test_failed_stop_removes_nothing(self):
        self.install()
        self.sys.fail_systemctl = {"stop"}
        self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_ERROR)
        self.assertIn("systemctl stop", self.err.getvalue())
        self.assertEqual(self.sys.upstreams, [ub.UNBOUND_UPSTREAM])
        self.assertIn("unbound", self.sys.packages)
        self.assertEqual(self.purged(), [])

    def test_marker_without_state_changes_nothing(self):
        self.install()
        self.sys.path(ub.STATE_FILE).unlink()
        before = list(self.sys.mutations())
        self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_ERROR)
        self.assertIn("record", self.err.getvalue())
        self.assertEqual(self.sys.mutations(), before)

    def test_manual_setup_removal(self):
        self.sys.packages.update({"unbound": "ii", "dns-root-data": "ii"})
        self.sys.units["unbound.service"] = [True, True]
        self.sys.upstreams = ["localhost#5335"]
        self.sys.write(ub.CONF_FILE, "server:\n    port: 5335\n")
        self.sys.write(ub.SYSCTL_FILE, "net.core.rmem_max=1048576\n")
        self.assertEqual(self.cli("--remove", "--yes", "--upstream", "9.9.9.9"), ub.EXIT_OK, self.err.getvalue())
        self.assertEqual(self.sys.upstreams, ["9.9.9.9"])
        self.assertEqual(self.sys.packages, {"dns-root-data": "ii"})
        self.assertFalse(self.sys.path(ub.CONF_FILE).exists())
        # A manual setup's other files are not this script's to change.
        self.assertTrue(self.sys.path(ub.SYSCTL_FILE).exists())
        self.assertEqual(self.sys.path(ub.RESOLVCONF_CONF).read_text(), RESOLVCONF)

    def test_manual_purge_refusal_keeps_config(self):
        self.sys.packages["unbound"] = "ii"
        self.sys.units["unbound.service"] = [True, True]
        self.sys.upstreams = [ub.UNBOUND_UPSTREAM]
        self.sys.write(ub.CONF_FILE, "server:\n    port: 5335\n")
        self.sys.purge_extra = ["someones-app"]
        self.assertEqual(self.cli("--remove", "--yes", "--upstream", "9.9.9.9"), ub.EXIT_ERROR)
        self.assertTrue(self.sys.path(ub.CONF_FILE).exists())
        self.assertEqual(self.sys.mutations(), [])

    def test_mixed_upstreams_keep_the_other_servers(self):
        self.install()
        self.sys.upstreams = [ub.UNBOUND_UPSTREAM, "149.112.112.112"]
        self.assertEqual(self.cli("--remove", "--yes"), ub.EXIT_OK, self.err.getvalue())
        self.assertEqual(self.sys.upstreams, ["149.112.112.112"])

    def test_remove_dry_run_changes_nothing(self):
        self.install()
        before = list(self.sys.mutations())
        self.assertEqual(self.cli("--remove", "--dry-run"), ub.EXIT_OK)
        self.assertEqual(self.sys.mutations(), before)
        self.assertEqual(self.sys.upstreams, [ub.UNBOUND_UPSTREAM])


class StatusTests(Base):
    def test_status_after_install(self):
        self.install()
        self.out.truncate(0)
        self.assertEqual(self.cli("--status"), ub.EXIT_OK, self.err.getvalue())
        text = self.out.getvalue()
        self.assertIn("this script", text)
        self.assertIn("Pi-hole returns an address", text)

    def test_status_when_not_installed(self):
        self.assertEqual(self.cli("--status"), ub.EXIT_OK)
        self.assertIn("not installed", self.out.getvalue())


if __name__ == "__main__":
    unittest.main()
