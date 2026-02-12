from dataclasses import dataclass
from pathlib import Path
import stat

@dataclass(frozen=True)
class Finding:
    path: str
    kind: str
    severity: str

def is_world_writable(mode: int) -> bool:
    return bool(mode & 0o002)

def has_suid(mode: int) -> bool:
    return bool(mode & 0o4000)

def has_sgid(mode: int) -> bool:
    return bool(mode & 0o2000)

def has_sticky(mode: int) -> bool:
    return bool(mode & 0o1000)

def severity_for(mode: int, is_dir: bool) -> str:
    if (has_suid(mode) or has_sgid(mode)) and is_world_writable(mode):
        return "critical"
    if has_suid(mode) or has_sgid(mode):
        return "high"
    if is_world_writable(mode):
        return "medium"
    if is_dir and has_sticky(mode):
        return "low"
    return "low"

def scan_tree(root: Path) -> list[Finding]:
    findings: list[Finding] = []

    for p in root.rglob("*"):
        if not (p.is_file() or p.is_dir()):
            continue

        st_mode = p.stat().st_mode
        mode = st_mode & 0o7777

        if p.is_dir() and has_sticky(mode):
            findings.append(
                Finding(str(p), "sticky_dir", severity_for(mode, True))
            )

        if is_world_writable(mode):
            findings.append(
                Finding(str(p), "world_writable", severity_for(mode, p.is_dir()))
            )

        if has_suid(mode):
            findings.append(
                Finding(str(p), "suid", severity_for(mode, p.is_dir()))
            )

        if has_sgid(mode):
            findings.append(
                Finding(str(p), "sgid", severity_for(mode, p.is_dir()))
            )

    return findings
