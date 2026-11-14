#!/usr/bin/env python3
"""Install unbound as Pi-hole's own recursive DNS resolver, or remove it completely.

Follows Pi-hole's official guide (https://docs.pi-hole.net/guides/dns/unbound/) step by
step and runs its checks. Every change is written to a journal before it is made, so a
failed or cancelled install can be undone and --remove can put the system back. Pi-hole
is only moved onto or off unbound after a check proves the new path resolves names.

Uses only the Python standard library because it is started with
`sudo python3 unbound.py`, and sudo selects the system Python, which has no third-party
packages. Supports Python 3.9+, Debian-based systems with systemd, and Pi-hole v6.
"""

from __future__ import annotations

import argparse
import fcntl
import ipaddress
import json
import os
import re
import secrets
import shutil
import signal
import socket
import struct
import subprocess
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import NoReturn

VERSION = "1.0.0"
REPO_URL = "https://github.com/slyfox1186/pihole-regex"
GUIDE_URL = "https://docs.pi-hole.net/guides/dns/unbound/"

PORT = 5335
UNBOUND_UPSTREAM = f"127.0.0.1#{PORT}"
PACKAGES = ("unbound", "dns-root-data")
CONF_FILE = "/etc/unbound/unbound.conf.d/pi-hole.conf"
CONF_DIRS = ("/etc/unbound", "/etc/unbound/unbound.conf.d")
STATE_DIR = "/var/lib/pihole-unbound"
STATE_FILE = f"{STATE_DIR}/state.json"
BACKUP_DIR = f"{STATE_DIR}/backup"
LOCK_FILE = "/run/lock/pihole-unbound.lock"
RESOLVCONF_CONF = "/etc/resolvconf.conf"
RESOLVCONF_SNIPPET = "/etc/unbound/unbound.conf.d/resolvconf_resolvers.conf"
RESOLVCONF_SERVICE = "unbound-resolvconf.service"
SYSCTL_FILE = "/etc/sysctl.d/99-unbound.conf"
SYSCTL_KEY = "net.core.rmem_max"
RMEM_PROC = "/proc/sys/net/core/rmem_max"
RMEM_WANTED = 1048576
DEFAULT_PIHOLE_LOG = "/var/log/pihole/pihole.log"
OS_RELEASE = "/etc/os-release"
CHECK_NAME = "pi-hole.net"
MARKER = "# Written by unbound.py from github.com/slyfox1186/pihole-regex."
ROOT_V4 = "198.41.0.4"            # a.root-servers.net, the server the guide tests
ROOT_V6 = "2001:503:ba3e::2:30"   # a.root-servers.net over IPv6
PRESETS = (
    ("Quad9", ("9.9.9.9", "149.112.112.112")),
    ("Cloudflare", ("1.1.1.1", "1.0.0.1")),
    ("Google", ("8.8.8.8", "8.8.4.4")),
)
APT_ENV = {"DEBIAN_FRONTEND": "noninteractive", "LC_ALL": "C", "LANG": "C"}
# Waits for unattended-upgrades or another apt run instead of failing at once.
APT_OPTS = ("-o", "DPkg::Lock::Timeout=300")
INSTALL_ARGS = ("install", "-y", "--no-remove", "-o", "Dpkg::Options::=--force-confold")
APT_HISTORY = "/var/log/apt/history.log"
# A harmless apt option carrying a random value, so apt's history names this exact run.
RUN_MARKER = "PiholeUnbound::Run="
PACKAGE_NAME = re.compile(r"^[a-z0-9][a-z0-9+.-]+(:[a-z0-9-]+)?$")

EXIT_OK, EXIT_ERROR, EXIT_USAGE, EXIT_CANCELLED = 0, 1, 2, 130

TYPE_A, TYPE_NS, TYPE_CNAME, TYPE_TXT, TYPE_AAAA = 1, 2, 5, 16, 28
CLASS_IN, CLASS_CH = 1, 3
RCODE_NOERROR, RCODE_SERVFAIL, RCODE_NXDOMAIN = 0, 2, 3
FLAG_QR, FLAG_AA, FLAG_TC, FLAG_RD, FLAG_RA, FLAG_AD = 0x8000, 0x0400, 0x0200, 0x0100, 0x0080, 0x0020
RCODES = {0: "NOERROR", 1: "FORMERR", 2: "SERVFAIL", 3: "NXDOMAIN", 4: "NOTIMP", 5: "REFUSED"}


class AppError(Exception):
    """A failure with a message meant for the user."""


class Cancelled(Exception):
    """Ctrl+C or SIGTERM, raised at a point where the undo path can run."""


class UnsupportedSystem(AppError):
    """Not a Debian-based system with systemd and Pi-hole v6; nothing was changed."""


class DNSError(Exception):
    """A DNS reply that is missing, malformed or does not belong to the question."""


# ---------------------------------------------------------------------------
# Terminal output (copied from pi.py: each script must work as a single file)
# ---------------------------------------------------------------------------

class Palette:
    def __init__(self, enabled: bool) -> None:
        def code(n: int) -> str:
            return f"\033[{n}m" if enabled else ""

        self.reset, self.bold, self.dim = code(0), code(1), code(2)
        self.red, self.green, self.yellow = code(31), code(32), code(33)
        self.blue, self.magenta, self.cyan = code(34), code(35), code(36)


def _color_wanted(argv: list[str]) -> bool:
    # Follows the NO_COLOR convention (https://no-color.org) and keeps escape
    # codes out of pipes and log files.
    return (sys.stdout.isatty() and os.environ.get("NO_COLOR", "") == ""
            and os.environ.get("TERM") != "dumb" and "--no-color" not in argv)


C = Palette(_color_wanted(sys.argv))
INTERACTIVE = sys.stdin.isatty() and sys.stdout.isatty()


def heading(text: str) -> None:
    print(f"\n{C.bold}{C.cyan}{text}{C.reset}")


def success(text: str) -> None:
    print(f"{C.green}{text}{C.reset}")


def note(text: str) -> None:
    print(f"{C.dim}{text}{C.reset}")


def step(text: str) -> None:
    print(f"  {C.cyan}>{C.reset} {text}")


def passed(text: str) -> None:
    print(f"    {C.green}ok{C.reset}  {text}")


def warn(text: str) -> None:
    sys.stdout.flush()  # keep stdout and stderr in order when both are piped
    print(f"{C.yellow}Warning:{C.reset} {text}", file=sys.stderr)


def error(text: str) -> None:
    sys.stdout.flush()
    print(f"{C.red}{C.bold}Error:{C.reset} {text}", file=sys.stderr)


def ask(prompt: str) -> str:
    return input(f"{C.bold}{prompt}{C.reset} ").strip()


def confirm(question: str, *, default: bool, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    if not sys.stdin.isatty():
        warn(f"{question} Not asked because input is not a terminal; pass --yes to agree.")
        return False
    hint = "[Y/n]" if default else "[y/N]"
    while True:
        reply = input(f"{C.yellow}{question}{C.reset} {hint} ").strip().lower()
        if not reply:
            return default
        if reply in ("y", "yes"):
            return True
        if reply in ("n", "no"):
            return False
        print("Please answer y or n.")


def page(text: str) -> None:
    height = shutil.get_terminal_size((100, 24)).lines
    pager = shutil.which("less")
    if INTERACTIVE and pager and text.count("\n") > height - 2:
        subprocess.run([pager, "-RFX"], input=text.encode(), check=False)
    else:
        print(text)


# ---------------------------------------------------------------------------
# Cancellation: Ctrl+C and SIGTERM are held during steps that must not stop halfway
# ---------------------------------------------------------------------------

_HOLD = {"depth": 0, "pending": False, "reason": ""}
_SAVED_HANDLERS: list = []
_SIGNALS = {signal.SIGINT, signal.SIGTERM}


def _hold_signal(signum: int, frame: object) -> None:
    del signum, frame
    _HOLD["pending"] = True
    warn(f"Please wait: {_HOLD['reason']} It stops as soon as that is safe.")


@contextmanager
def uninterruptible(reason: str) -> Iterator[None]:
    """Defer Ctrl+C and SIGTERM until the block ends, then raise Cancelled.

    Nested blocks share one pending flag; the outermost one delivers it. If the block
    already failed, its own exception is raised instead.
    """
    # Both signals are blocked while handlers and the shared flag change, so a signal can
    # never land between the two handler swaps and leave one of them behind.
    mask = signal.pthread_sigmask(signal.SIG_BLOCK, _SIGNALS)
    try:
        if _HOLD["depth"] == 0:
            _HOLD["reason"] = reason
            _SAVED_HANDLERS[:] = [signal.signal(signal.SIGINT, _hold_signal),
                                  signal.signal(signal.SIGTERM, _hold_signal)]
        _HOLD["depth"] += 1
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, mask)
    deliver = False
    try:
        yield
    finally:
        mask = signal.pthread_sigmask(signal.SIG_BLOCK, _SIGNALS)
        try:
            _HOLD["depth"] -= 1
            if _HOLD["depth"] == 0:
                signal.signal(signal.SIGINT, _SAVED_HANDLERS[0])
                signal.signal(signal.SIGTERM, _SAVED_HANDLERS[1])
                deliver, _HOLD["pending"] = bool(_HOLD["pending"]), False
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, mask)
    if deliver:
        raise Cancelled()


# ---------------------------------------------------------------------------
# DNS messages (RFC 1035), enough for the guide's checks without needing dig
# ---------------------------------------------------------------------------

def encode_name(name: str) -> bytes:
    out = b""
    for label in name.rstrip(".").split("."):
        if not label:
            continue
        raw = label.encode("ascii")
        if len(raw) > 63:
            raise ValueError(f"DNS label too long: {label}")
        out += bytes([len(raw)]) + raw
    return out + b"\0"


def build_query(qid: int, name: str, qtype: int, qclass: int = CLASS_IN, *,
                recursion: bool = True, ad: bool = False) -> bytes:
    flags = (FLAG_RD if recursion else 0) | (FLAG_AD if ad else 0)
    header = struct.pack(">HHHHHH", qid, flags, 1, 0, 0, 0)
    return header + encode_name(name) + struct.pack(">HH", qtype, qclass)


