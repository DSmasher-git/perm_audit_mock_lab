import os
import stat as statmod
from pathlib import Path

from src.perm_audit import (
    is_world_writable,
    has_suid,
    has_sgid,
    has_sticky,
    severity_for,
    scan_tree,
)



def test_world_writable_true():
    assert is_world_writable(0o666) is True


def test_world_writable_false():
    assert is_world_writable(0o644) is False


def test_suid_sgid_sticky_bits():
    assert has_suid(0o4755) is True
    assert has_sgid(0o2755) is True
    assert has_sticky(0o1777) is True


def test_severity_critical_when_suid_and_world_writable():
    assert severity_for(0o4777, is_dir=False) == "critical"



def test_scan_tree_with_monkeypatch(monkeypatch):
    root = Path("/FAKE_ROOT")

    fake_paths = [
        Path("/FAKE_ROOT/world.txt"),
        Path("/FAKE_ROOT/suidbin"),
        Path("/FAKE_ROOT/tmpdir"),
    ]

    monkeypatch.setattr(Path, "rglob", lambda self, pattern: fake_paths)

    def fake_is_file(self):
        return self.name in {"world.txt", "suidbin"}

    def fake_is_dir(self):
        return self.name == "tmpdir"

    monkeypatch.setattr(Path, "is_file", fake_is_file)
    monkeypatch.setattr(Path, "is_dir", fake_is_dir)

    modes = {
        "/FAKE_ROOT/world.txt": statmod.S_IFREG | 0o666,
        "/FAKE_ROOT/suidbin":   statmod.S_IFREG | 0o4755,
        "/FAKE_ROOT/tmpdir":    statmod.S_IFDIR | 0o1777,
    }

    original_stat = Path.stat

    def fake_stat(self, *args, **kwargs):
        key = str(self).replace("\\", "/")

        if key in modes:
            m = modes[key]
            return os.stat_result((m, 0, 0, 0, 0, 0, 0, 0, 0, 0))

        return original_stat(self, *args, **kwargs)

    monkeypatch.setattr(Path, "stat", fake_stat)

    findings = scan_tree(root)

    kinds = {(f.path.replace("\\", "/"), f.kind) for f in findings}

    assert ("/FAKE_ROOT/world.txt", "world_writable") in kinds
    assert ("/FAKE_ROOT/suidbin", "suid") in kinds
    assert ("/FAKE_ROOT/tmpdir", "sticky_dir") in kinds
