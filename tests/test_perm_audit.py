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


def test_suid_bit():
    assert has_suid(0o4755) is True


def test_sticky_bit():
    # Должно быть True для 0o1777 (как /tmp)
    assert has_sticky(0o1777) is True


def test_scan_tree_with_monkeypatch(monkeypatch):
    root = Path("/FAKE_ROOT")

    fake_paths = [
        Path("/FAKE_ROOT/world.txt"),
        Path("/FAKE_ROOT/suidbin"),
        Path("/FAKE_ROOT/tmpdir"),
    ]

    # 1) подменяем rglob: возвращаем заранее заданные пути
    monkeypatch.setattr(Path, "rglob", lambda self, pattern: fake_paths)

    # 2) подменяем is_file/is_dir
    def fake_is_file(self):
        return self.name in {"world.txt", "suidbin"}

    def fake_is_dir(self):
        return self.name == "tmpdir"

    monkeypatch.setattr(Path, "is_file", fake_is_file)
    monkeypatch.setattr(Path, "is_dir", fake_is_dir)

    # 3) подменяем stat(): отдаём режимы для каждого пути
    modes = {
        "/FAKE_ROOT/world.txt": statmod.S_IFREG | 0o666,   # world-writable file
        "/FAKE_ROOT/suidbin":   statmod.S_IFREG | 0o4755,  # SUID file
        "/FAKE_ROOT/tmpdir":    statmod.S_IFDIR | 0o1777,  # sticky dir
    }

    def fake_stat(self):
        m = modes[str(self)]
        return os.stat_result((m, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    monkeypatch.setattr(Path, "stat", fake_stat)

    findings = scan_tree(root)

    kinds = {(f.path, f.kind) for f in findings}
    assert ("/FAKE_ROOT/world.txt", "world_writable") in kinds
    assert ("/FAKE_ROOT/suidbin", "suid") in kinds

    # ВАЖНО: sticky_dir должен появиться после того, как студент исправит код
    assert ("/FAKE_ROOT/tmpdir", "sticky_dir") in kinds


# TODO (дописать студенту):
# 1) test_sgid_bit() -> проверить, что has_sgid(0o2755) == True
# 2) test_severity_critical() -> severity_for(0o4777, is_dir=False) == "critical"