def read_name(data: bytes, offset: int) -> tuple[str, int]:
    """Return the name at `offset` and the offset just after it, following compression."""
    labels: list[str] = []
    end = -1
    pos = offset
    for _ in range(128):
        if pos >= len(data):
            raise DNSError("reply ends inside a name")
        length = data[pos]
        if length == 0:
            return ".".join(labels).lower(), (pos + 1 if end < 0 else end)
        if length & 0xC0 == 0xC0:
            if pos + 1 >= len(data):
                raise DNSError("reply ends inside a name pointer")
            target = ((length & 0x3F) << 8) | data[pos + 1]
            # A pointer may only point backwards; this rules out loops.
            if target >= pos:
                raise DNSError("name pointer does not point backwards")
            if end < 0:
                end = pos + 2
            pos = target
            continue
        if length > 63:
            raise DNSError("bad label length")
        if pos + 1 + length > len(data):
            raise DNSError("reply ends inside a label")
        labels.append(data[pos + 1:pos + 1 + length].decode("ascii", "replace"))
        pos += 1 + length
    raise DNSError("name has too many labels")


def txt_strings(data: bytes) -> list[str]:
    parts, pos = [], 0
    while pos < len(data):
        size = data[pos]
        if pos + 1 + size > len(data):
            raise DNSError("TXT data runs past its record")
        parts.append(data[pos + 1:pos + 1 + size].decode("utf-8", "replace"))
        pos += 1 + size
    return parts


@dataclass
class Record:
    type: int
    data: bytes

    def text(self) -> str:
        if self.type == TYPE_A:
            return socket.inet_ntop(socket.AF_INET, self.data)
        if self.type == TYPE_AAAA:
            return socket.inet_ntop(socket.AF_INET6, self.data)
        if self.type == TYPE_TXT:
            return "".join(txt_strings(self.data))
        return self.data.hex()


@dataclass
class Reply:
    rcode: int
    flags: int
    answers: list[Record] = field(default_factory=list)

    def flag(self, bit: int) -> bool:
        return self.flags & bit != 0

    def addresses(self) -> list[str]:
        return [r.text() for r in self.answers if r.type in (TYPE_A, TYPE_AAAA)]

    def texts(self) -> list[str]:
        return [r.text() for r in self.answers if r.type == TYPE_TXT]

    def has(self, rtype: int) -> bool:
        return any(r.type == rtype for r in self.answers)

    def flag_names(self) -> str:
        names = (("qr", FLAG_QR), ("aa", FLAG_AA), ("tc", FLAG_TC), ("rd", FLAG_RD),
                 ("ra", FLAG_RA), ("ad", FLAG_AD))
        return " ".join(n for n, bit in names if self.flag(bit))


def parse_reply(data: bytes, qid: int, name: str, qtype: int, qclass: int, *,
                allow_truncated: bool = False) -> Reply:
    """Check the reply belongs to the question, then keep the answers for that name.

    A truncated (TC) UDP reply is returned without answers when `allow_truncated` is set,
    so the caller can ask again over TCP. Answers count only if their class matches and
    their owner is the question name or a CNAME target reached from it.
    """
    if len(data) < 12:
        raise DNSError("reply shorter than a DNS header")
    rid, flags, qdcount, ancount, _ns, _ar = struct.unpack(">HHHHHH", data[:12])
    if rid != qid:
        raise DNSError("reply ID does not match the question")
    if not flags & FLAG_QR or (flags >> 11) & 0xF != 0:
        raise DNSError("message is not a standard query reply")
    if qdcount != 1:
        raise DNSError("reply does not repeat the question")
    qname, pos = read_name(data, 12)
    if pos + 4 > len(data):
        raise DNSError("reply ends inside the question")
    rtype, rclass = struct.unpack(">HH", data[pos:pos + 4])
    if (qname.rstrip("."), rtype, rclass) != (name.lower().rstrip("."), qtype, qclass):
        raise DNSError("reply is for a different question")
    pos += 4
    reply = Reply(flags & 0x000F, flags)
    if flags & FLAG_TC:
        if allow_truncated:
            return reply
        raise DNSError("reply is truncated")
    raw = []
    for _ in range(ancount):
        owner, pos = read_name(data, pos)
        if pos + 10 > len(data):
            raise DNSError("reply ends inside a record")
        atype, aclass, _ttl, size = struct.unpack(">HHIH", data[pos:pos + 10])
        pos += 10
        if pos + size > len(data):
            raise DNSError("reply ends inside record data")
        target = ""
        if atype == TYPE_CNAME:
            target, end = read_name(data, pos)
            if end != pos + size:
                raise DNSError("CNAME data does not match its length")
        raw.append((owner.rstrip("."), atype, aclass, data[pos:pos + size], target.rstrip(".")))
        pos += size
    chain = {qname.rstrip(".")}
    grew = True
    while grew:
        grew = False
        for owner, atype, aclass, _rdata, target in raw:
            if atype == TYPE_CNAME and aclass == qclass and owner in chain and target not in chain:
                chain.add(target)
                grew = True
    for owner, atype, aclass, rdata, _target in raw:
        if owner not in chain or aclass != qclass:
            continue
        if (atype == TYPE_A and len(rdata) != 4) or (atype == TYPE_AAAA and len(rdata) != 16):
            raise DNSError("address record has the wrong length")
        if atype == TYPE_TXT:
            txt_strings(rdata)
        reply.answers.append(Record(atype, rdata))
    return reply


def usable(address: str) -> bool:
    """A real public address; blocking answers (0.0.0.0, ::, Pi-hole's own LAN IP) do not count."""
    try:
        return ipaddress.ip_address(address).is_global
    except ValueError:
        return False


def recv_exact(sock: socket.socket, size: int) -> bytes:
    data = b""
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise DNSError("connection closed before the reply was complete")
        data += chunk
    return data


# ---------------------------------------------------------------------------
# Everything that touches the system goes through System, so tests can fake it
# ---------------------------------------------------------------------------

@dataclass
class Result:
    code: int
    out: str = ""
    err: str = ""

    @property
    def ok(self) -> bool:
        return self.code == 0

    def message(self) -> str:
        return (self.err or self.out).strip() or f"exit code {self.code}"


class System:
    def __init__(self, root: str = "/") -> None:
        self.root = Path(root)

    def path(self, name: str) -> Path:
        return self.root / name.lstrip("/")

    def which(self, name: str) -> bool:
        return shutil.which(name) is not None

    def is_root(self) -> bool:
        return os.geteuid() == 0

    def run(self, cmd: list[str], *, env: dict[str, str] | None = None) -> Result:
        try:
            done = subprocess.run(cmd, capture_output=True, text=True, check=False,
                                  env={**os.environ, **(env or {})})
        except OSError as exc:
            return Result(127, "", str(exc))
        return Result(done.returncode, done.stdout, done.stderr)

    def run_protected(self, cmd: list[str], *, env: dict[str, str] | None = None) -> Result:
        """Run apt or dpkg, showing its output and keeping a copy; it always finishes.

        It runs in its own session, so the terminal's Ctrl+C does not reach it, and a
        cancel received meanwhile is delivered only after it exits: stopping dpkg
        halfway can leave packages half configured.
        """
        with uninterruptible(f"{cmd[0]} is running."):
            show = True
            try:
                sys.stdout.flush()  # keep this script's lines ahead of apt's in piped output
            except OSError:
                show = False
            try:
                proc = subprocess.Popen(cmd, env={**os.environ, **(env or {})}, start_new_session=True,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        text=True, errors="replace")
            except OSError as exc:
                raise AppError(f"Could not run {cmd[0]}: {exc}") from exc
            lines = []
            try:
                for line in proc.stdout or ():
                    lines.append(line)
                    if show:
                        try:
                            print(line, end="", flush=True)
                        except OSError:
                            show = False  # the terminal went away; apt still has to finish
            finally:
                code = proc.wait()
                if proc.stdout is not None:
                    proc.stdout.close()
            return Result(code, "".join(lines))

    def exchange(self, server: str, port: int, packet: bytes, *, tcp: bool, timeout: float) -> bytes:
        family = socket.AF_INET6 if ":" in server else socket.AF_INET
        kind = socket.SOCK_STREAM if tcp else socket.SOCK_DGRAM
        with socket.socket(family, kind) as sock:
            sock.settimeout(timeout)
            if tcp:
                sock.connect((server, port))
                sock.sendall(struct.pack(">H", len(packet)) + packet)
                (size,) = struct.unpack(">H", recv_exact(sock, 2))
                return recv_exact(sock, size)
            sock.sendto(packet, (server, port))
            deadline = time.monotonic() + timeout
            while True:
                sock.settimeout(max(0.05, deadline - time.monotonic()))
                data, source = sock.recvfrom(65535)
                # Ignore anything that is not from the server that was asked.
                if ipaddress.ip_address(source[0]) == ipaddress.ip_address(server) and source[1] == port:
                    return data
                if time.monotonic() >= deadline:
                    raise TimeoutError("no reply from the server that was asked")

    def ask(self, server: str, name: str, qtype: int, *, port: int = 53, qclass: int = CLASS_IN,
            recursion: bool = True, ad: bool = False, tcp: bool = False,
            timeout: float = 3.0, tries: int = 2) -> Reply:
        last = "no reply"
        for _ in range(tries):
            qid = secrets.randbelow(65536)
            packet = build_query(qid, name, qtype, qclass, recursion=recursion, ad=ad)
            try:
                reply = parse_reply(self.exchange(server, port, packet, tcp=tcp, timeout=timeout),
                                    qid, name, qtype, qclass, allow_truncated=not tcp)
                if reply.flag(FLAG_TC):
                    return self.ask(server, name, qtype, port=port, qclass=qclass,
                                    recursion=recursion, ad=ad, tcp=True, timeout=timeout, tries=tries)
                return reply
            except (OSError, DNSError) as exc:
                last = str(exc) or type(exc).__name__
        raise DNSError(last)

    def can_bind(self, port: int, *, tcp: bool) -> bool:
        kind = socket.SOCK_STREAM if tcp else socket.SOCK_DGRAM
        with socket.socket(socket.AF_INET, kind) as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                return False
        return True

    def resolves(self, name: str) -> bool:
        try:
            return len(socket.getaddrinfo(name, 443)) > 0
        except OSError:
            return False

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    @contextmanager
    def lock(self) -> Iterator[None]:
        """One install or remove at a time; apt's own lock does not cover the steps around it."""
        path = self.path(LOCK_FILE)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a") as handle:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise AppError("Another unbound.py run is in progress. Wait for it to finish.") from exc
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def write_atomic(path: Path, text: str, mode: int = 0o644) -> None:
    """Write through a temporary file, flushed to disk, so a crash leaves old or new, never half."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    tmp.chmod(mode)
    os.replace(tmp, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def read_os_release(sysm: System) -> dict[str, str]:
    values: dict[str, str] = {}
    try:
        text = sysm.path(OS_RELEASE).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return values
    for line in text.splitlines():
        key, sep, value = line.partition("=")
        if sep and key.strip() and not key.startswith("#"):
            values[key.strip()] = value.strip().strip("\"'")
    return values


def check_debian(sysm: System) -> str:
    """Return the OS name, or raise UnsupportedSystem for anything not Debian-based."""
    release = read_os_release(sysm)
    name = release.get("PRETTY_NAME") or release.get("NAME") or "an unknown system"
    family = {release.get("ID", "").lower(), *release.get("ID_LIKE", "").lower().split()}
    if "debian" not in family or not (sysm.which("apt-get") and sysm.which("dpkg-query")):
        raise UnsupportedSystem(
            f"This system is {name}. unbound.py supports only Debian-based systems "
            f"(Debian, Ubuntu, Raspberry Pi OS, Armbian and others built on Debian). "
            f"Nothing was changed. For other systems, follow Pi-hole's guide: {GUIDE_URL}")
    return name


def parse_upstreams(text: str) -> list[str]:
    """Parse `pihole-FTL --config dns.upstreams` output, for example `[ 1.1.1.1, 1.0.0.1 ]`."""
    value = text.strip()
    if not (value.startswith("[") and value.endswith("]")):
        raise AppError(f"Unexpected answer from pihole-FTL for dns.upstreams: {value!r}")
    return [item.strip().strip("\"'") for item in value[1:-1].split(",") if item.strip().strip("\"'")]


def split_upstream(item: str) -> tuple[str, int]:
    """("host", port) for Pi-hole's `host#port` form; the port defaults to 53."""
    host, sep, port = item.rpartition("#")
    if sep and port.isdigit():
        item, number = host, int(port)
    else:
        number = 53
    item = item.strip("[]").lower()
    try:
        item = str(ipaddress.ip_address(item))
    except ValueError:
        pass  # a host name such as docker-resolver stays as written
    return item, number


def is_this_machine(host: str) -> bool:
    if host == "localhost":
        return True
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    return address.is_loopback or address.is_unspecified


def points_at_unbound(item: str) -> bool:
    host, port = split_upstream(item)
    return port == PORT and is_this_machine(host)


def is_loop(item: str) -> bool:
    """True if Pi-hole would forward to the unbound being removed or to itself."""
    host, port = split_upstream(item)
    return is_this_machine(host) and port in (53, PORT)


def parse_upstream_option(value: str) -> list[str]:
    items = [t for t in value.replace(",", " ").split() if t]
    if not items:
        raise AppError("--upstream needs at least one IP address, for example --upstream 9.9.9.9,149.112.112.112")
    for item in items:
        host, port = split_upstream(item)
        try:
            ipaddress.ip_address(host)
        except ValueError as exc:
            raise AppError(f"--upstream takes IP addresses with an optional #port; {item!r} is not one.") from exc
        if not 0 < port < 65536:
            raise AppError(f"--upstream: {item!r} has a port outside 1-65535.")
        if is_loop(item):
            raise AppError(f"--upstream: {item} points at this machine's unbound or at Pi-hole itself.")
    return items


def render_config(ipv6: bool) -> str:
    return f"""{MARKER}
# unbound.py --remove deletes it. Settings follow Pi-hole's guide:
# {GUIDE_URL}
server:
    # If no logfile is specified, syslog is used
    verbosity: 0

    interface: 127.0.0.1
    port: {PORT}
    do-ip4: yes
    do-udp: yes
    do-tcp: yes

    # Set from whether this machine reached a root server over IPv6 during install
    do-ip6: {"yes" if ipv6 else "no"}

    # You want to leave this to no unless you have *native* IPv6
    prefer-ip6: no

    # Root server list from the dns-root-data package, which apt keeps current
    root-hints: "/usr/share/dns/root.hints"

    # Trust glue only if it is within the server's authority
    harden-glue: yes

    # Require DNSSEC data for trust-anchored zones, if such data is absent, the zone becomes BOGUS
    harden-dnssec-stripped: yes

    # Don't use Capitalization randomization as it known to cause DNSSEC issues sometimes
    use-caps-for-id: no

    # Reduce EDNS reassembly buffer size (DNS Flag Day 2020)
    edns-buffer-size: 1232

    # Perform prefetching of close to expired message cache entries
    prefetch: yes

    # One thread should be sufficient for most home networks
    num-threads: 1

    # Ensure kernel buffer is large enough to not lose messages in traffic spikes
    so-rcvbuf: 1m

    # Ensure privacy of local IP ranges
    private-address: 192.168.0.0/16
    private-address: 169.254.0.0/16
    private-address: 172.16.0.0/12
    private-address: 10.0.0.0/8
    private-address: fd00::/8
    private-address: fe80::/10

    # Ensure no reverse queries to non-public IP ranges (RFC6303 4.2)
    private-address: 192.0.2.0/24
    private-address: 198.51.100.0/24
    private-address: 203.0.113.0/24
    private-address: 255.255.255.255/32
    private-address: 2001:db8::/32
"""


def set_sysctl_line(text: str, value: int) -> str:
    """Set the rmem_max key in a sysctl file's text, leaving every other line as it was."""
    pattern = re.compile(r"^\s*net\.core\.rmem_max\s*=.*$", re.MULTILINE)
    line = f"{SYSCTL_KEY}={value}"
    if pattern.search(text):
        return pattern.sub(line, text)
    return text + ("" if text == "" or text.endswith("\n") else "\n") + line + "\n"


def parse_new_packages(text: str) -> list[str]:
    """Names under apt's "The following NEW packages will be installed:" heading.

    apt prints this list while it holds its lock, so it is what this run really installed.
    """
    names: list[str] = []
    collecting = False
    for line in text.splitlines():
        if line.startswith("The following NEW packages will be installed"):
            collecting = True
        elif collecting and line.startswith(" "):
            names.extend(line.split())
        elif collecting:
            break
    return names


def history_installs(text: str, command: str, since: float) -> list[str] | None:
    """Packages apt's history log says `command` installed, at or after `since`.

    apt writes this log itself at the end of each transaction, so it is evidence of what a
    run installed even if this script stopped before saving apt's output. None if no
    matching run is recorded.
    """
    found = None
    for block in re.split(r"\n\s*\n", text):
        fields = dict(line.split(": ", 1) for line in block.strip().splitlines() if ": " in line)
        if fields.get("Commandline", "").strip() != command:
            continue
        try:
            start = time.mktime(time.strptime(fields.get("Start-Date", "").strip(), "%Y-%m-%d  %H:%M:%S"))
        except ValueError:
            continue
        if start >= since - 60:
            found = re.findall(r"([a-z0-9][^\s,()]*) \(", fields.get("Install", ""))
    return found


def parse_apt_simulation(text: str) -> tuple[list[str], list[str], list[str]]:
    """Return (new, upgraded, removed) package names from `apt-get -s` output."""
    new, upgraded, removed = [], [], []
    for line in text.splitlines():
        match = re.match(r"^(Inst|Remv|Purg) (\S+)( \[[^\]]*\])?", line)
        if not match:
            continue
        action, name, old = match.group(1), match.group(2), match.group(3)
        if action == "Inst":
            (upgraded if old else new).append(name)
        else:
            removed.append(name)
    return new, upgraded, removed


# ---------------------------------------------------------------------------
# State journal
# ---------------------------------------------------------------------------

STATUSES = ("installing", "installed", "removing", "incomplete")


def _invalid(why: str) -> NoReturn:
    raise AppError(f"{STATE_FILE} is not a valid record ({why}). Nothing was changed. "
                   "Move the file away only if you are sure nothing from this script is installed.")


def _str_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


def validate_state(sysm: System, data: object) -> dict:
    """Check every field before anything is undone from it; a wrong default could delete files."""
    if not isinstance(data, dict):
        _invalid("not an object")
    if data.get("version") != 1:
        _invalid(f"unknown version {data.get('version')!r}")
    if data.get("status") not in STATUSES:
        _invalid(f"unknown status {data.get('status')!r}")
    changes = data.get("changes")
    if not isinstance(changes, list):
        _invalid("no list of changes")
    seen = set()
    for entry in changes:
        if not isinstance(entry, dict) or not isinstance(entry.get("done"), bool):
            _invalid("a change without its done flag")
        kind = entry.get("kind")
        if kind in seen:
            _invalid(f"{kind} recorded twice")
        seen.add(kind)
        if kind == "config":
            dirs = entry.get("created_dirs")
            if not _str_list(dirs) or not set(dirs) <= set(CONF_DIRS):
                _invalid("config.created_dirs")
        elif kind == "packages":
            lists = [entry.get(k) for k in ("planned", "preexisting", "owned")]
            if not all(_str_list(v) and all(PACKAGE_NAME.match(p) for p in v) for v in lists):
                _invalid("packages lists")
            command = entry.get("command")
            if not isinstance(command, str) or not re.search(rf"^apt-get .*-o {RUN_MARKER}[0-9a-f]{{16}} ", command):
                _invalid("packages.command")
        elif kind == "resolvconf":
            if "conf_backup" not in entry or not isinstance(entry.get("service_disabled"), bool):
                _invalid("resolvconf fields")
            _check_backup(sysm, entry["conf_backup"], "resolvconf.conf")
        elif kind == "sysctl":
            if (not isinstance(entry.get("old_value"), int) or "backup" not in entry
                    or not isinstance(entry.get("skipped"), bool)):
                _invalid("sysctl fields")
            _check_backup(sysm, entry["backup"], "99-unbound.conf")
        elif kind == "upstreams":
            if not _str_list(entry.get("old")):
                _invalid("upstreams.old")
        else:
            _invalid(f"unknown change {kind!r}")
    return data


def _check_backup(sysm: System, value: object, label: str) -> None:
    # The copy is made before its change is recorded, so a named backup must always exist.
    if value is None:
        return
    if value != f"{BACKUP_DIR}/{label}":
        _invalid(f"backup path {value!r}")
    if not sysm.path(str(value)).is_file():
        _invalid(f"backup {value} is missing")


class State:
    """What this script changed, written to disk before and after every change."""

    def __init__(self, sysm: System, data: dict) -> None:
        self.sysm = sysm
        self.data = data

    @classmethod
    def load(cls, sysm: System) -> State | None:
        path = sysm.path(STATE_FILE)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise AppError(f"{STATE_FILE} cannot be read ({exc}). Nothing was changed.") from exc
        return cls(sysm, validate_state(sysm, data))

    @classmethod
    def new(cls, sysm: System) -> State:
        return cls(sysm, {"version": 1, "status": "installing", "created": int(time.time()), "changes": []})

    def save(self) -> None:
        write_atomic(self.sysm.path(STATE_FILE), json.dumps(self.data, indent=2) + "\n", 0o600)

    @property
    def status(self) -> str:
        return str(self.data.get("status", ""))

    def set_status(self, status: str) -> None:
        self.data["status"] = status
        self.save()

    def change(self, kind: str) -> dict | None:
        for entry in self.data["changes"]:
            if entry.get("kind") == kind:
                return entry
        return None

    def begin(self, kind: str, **details: object) -> dict:
        entry = {"kind": kind, "done": False, **details}
        self.data["changes"].append(entry)
        self.save()
        return entry

    def finish(self, entry: dict, **details: object) -> None:
        entry.update(details, done=True)
        self.save()

    def backup(self, source: str, label: str) -> str | None:
        src = self.sysm.path(source)
        if not src.exists():
            return None
        dest = self.sysm.path(f"{BACKUP_DIR}/{label}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return f"{BACKUP_DIR}/{label}"

    def remove_all(self) -> None:
        shutil.rmtree(self.sysm.path(STATE_DIR), ignore_errors=True)


# ---------------------------------------------------------------------------
# Pi-hole, packages and services
# ---------------------------------------------------------------------------

class Box:
    """The system as this script sees it: Pi-hole, apt, systemd and the DNS checks."""

    def __init__(self, sysm: System) -> None:
        self.sysm = sysm
        self._arch: str | None = None

    # Pi-hole ---------------------------------------------------------------
    def ftl(self, *args: str) -> Result:
        return self.sysm.run(["pihole-FTL", *args])

    def ftl_major(self) -> int:
        result = self.ftl("--version")
        match = re.search(r"v?(\d+)\.", result.out)
        return int(match.group(1)) if result.ok and match else 0

    def ftl_setting(self, key: str) -> str:
        result = self.ftl("--config", key)
        if not result.ok:
            raise AppError(f"Could not read Pi-hole's setting {key}: {result.message()}")
        return result.out.strip()

    def upstreams(self) -> list[str]:
        return parse_upstreams(self.ftl_setting("dns.upstreams"))

    def set_upstreams(self, servers: list[str]) -> None:
        result = self.ftl("--config", "dns.upstreams", json.dumps(servers))
        if not result.ok:
            raise AppError(f"pihole-FTL refused the upstream servers {servers}: {result.message()}")
        if self.upstreams() != servers:
            raise AppError("Pi-hole did not keep the new upstream servers.")

    def flush_cache(self) -> None:
        """`pihole reloaddns` flushes Pi-hole's DNS cache, so the next answer has to come from upstream."""
        pihole = "pihole" if self.sysm.which("pihole") else "/usr/local/bin/pihole"
        result = self.sysm.run([pihole, "reloaddns"])
        if not result.ok:
            raise AppError(f"pihole reloaddns failed: {result.message()}")

    def pihole_answer(self) -> set[str]:
        """Public addresses Pi-hole returns for pi-hole.net; empty if blocked, local or failing."""
        try:
            reply = self.sysm.ask("127.0.0.1", CHECK_NAME, TYPE_A, timeout=5, tries=2)
        except DNSError:
            return set()
        if reply.rcode != RCODE_NOERROR:
            return set()
        return {a for a in reply.addresses() if usable(a)}

    def pihole_resolves(self) -> bool:
        return len(self.pihole_answer()) > 0

    def direct_answers(self, servers: list[str]) -> set[str] | None:
        """What the IP servers in `servers` return themselves; None if none is an IP address."""
        found: set[str] | None = None
        for server in servers:
            host, port = split_upstream(server)
            try:
                ipaddress.ip_address(host)
            except ValueError:
                continue
            found = found if found is not None else set()
            try:
                reply = self.sysm.ask(host, CHECK_NAME, TYPE_A, port=port, timeout=4, tries=2)
            except DNSError:
                continue
            found |= {a for a in reply.addresses() if usable(a)}
        return found

    def log_text_from(self, path: Path, start: int) -> str:
        try:
            with path.open("rb") as handle:
                size = handle.seek(0, 2)
                handle.seek(start if start <= size else 0)
                return handle.read().decode("utf-8", "replace")
        except OSError:
            return ""

    def check_forwarding(self, expected: list[str], *, seconds: float = 30) -> str:
        """Prove Pi-hole resolves through `expected`. Returns "seen" or "matched".

        Each try flushes Pi-hole's cache and asks for pi-hole.net, which must come back as a
        public address (a blocking or local answer does not count). With query logging on,
        the log must show the query forwarded to one of `expected`. With it off, Pi-hole's
        answer must match what those servers return when asked directly, so at least one of
        them must be an IP address. Pi-hole takes a few seconds to switch servers, so this
        keeps trying until `seconds` run out.
        """
        wanted = {split_upstream(e) for e in expected}
        logging = self.ftl_setting("dns.queryLogging").lower() == "true"
        log = self.sysm.path(self.ftl_setting("files.log.dnsmasq") or DEFAULT_PIHOLE_LOG)
        deadline = time.monotonic() + seconds
        last = "Pi-hole did not return a public address for " + CHECK_NAME
        while True:
            try:
                start = log.stat().st_size
            except OSError:
                start = 0
            self.flush_cache()
            answer = self.pihole_answer()
            if answer and not logging:
                direct = self.direct_answers(expected)
                if direct is None:
                    raise AppError("Query logging is off and " + ", ".join(expected) + " has no IP address to "
                                   "compare with, so it cannot be shown that Pi-hole really uses it. "
                                   "Name IP servers with --upstream.")
                if answer & direct:
                    return "matched"
                last = "Pi-hole's answer does not match what " + ", ".join(expected) + " return"
            elif answer:
                targets: list[str] = []
                for _ in range(10):
                    targets = re.findall(rf"forwarded {re.escape(CHECK_NAME)} to (\S+)",
                                         self.log_text_from(log, start))
                    if targets:
                        break
                    self.sysm.sleep(0.3)
                if any(split_upstream(t) in wanted for t in targets):
                    return "seen"
                last = (f"Pi-hole still forwards to {', '.join(sorted(set(targets)))}" if targets
                        else "Pi-hole's log does not show the test query being forwarded")
            if time.monotonic() >= deadline:
                raise AppError(f"{last} (expected {', '.join(expected)}).")
            self.sysm.sleep(1)

    # Packages --------------------------------------------------------------
    def native_arch(self) -> str:
        if self._arch is None:
            result = self.sysm.run(["dpkg", "--print-architecture"])
            self._arch = result.out.strip() if result.ok else ""
        return self._arch

    def normal(self, name: str) -> str:
        """`unbound` and `unbound:amd64` are the same package on amd64; foreign ones keep their arch."""
        arch = self.native_arch()
        return name[:-len(arch) - 1] if arch and name.endswith(f":{arch}") else name

    def dpkg_status(self, names: list[str]) -> dict[str, str]:
        """Package -> dpkg's two-letter state (`ii` installed, `rc` config files only, ...)."""
        if not names:
            return {}
        result = self.sysm.run(["dpkg-query", "-W", "-f=${binary:Package}\t${db:Status-Abbrev}\n", *names],
                               env=APT_ENV)
        # Exit 1 only means some names are unknown; 2 or more means dpkg could not answer.
        if result.code not in (0, 1):
            raise AppError(f"dpkg-query failed, so installed packages cannot be checked: {result.message()}")
        status = {}
        for line in result.out.splitlines():
            name, _, abbrev = line.partition("\t")
            if name:
                status[self.normal(name)] = abbrev.strip()
        return status

    def present(self, names: list[str]) -> list[str]:
        """Packages with anything left on disk: installed, half installed or config files."""
        wanted = [self.normal(n) for n in names]
        status = self.dpkg_status(wanted)
        return [n for n in wanted if len(status.get(n, "")) >= 2 and status[n][1] != "n"]

    def installed(self, name: str) -> bool:
        state = self.dpkg_status([name]).get(self.normal(name), "")
        return len(state) >= 2 and state[1] in "iUHFWt"

    def simulate(self, action: str, names: list[str]) -> tuple[list[str], list[str], list[str]]:
        result = self.sysm.run(["apt-get", "-s", *APT_OPTS, action, *names], env=APT_ENV)
        if not result.ok:
            raise AppError(f"apt cannot {action} {' '.join(names)}:\n{result.message()}")
        new, upgraded, removed = parse_apt_simulation(result.out)
        return ([self.normal(n) for n in new], [self.normal(n) for n in upgraded],
                [self.normal(n) for n in removed])

    def local_addresses(self) -> set[str]:
        """This machine's own IP addresses, so Pi-hole is never pointed back at itself."""
        result = self.sysm.run(["ip", "-j", "addr", "show"])
        try:
            interfaces = json.loads(result.out) if result.ok else []
        except ValueError:
            return set()
        return {str(ipaddress.ip_address(a["local"])) for i in interfaces for a in i.get("addr_info", [])
                if isinstance(a, dict) and "local" in a}

    def owned(self, state: State) -> list[str]:
        """Packages this script installed: the list apt printed under its lock.

        If the run stopped before that list was saved (power loss), apt's history log is the
        evidence instead: the command carries a random marker, so only this run's entry can
        match. With neither, nothing is claimed: a package another program installed must
        never be removed by this script.
        """
        entry = state.change("packages")
        if entry is None:
            return []
        if entry["done"]:
            return list(entry["owned"])
        try:
            text = self.sysm.path(APT_HISTORY).read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        since = state.data.get("created")
        found = history_installs(text, entry["command"], since if isinstance(since, (int, float)) else 0)
        if found is None:
            return []
        return [p for p in self.present([self.normal(n) for n in found]) if p not in entry["preexisting"]]

    def to_install(self) -> list[str]:
        """unbound, plus dns-root-data only if it is missing: naming an installed package to
        apt would mark it as manually installed, a change this script could not undo."""
        return ["unbound", *(p for p in PACKAGES[1:] if not self.installed(p))]

    def apt(self, *args: str) -> Result:
        return self.sysm.run_protected(["apt-get", *APT_OPTS, *args], env=APT_ENV)

    def check_purge(self, names: list[str]) -> list[str]:
        """The packages to purge, after apt confirms it would remove nothing else."""
        names = self.present(names)
        if names:
            _new, _up, removed = self.simulate("purge", names)
            extra = sorted(set(removed) - set(names))
            if extra:
                raise AppError("Removing " + ", ".join(names) + " would also remove " + ", ".join(extra)
                               + ", which this script did not install. Nothing was changed.")
        return names

    def purge(self, names: list[str]) -> None:
        """Purge exactly `names`. dpkg refuses, rather than widens, if another package needs one."""
        names = self.check_purge(names)
        if not names:
            return
        if not self.sysm.run_protected(["dpkg", "--purge", *names], env=APT_ENV).ok:
            raise AppError("dpkg --purge failed; see its messages above.")
        left = self.present(names)
        if left:
            raise AppError("Still installed after removal: " + ", ".join(left))

    # Services --------------------------------------------------------------
    def systemctl(self, *args: str) -> Result:
        return self.sysm.run(["systemctl", *args])

    def must(self, *args: str) -> None:
        result = self.systemctl(*args)
        if not result.ok:
            raise AppError(f"systemctl {' '.join(args)} failed: {result.message()}")

    def unit_exists(self, unit: str) -> bool:
        result = self.systemctl("list-unit-files", "--no-legend", unit)
        return result.ok and unit in result.out

    def active(self, unit: str) -> bool:
        return self.systemctl("is-active", "--quiet", unit).ok

    def enabled(self, unit: str) -> bool:
        return self.systemctl("is-enabled", "--quiet", unit).ok

    def stop_unbound(self) -> None:
        """Stop unbound and make sure it is really gone from port 5335.

        A half-installed package may have no service unit; then a free port is enough.
        """
        if self.unit_exists("unbound.service"):
            self.must("stop", "unbound.service")
        for _ in range(20):
            if not self.active("unbound.service") and self.port_free() == (True, True):
                return
            self.sysm.sleep(0.25)
        raise AppError(f"unbound did not stop; port {PORT} is still in use.")

    def disable_unbound(self) -> None:
        if self.unit_exists("unbound.service"):
            self.must("disable", "unbound.service")

    def start_unbound(self) -> None:
        """Start unbound and wait until it returns a real address."""
        self.must("start", "unbound.service")
        for _ in range(20):
            try:
                reply = self.sysm.ask("127.0.0.1", CHECK_NAME, TYPE_A, port=PORT, timeout=3, tries=1)
                if reply.rcode == RCODE_NOERROR and any(usable(a) for a in reply.addresses()):
                    return
            except DNSError:
                pass
            self.sysm.sleep(0.5)
        raise AppError(f"unbound started but does not resolve {CHECK_NAME}.")

    # Unbound checks ----------------------------------------------------------
    def port_free(self) -> tuple[bool, bool]:
        return self.sysm.can_bind(PORT, tcp=False), self.sysm.can_bind(PORT, tcp=True)

    def unbound_checks(self, *, show: bool = True) -> list[str]:
        """The guide's three checks against 127.0.0.1:5335. Returns the failures."""
        failures = []

        def query(name: str, *, ad: bool = False, timeout: float = 5.0) -> Reply | None:
            try:
                return self.sysm.ask("127.0.0.1", name, TYPE_A, port=PORT, ad=ad, timeout=timeout, tries=3)
            except DNSError as exc:
                failures.append(f"{name}: no reply from unbound ({exc})")
                return None

        # The first query walks down from the root servers, so it is allowed to be slow.
        reply = query(CHECK_NAME, timeout=10)
        if reply is not None:
            if reply.rcode == RCODE_NOERROR and reply.addresses():
                if show:
                    passed(f"{CHECK_NAME} resolves through unbound ({', '.join(reply.addresses()[:2])})")
            else:
                failures.append(f"{CHECK_NAME}: {RCODES.get(reply.rcode, reply.rcode)} with no address")
        reply = query("fail01.dnssec.works")
        if reply is not None:
            if reply.rcode == RCODE_SERVFAIL and not reply.addresses():
                if show:
                    passed("fail01.dnssec.works is refused (SERVFAIL, no address): DNSSEC validation works")
            else:
                failures.append("fail01.dnssec.works should fail DNSSEC validation (SERVFAIL, no address) "
                                f"but got {RCODES.get(reply.rcode, reply.rcode)}")
        reply = query("dnssec.works", ad=True)
        if reply is not None:
            if reply.rcode == RCODE_NOERROR and reply.addresses() and reply.flag(FLAG_AD):
                if show:
                    passed("dnssec.works is signed and validated (NOERROR, address and the ad flag)")
            else:
                failures.append(f"dnssec.works should be NOERROR with an address and the ad flag but got "
                                f"{RCODES.get(reply.rcode, reply.rcode)}, flags: {reply.flag_names()}")
        return failures


# ---------------------------------------------------------------------------
# Checks before any change
# ---------------------------------------------------------------------------

def supported(box: Box) -> str:
    """Exit 1 on anything this script cannot handle; nothing has been changed yet."""
    sysm = box.sysm
    name = check_debian(sysm)
    if not sysm.is_root():
        raise AppError("Run it with sudo: sudo python3 unbound.py")
    if not (sysm.which("systemctl") and sysm.path("/run/systemd/system").is_dir()):
        raise UnsupportedSystem(f"{name} is not running systemd, which this script needs. Nothing was changed.")
    if not sysm.which("pihole-FTL"):
        raise UnsupportedSystem("Pi-hole is not installed on this machine (pihole-FTL was not found). "
                                "The Pi-hole Docker image is not supported. Nothing was changed.")
    if box.ftl_major() < 6:
        raise UnsupportedSystem("This script needs Pi-hole v6 or newer. Nothing was changed.")
    return name


def root_server_tests(box: Box) -> None:
    """The guide's recommended tests: the root servers must be reachable without interception."""
    explain = ("Your network is changing or blocking DNS traffic to the root servers (often an ISP, "
               "CG-NAT, or a router's DNS filtering or redirection). unbound would not work reliably, "
               "so nothing was installed. See 'Test access to root servers' in " + GUIDE_URL)
    sysm = box.sysm
    for tcp in (False, True):
        how = "TCP" if tcp else "UDP"
        try:
            reply = sysm.ask(ROOT_V4, ".", TYPE_NS, recursion=False, tcp=tcp, timeout=3, tries=2)
        except DNSError as exc:
            raise AppError(f"No {how} reply from a.root-servers.net ({ROOT_V4}): {exc}. {explain}") from exc
        if reply.rcode != RCODE_NOERROR or not reply.has(TYPE_NS) or not reply.flag(FLAG_AA) or reply.flag(FLAG_RA):
            raise AppError(f"The {how} reply did not come from a root server "
                           f"({RCODES.get(reply.rcode, reply.rcode)}, flags: {reply.flag_names()}). {explain}")
        passed(f"a.root-servers.net answers directly over {how} (flags: {reply.flag_names()})")
    try:
        reply = sysm.ask(ROOT_V4, "version.bind", TYPE_TXT, qclass=CLASS_CH, recursion=False, timeout=3, tries=2)
    except DNSError as exc:
        raise AppError(f"No reply to the CHAOS identity check: {exc}. {explain}") from exc
    if not any("ATLAS" in text for text in reply.texts()):
        raise AppError(f"The root server identity check returned {reply.texts() or 'nothing'} instead of ATLAS. {explain}")
    passed("The root server identifies itself as ATLAS, as the guide expects")


def ipv6_works(box: Box) -> bool:
    """`do-ip6: yes` only when a root server really answered over IPv6 (an IPv6 route alone is not enough)."""
    try:
        reply = box.sysm.ask(ROOT_V6, ".", TYPE_NS, recursion=False, timeout=3, tries=1)
    except (DNSError, OSError):
        return False
    return reply.flag(FLAG_AA) and reply.has(TYPE_NS)


def existing_setup(box: Box) -> list[str]:
    """Signs of an unbound this script did not install, including leftovers of an old one."""
    signs = []
    if box.present(["unbound"]):
        signs.append("the unbound package (or its leftover settings) is on this machine")
    elif box.unit_exists("unbound.service"):
        signs.append("an unbound service exists")
    etc = box.sysm.path("/etc/unbound")
    if etc.is_dir() and any(p.is_file() for p in etc.rglob("*")):
        signs.append("/etc/unbound has files in it")
    return signs


# ---------------------------------------------------------------------------
# Undo (shared by a failed install and by --remove)
# ---------------------------------------------------------------------------

def restore_file(sysm: System, target: str, backup: str | None) -> None:
    path = sysm.path(target)
    if backup is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(sysm.path(backup), path)


def undo_system_changes(box: Box, state: State) -> None:
    """Undo everything except Pi-hole's upstream servers, in a fixed order.

    Pi-hole must already be off unbound. Package removal is checked before anything is
    touched and the config file goes only after the packages are gone, so a refusal leaves
    unbound as it was. Every step can run again, so an interrupted undo can be finished by
    a later --remove. Raises AppError on any failure; the record is kept.
    """
    sysm = box.sysm
    owned = box.owned(state)
    entry = state.change("packages")
    if entry is not None and not entry["done"]:
        left = [p for p in box.present(entry["planned"]) if p not in entry["preexisting"] and p not in owned]
        if left:
            warn("The install stopped before apt's list of new packages was saved, and apt's history does "
                 "not show this script installing " + ", ".join(left) + ", so they stay. Remove them with "
                 "'sudo apt purge' if you are sure nothing else needs them.")
    box.check_purge(owned)
    if "unbound" in owned and box.present(["unbound"]):
        box.stop_unbound()
        box.disable_unbound()
        step("Stopped unbound")
    if owned:
        box.purge(owned)
        step("Removed packages: " + ", ".join(owned))
    if state.change("config") is not None:
        conf = sysm.path(CONF_FILE)
        if conf.exists() and MARKER in conf.read_text(encoding="utf-8", errors="replace"):
            conf.unlink()
            step(f"Deleted {CONF_FILE}")
    if "/etc/unbound" in (state.change("config") or {}).get("created_dirs", []):
        # Install refused to run if /etc/unbound held anything, so this file can only have
        # been generated for the unbound package removed above.
        sysm.path(RESOLVCONF_SNIPPET).unlink(missing_ok=True)
    entry = state.change("resolvconf")
    if entry is not None and entry["conf_backup"] is not None:
        # unbound-resolvconf.service belonged to the unbound package removed above, so only
        # the openresolv file needs to go back.
        restore_file(sysm, RESOLVCONF_CONF, entry["conf_backup"])
        step(f"Restored {RESOLVCONF_CONF}")
    entry = state.change("sysctl")
    if entry is not None and not entry["skipped"]:
        restore_file(sysm, SYSCTL_FILE, entry["backup"])
        old = entry["old_value"]
        try:
            current = int(sysm.path(RMEM_PROC).read_text().strip())
        except (OSError, ValueError):
            current = None
        if current != old:
            result = sysm.run(["sysctl", "-w", f"{SYSCTL_KEY}={old}"])
            if not result.ok:
                raise AppError(f"Could not put {SYSCTL_KEY} back to {old}: {result.message()}")
        step(f"Restored {SYSCTL_KEY} to {old}")
    for directory in reversed((state.change("config") or {}).get("created_dirs", [])):
        try:
            sysm.path(directory).rmdir()
        except OSError:
            pass  # not empty or already gone: dpkg or the user keeps files there


def put_back(box: Box, servers: list[str], why: str) -> AppError:
    """After a failed move, restart unbound and give Pi-hole back `servers`, then check.

    Each step is tried even if the one before failed, and the message says what is true.
    """
    problems = []
    if box.present(["unbound"]):
        try:
            box.start_unbound()
        except AppError as exc:
            problems.append(str(exc))
    try:
        if box.upstreams() != servers:
            box.set_upstreams(servers)
    except AppError as exc:
        problems.append(str(exc))
    try:
        box.flush_cache()
    except AppError as exc:
        problems.append(str(exc))
    resolving = box.pihole_resolves()
    if not problems and resolving:
        return AppError(f"{why} Pi-hole is back on {', '.join(servers)} and resolving names; nothing was removed.")
    state_now = "Pi-hole resolves names" if resolving else "Pi-hole does not resolve names"
    return AppError(f"{why} Putting Pi-hole back did not fully work ({'; '.join(problems + [state_now])}). "
                    f"Fix it with:\n  sudo systemctl start unbound\n"
                    f"  sudo pihole-FTL --config dns.upstreams '{json.dumps(servers)}'")


def move_pihole(box: Box, servers: list[str], *, before: list[str]) -> None:
    """Point Pi-hole at `servers` and prove, with unbound stopped, that it resolves through them.

    On failure unbound is started again and Pi-hole goes back to `before`; AppError is raised.
    """
    try:
        if box.upstreams() != servers:
            box.set_upstreams(servers)
        if box.present(["unbound"]) or box.active("unbound.service"):
            box.stop_unbound()
        box.check_forwarding(servers)
    except (AppError, OSError) as exc:
        raise put_back(box, before, str(exc)) from exc
    passed("Pi-hole resolves names with unbound stopped, using " + (", ".join(servers) or "its servers"))


def rollback(box: Box, state: State) -> bool:
    """Undo a failed or cancelled install, DNS first. Returns True if everything was undone."""
    heading("Undoing the changes")
    with uninterruptible("the changes are being undone."):
        entry = state.change("upstreams")
        if entry is not None:
            try:
                move_pihole(box, entry["old"], before=[UNBOUND_UPSTREAM])
                step("Pi-hole uses its earlier upstream servers again: " + (", ".join(entry["old"]) or "(none)"))
            except AppError as exc:
                state.set_status("incomplete")
                error(f"{exc}\nunbound was left installed. Once the old servers answer again, run: "
                      "sudo python3 unbound.py --remove")
                return False
        try:
            undo_system_changes(box, state)
        except AppError as exc:
            state.set_status("incomplete")
            error(f"{exc}\nThe record of changes is kept in {STATE_FILE}; run "
                  "'sudo python3 unbound.py --remove' to finish.")
            return False
        state.remove_all()
    success("Everything this script changed was undone.")
    return True


# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------

def cmd_install(args: argparse.Namespace, box: Box) -> int:
    supported(box)
    with box.sysm.lock():
        return install(args, box)


def install(args: argparse.Namespace, box: Box) -> int:
    sysm = box.sysm
    state = State.load(sysm)
    if state is not None:
        if state.status == "installed":
            success("unbound was already installed by this script; nothing was changed.")
            return cmd_status(args, box, checks_only=True)
        raise AppError(f"An earlier run did not finish ({STATE_FILE} says '{state.status}'). "
                       "Run 'sudo python3 unbound.py --remove' to clean it up first.")
    heading("Checking this system")
    signs = existing_setup(box)
    if signs:
        raise AppError("unbound is already set up on this machine without this script ("
                       + "; ".join(signs) + "). Nothing was changed. To let this script manage it, "
                       "remove that setup first (sudo python3 unbound.py --remove), then install again.")
    if not box.active("pihole-FTL"):
        raise AppError("Pi-hole (pihole-FTL) is not running. Start it first: sudo systemctl start pihole-FTL")
    if not box.pihole_resolves():
        raise AppError(f"Pi-hole does not return an address for {CHECK_NAME} right now. Fix Pi-hole's DNS first.")
    passed("Pi-hole v6 is running and resolving names")
    udp, tcp = box.port_free()
    if not (udp and tcp):
        busy = " and ".join(p for p, free in (("UDP", udp), ("TCP", tcp)) if not free)
        raise AppError(f"Port {PORT} ({busy}) on 127.0.0.1 is already used by another program. Nothing was changed.")
    passed(f"Port {PORT} is free for unbound")
    host_ok = sysm.resolves(CHECK_NAME)

    heading("Testing access to the root servers (Pi-hole's guide)")
    root_server_tests(box)
    ipv6 = ipv6_works(box)
    passed("IPv6 reaches the root servers, so unbound will use it" if ipv6
           else "IPv6 does not reach the root servers, so unbound will use IPv4 only")

    new, upgraded, removed = box.simulate("install", box.to_install())
    if removed:
        raise AppError("Installing unbound would remove " + ", ".join(removed) + ". Nothing was changed.")
    heading("Plan")
    print(f"  1. Write {CONF_FILE} (Pi-hole's settings, port {PORT}, IPv6 {'on' if ipv6 else 'off'})")
    print("  2. Install " + ", ".join(new or box.to_install())
          + (f"; upgrade {', '.join(upgraded)} (upgrades stay)" if upgraded else ""))
    print(f"  3. Turn off {RESOLVCONF_SERVICE} if it is on (Debian Bullseye and newer)")
    print(f"  4. Raise {SYSCTL_KEY} to {RMEM_WANTED} if it is lower")
    print("  5. Start unbound and run the guide's DNSSEC checks")
    print(f"  6. Point Pi-hole at unbound ({UNBOUND_UPSTREAM}) and check Pi-hole really uses it")
    note("  If a step fails, the changes are undone, Pi-hole's DNS servers first.")
    if args.dry_run:
        print(f"\n{C.cyan}Dry run:{C.reset} nothing was changed.")
        return EXIT_OK
    if not confirm("\nInstall unbound now?", default=True, assume_yes=args.yes):
        note("Cancelled. Nothing was changed.")
        return EXIT_OK

    state = State.new(sysm)
    state.save()
    try:
        install_steps(box, state, ipv6, host_ok)
    except (AppError, Cancelled, KeyboardInterrupt) as exc:
        cancelled = not isinstance(exc, AppError)
        error("Cancelled." if cancelled else str(exc))
        rollback(box, state)
        return EXIT_CANCELLED if cancelled else EXIT_ERROR
    except Exception:
        # An unexpected failure still gets the system put back before it is shown.
        error("Unexpected failure; undoing the changes before showing it.")
        rollback(box, state)
        raise
    state.set_status("installed")
    success(f"\nunbound is installed and Pi-hole uses it ({UNBOUND_UPSTREAM}).")
    note("Remove it at any time with: sudo python3 unbound.py --remove")
    return EXIT_OK


def install_steps(box: Box, state: State, ipv6: bool, host_ok: bool) -> None:
    sysm = box.sysm
    heading("Installing")
    if not box.apt("update").ok:
        raise AppError("apt-get update failed; see apt's messages above.")
    names = box.to_install()
    planned, _upgraded, removed = box.simulate("install", names)
    if removed:
        raise AppError("Installing unbound would remove " + ", ".join(removed) + ".")

    # 1. The config goes in first, so unbound's very first start uses port 5335 and never
    #    competes with Pi-hole for port 53.
    entry = state.begin("config", created_dirs=[d for d in CONF_DIRS if not sysm.path(d).exists()])
    write_atomic(sysm.path(CONF_FILE), render_config(ipv6))
    state.finish(entry)
    step(f"Wrote {CONF_FILE}")

    # 2. Packages. This script owns what apt itself lists as NEW while holding its lock;
    #    the snapshot covers a run that stops before that list is saved.
    preexisting = box.present(planned)
    if box.present(["unbound"]) or "unbound" in preexisting:
        raise AppError("unbound was installed by another program while this ran.")
    command = ["apt-get", *APT_OPTS, "-o", RUN_MARKER + secrets.token_hex(8), *INSTALL_ARGS, *names]
    entry = state.begin("packages", planned=planned, preexisting=preexisting, owned=[], command=" ".join(command))
    # A cancel waits until apt's own list is saved, so ownership never falls back to a guess.
    with uninterruptible("apt is installing unbound."):
        result = box.sysm.run_protected(command, env=APT_ENV)
        new = [box.normal(n) for n in parse_new_packages(result.out)]
        state.finish(entry, owned=box.present(new))
    if not result.ok:
        raise AppError("apt-get install failed; see apt's messages above.")
    if "unbound" not in new or not box.installed("unbound"):
        raise AppError("apt did not install unbound in this run, so this script will not manage it.")
    step("Installed " + ", ".join(new))

    # 3. Debian Bullseye+ (guide): stop resolvconf from pointing this machine at unbound on port 53.
    conf = sysm.path(RESOLVCONF_CONF)
    conf_text = conf.read_text(encoding="utf-8", errors="replace") if conf.exists() else ""
    edits_conf = re.search(r"^unbound_conf=", conf_text, re.MULTILINE) is not None
    service_on = box.unit_exists(RESOLVCONF_SERVICE) and (box.enabled(RESOLVCONF_SERVICE)
                                                          or box.active(RESOLVCONF_SERVICE))
    if service_on or edits_conf or sysm.path(RESOLVCONF_SNIPPET).exists():
        entry = state.begin("resolvconf", service_disabled=service_on,
                            conf_backup=state.backup(RESOLVCONF_CONF, "resolvconf.conf") if edits_conf else None)
        if service_on:
            box.must("disable", "--now", RESOLVCONF_SERVICE)
        if edits_conf:
            write_atomic(conf, re.sub(r"^unbound_conf=", "#unbound_conf=", conf_text, flags=re.MULTILINE))
        # Written by that service for the unbound package installed above; nothing else owns it.
        sysm.path(RESOLVCONF_SNIPPET).unlink(missing_ok=True)
        state.finish(entry)
        step(f"Turned off {RESOLVCONF_SERVICE} and unbound's resolvconf entry")

    # 4. so-rcvbuf: 1m needs net.core.rmem_max of at least 1048576 (guide's fix).
    try:
        current = int(sysm.path(RMEM_PROC).read_text().strip())
    except (OSError, ValueError):
        current = None
    if current is None:
        note(f"    {SYSCTL_KEY} cannot be read here; unbound may log a so-rcvbuf warning.")
    elif current < RMEM_WANTED:
        entry = state.begin("sysctl", old_value=current, skipped=False,
                            backup=state.backup(SYSCTL_FILE, "99-unbound.conf"))
        result = sysm.run(["sysctl", "-w", f"{SYSCTL_KEY}={RMEM_WANTED}"])
        if result.ok:
            existing = sysm.path(SYSCTL_FILE)
            text = existing.read_text(encoding="utf-8") if existing.exists() else ""
            write_atomic(existing, set_sysctl_line(text, RMEM_WANTED))
            state.finish(entry)
            step(f"Raised {SYSCTL_KEY} from {current} to {RMEM_WANTED}")
        else:
            # Nothing changed, so there is nothing to undo later.
            state.finish(entry, skipped=True)
            note(f"    {SYSCTL_KEY} cannot be changed here; unbound may log a so-rcvbuf warning.")

    # 5. Start unbound. Its config is checked only if the start fails: Debian's service creates
    #    the DNSSEC trust anchor (/var/lib/unbound/root.key) just before the first start, so
    #    unbound-checkconf fails on a fresh install until then.
    box.must("enable", "unbound.service")
    restart = box.systemctl("restart", "unbound.service")
    if not restart.ok:
        check = sysm.run(["unbound-checkconf"])
        reason = restart.message() if check.ok else check.message()
        raise AppError(f"unbound did not start: {reason}\nSee: sudo journalctl -u unbound --no-pager -n 30")
    step("Started unbound")

    heading("Checking unbound (Pi-hole's guide)")
    failures = box.unbound_checks()
    if failures:
        raise AppError("unbound failed the guide's checks:\n  " + "\n  ".join(failures))

    # 6. Only now does Pi-hole depend on unbound.
    heading("Pointing Pi-hole at unbound")
    old = box.upstreams()
    entry = state.begin("upstreams", old=old)
    box.set_upstreams([UNBOUND_UPSTREAM])
    state.finish(entry)
    step(f"Pi-hole's upstream is now {UNBOUND_UPSTREAM} (was {', '.join(old) or 'none'})")
    if box.check_forwarding([UNBOUND_UPSTREAM]) == "seen":
        passed(f"Pi-hole's log shows it forwarding to {UNBOUND_UPSTREAM}")
    else:
        passed("Pi-hole returns the same answer as unbound (query logging is off, so the log cannot show it)")
    if host_ok and not sysm.resolves(CHECK_NAME):
        raise AppError("This machine can no longer look up names after the change.")


# ---------------------------------------------------------------------------
# Remove
# ---------------------------------------------------------------------------

def choose_upstream(args: argparse.Namespace, current: list[str], saved: list[str]) -> list[str]:
    """Servers for Pi-hole after removal: the others it already uses, else the saved ones, else ask."""
    others = [s for s in current if not is_loop(s)]
    if others:
        return others
    usable = [s for s in saved if not is_loop(s)]
    if usable:
        return usable
    if not INTERACTIVE or args.yes:
        raise AppError("Pi-hole needs another upstream DNS server once unbound is gone, and none was saved. "
                       "Name one, for example: --upstream 9.9.9.9,149.112.112.112. Nothing was changed.")
    print(f"\n{C.bold}Which DNS servers should Pi-hole use after unbound is removed?{C.reset}")
    for i, (label, servers) in enumerate(PRESETS, 1):
        print(f"  {C.green}{i}{C.reset}  {label:<11}{C.dim}{', '.join(servers)}{C.reset}")
    print(f"  {C.green}c{C.reset}  Custom")
    while True:
        reply = ask("Choose 1-3 or c (Enter cancels):").lower()
        if not reply:
            raise Cancelled()
        if reply.isdigit() and 1 <= int(reply) <= len(PRESETS):
            return list(PRESETS[int(reply) - 1][1])
        if reply == "c":
            try:
                return parse_upstream_option(ask("IP addresses, separated by commas:"))
            except AppError as exc:
                error(str(exc))


def check_candidates(box: Box, servers: list[str]) -> None:
    local = box.local_addresses()
    for server in servers:
        host, port = split_upstream(server)
        try:
            ipaddress.ip_address(host)
        except ValueError:
            continue  # a host name such as docker-resolver; Pi-hole's own check covers it
        if host in local and port in (53, PORT):
            raise AppError(f"{server} is this machine (Pi-hole or unbound), not another DNS server. "
                           "Nothing was changed.")
        try:
            reply = box.sysm.ask(host, CHECK_NAME, TYPE_A, port=port, timeout=4, tries=2)
        except DNSError as exc:
            raise AppError(f"{server} does not answer DNS queries ({exc}). Nothing was changed.") from exc
        if reply.rcode != RCODE_NOERROR or not reply.addresses():
            raise AppError(f"{server} returned no address for {CHECK_NAME}. Nothing was changed.")
        passed(f"{server} answers DNS queries")


def cmd_remove(args: argparse.Namespace, box: Box) -> int:
    supported(box)
    with box.sysm.lock():
        return remove(args, box)


def remove(args: argparse.Namespace, box: Box) -> int:
    sysm = box.sysm
    state = State.load(sysm)
    conf = sysm.path(CONF_FILE)
    if state is None:
        if conf.exists() and MARKER in conf.read_text(encoding="utf-8", errors="replace"):
            raise AppError(f"{CONF_FILE} was written by this script but its record ({STATE_FILE}) is "
                           "missing, so it cannot tell what to undo. Nothing was changed.")
        if not box.present(["unbound"]) and not conf.exists():
            success("unbound is not installed. Nothing to remove.")
            return EXIT_OK
    current = box.upstreams()
    uses_unbound = any(points_at_unbound(u) for u in current)
    saved = list((state.change("upstreams") or {}).get("old", [])) if state else []
    if args.upstream:
        servers = parse_upstream_option(args.upstream)
    else:
        servers = choose_upstream(args, current, saved) if uses_unbound else current
    if servers != current:
        check_candidates(box, servers)
    to_purge = box.check_purge(box.owned(state) if state else ["unbound"])

    heading("Plan")
    if servers != current:
        print("  1. Point Pi-hole at " + ", ".join(servers) + " and check it resolves names with unbound stopped")
    else:
        print("  1. Keep Pi-hole's servers (" + ", ".join(current) + ") and check it resolves names with unbound stopped")
    print("  2. Remove " + (", ".join(to_purge) if to_purge else "no packages (none are left)")
          + ("" if state else " (set up without this script; nothing else is touched)"))
    if state is not None:
        print("  3. Put back the settings this script changed (resolvconf, sysctl) and delete its files")
    elif conf.exists():
        print(f"  3. Delete {CONF_FILE} after the package is gone")
    if args.dry_run:
        print(f"\n{C.cyan}Dry run:{C.reset} nothing was changed.")
        return EXIT_OK
    if not confirm("\nRemove unbound now?", default=state is not None, assume_yes=args.yes):
        note("Cancelled. Nothing was changed.")
        return EXIT_OK

    with uninterruptible("unbound is being removed; stopping halfway could leave Pi-hole without DNS."):
        heading("Moving Pi-hole off unbound")
        move_pihole(box, servers, before=current)
        heading("Removing")
        if state is None:
            box.disable_unbound()
            box.purge(to_purge)
            if to_purge:
                step("Removed " + ", ".join(to_purge))
            if conf.exists():
                conf.unlink()
                step(f"Deleted {CONF_FILE}")
        else:
            state.set_status("removing")
            try:
                undo_system_changes(box, state)
            except AppError as exc:
                state.set_status("incomplete")
                raise AppError(f"{exc}\nThe record is kept in {STATE_FILE}; run --remove again to finish.") from exc

        heading("Checking")
        problems = []
        if box.present(["unbound"]):
            problems.append("the unbound package is still on this machine")
        if box.port_free() != (True, True):
            problems.append(f"something still listens on port {PORT}")
        box.flush_cache()
        if not box.pihole_resolves():
            problems.append(f"Pi-hole does not return an address for {CHECK_NAME}")
        if problems:
            raise AppError("After removal: " + "; ".join(problems) + "."
                           + (f" The record is kept in {STATE_FILE}." if state else ""))
        passed(f"unbound is gone, port {PORT} is free and Pi-hole resolves names")
        if state is not None:
            state.remove_all()
    success("\nunbound was removed completely.")
    return EXIT_OK


# ---------------------------------------------------------------------------
# Status (read-only: no cache flush, no service changes)
# ---------------------------------------------------------------------------

def cmd_status(args: argparse.Namespace, box: Box, *, checks_only: bool = False) -> int:
    del args
    sysm = box.sysm
    if not checks_only:
        name = supported(box)
        heading("unbound for Pi-hole")
        state = State.load(sysm)
        installed = box.installed("unbound")
        version = sysm.run(["dpkg-query", "-W", "-f=${Version}", "unbound"]).out.strip() if installed else ""
        active = box.active("unbound.service")
        conf = sysm.path(CONF_FILE)
        owner = ("this script" if conf.exists() and MARKER in conf.read_text(encoding="utf-8", errors="replace")
                 else "set up by hand" if conf.exists() else "missing")
        rows = (
            ("System", name),
            ("Package", f"installed, version {version}" if installed else "not installed"),
            ("Service", ", ".join(("running" if active else "stopped",
                                   "starts at boot" if box.enabled("unbound.service") else "off at boot"))),
            (f"Port {PORT}", "in use" if box.port_free() != (True, True) else "free"),
            ("Config", f"{CONF_FILE} ({owner})"),
            ("Pi-hole uses", ", ".join(box.upstreams()) or "(no upstream servers)"),
            ("Record", f"{STATE_FILE} ({state.status})" if state else "none (not installed by this script)"),
        )
        for label, value in rows:
            print(f"  {label:<14}{value}")
        if not active:
            return EXIT_OK
    heading("Checks")
    failures = box.unbound_checks()
    if any(points_at_unbound(u) for u in box.upstreams()):
        if box.pihole_resolves():
            passed(f"Pi-hole returns an address for {CHECK_NAME}")
        else:
            failures.append(f"Pi-hole does not return an address for {CHECK_NAME}")
    for failure in failures:
        error(failure)
    return EXIT_ERROR if failures else EXIT_OK


# ---------------------------------------------------------------------------
# Interactive menu and command line
# ---------------------------------------------------------------------------

MENU = (
    ("1", "Install", "set up unbound and point Pi-hole at it"),
    ("2", "Remove", "remove unbound completely and put everything back"),
    ("3", "Status", "show the setup and run the guide's checks"),
    ("h", "Help", "command-line options"),
    ("q", "Quit", ""),
)


def interactive(args: argparse.Namespace, box: Box) -> int:
    while True:
        print(f"\n{C.bold}{C.cyan}  unbound for Pi-hole{C.reset}  {C.dim}v{VERSION}  {GUIDE_URL}{C.reset}\n")
        for key, label, text in MENU:
            print(f"  {C.green}{C.bold}{key}{C.reset}  {label:<10}{C.dim}{text}{C.reset}")
        choice = ask("\nChoose an option:").lower()
        if choice in ("q", "quit", "exit"):
            return EXIT_OK
        try:
            if choice == "1":
                cmd_install(args, box)
            elif choice == "2":
                cmd_remove(args, box)
            elif choice == "3":
                cmd_status(args, box)
            elif choice in ("h", "help", "?"):
                page(help_text())
            else:
                continue
        except AppError as exc:
            error(str(exc))
        except Cancelled:
            note("Cancelled.")
        reply = ask(f"\n{C.dim}Press Enter for the menu, or q to quit:{C.reset}").lower()
        if reply in ("q", "quit", "exit"):
            return EXIT_OK


def help_text() -> str:
    r, h, o, a, d = C.reset, C.bold + C.cyan, C.green, C.magenta, C.dim

    def row(flags: str, arg: str, text: str) -> str:
        # Pad on the visible width; the color codes would otherwise skew the column.
        visible = len(flags) + (len(arg) + 1 if arg else 0)
        colored = ", ".join(f"{o}{flag}{r}" for flag in flags.split(", "))
        colored += f" {a}{arg}{r}" if arg else ""
        return f"  {colored}{' ' * (26 - visible)}{text}"

    options = "\n".join((
        row("-i, --install", "", "Install unbound and point Pi-hole at it"),
        row("-r, --remove", "", "Remove unbound completely and put everything back"),
        row("-s, --status", "", "Show the setup and run the guide's checks"),
    ))
    modifiers = "\n".join((
        row("-n, --dry-run", "", "Run the checks and show the plan, change nothing"),
        row("-y, --yes", "", f"Answer yes to every question {d}(for scripts){r}"),
        row("--upstream", "SERVERS", f"DNS servers for Pi-hole after removal {d}(IP[#port], commas){r}"),
        row("--no-color", "", f"Plain output {d}(the NO_COLOR variable works too){r}"),
        row("-h, --help", "", "Show this help"),
        row("--version", "", "Show the version"),
    ))
    return f"""
{h}unbound.py{r} {d}v{VERSION}{r}  Pi-hole's own recursive DNS resolver, installed or removed for you

{h}USAGE{r}
  sudo python3 unbound.py              {d}# interactive menu{r}
  sudo python3 unbound.py --install    {d}# install and switch Pi-hole to unbound{r}
  sudo python3 unbound.py --remove     {d}# remove it and put everything back{r}

{h}OPTIONS{r}
{options}

{h}MODIFIERS{r}
{modifiers}

{h}EXAMPLES{r}
  sudo python3 unbound.py -i -n                         {d}# run the checks, change nothing{r}
  sudo python3 unbound.py -i -y                         {d}# install without questions{r}
  sudo python3 unbound.py -r --upstream 9.9.9.9,149.112.112.112

{h}GOOD TO KNOW{r}
  Follows Pi-hole's guide: {GUIDE_URL}
  Works on Debian-based systems only (Debian, Ubuntu, Raspberry Pi OS, Armbian and
  others built on Debian) with systemd and Pi-hole v6 installed on the machine itself.
  On any other system it changes nothing and exits with code 1.
  Install first checks that the root servers answer without interference, and points
  Pi-hole at unbound only after the guide's DNSSEC checks pass. If a step fails, the
  changes are undone. Remove moves Pi-hole back to the servers it used before (or the
  ones you choose) and proves Pi-hole resolves names with unbound stopped before it
  removes anything. If something cannot be undone safely, unbound is left installed, the
  record in {STATE_DIR} is kept, and running --remove again finishes the job.
  An unbound set up without this script is never taken over; remove can uninstall it.

  {d}Exit codes: 0 done, 1 error or unsupported system, 2 bad option, 130 cancelled.  {REPO_URL}{r}
"""


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        error(f"{message}\n       Run {C.bold}unbound.py --help{C.reset} to see the options.")
        sys.exit(EXIT_USAGE)


class HelpAction(argparse.Action):
    def __init__(self, option_strings: list[str], dest: str, **kwargs: object) -> None:
        super().__init__(option_strings, dest, nargs=0, default=argparse.SUPPRESS)

    def __call__(self, parser, namespace, values, option_string=None):
        print(help_text())
        sys.exit(EXIT_OK)


def build_parser() -> Parser:
    parser = Parser(prog="unbound.py", add_help=False, allow_abbrev=False)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("-i", "--install", action="store_true")
    actions.add_argument("-r", "--remove", action="store_true")
    actions.add_argument("-s", "--status", action="store_true")
    parser.add_argument("-n", "--dry-run", action="store_true")
    parser.add_argument("-y", "--yes", action="store_true")
    parser.add_argument("--upstream", metavar="SERVERS")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("-h", "--help", action=HelpAction)
    parser.add_argument("--version", action="version", version=f"unbound.py {VERSION}")
    return parser


def main(argv: list[str] | None = None, sysm: System | None = None) -> int:
    args = build_parser().parse_args(argv)
    box = Box(sysm or System())
    # The OS check comes before everything else, the menu included.
    check_debian(box.sysm)
    if args.upstream is not None:
        parse_upstream_option(args.upstream)
    if args.install:
        return cmd_install(args, box)
    if args.remove:
        return cmd_remove(args, box)
    if args.status:
        return cmd_status(args, box)
    if not INTERACTIVE:
        raise AppError("The menu needs a terminal. Use an option instead; run unbound.py --help to see them.")
    supported(box)
    return interactive(args, box)


def _raise_cancelled(signum: int, frame: object) -> NoReturn:
    del signum, frame
    raise Cancelled()


def cli(argv: list[str] | None = None, sysm: System | None = None) -> int:
    """Run and turn every outcome into the documented exit code."""
    try:
        return main(argv, sysm)
    except AppError as exc:
        error(str(exc))
        return EXIT_ERROR
    except (KeyboardInterrupt, EOFError, Cancelled):
        print(f"\n{C.yellow}Cancelled.{C.reset}", file=sys.stderr)
        return EXIT_CANCELLED


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, _raise_cancelled)
    sys.exit(cli())
