from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    path: str
    kind: str          # world_writable | suid | sgid | sticky_dir
    severity: str      # low | medium | high | critical


def is_world_writable(mode: int) -> bool:
    """True если others имеют право записи."""
    return bool(mode & 0o002)


def has_suid(mode: int) -> bool:
    return bool(mode & 0o4000)


def has_sgid(mode: int) -> bool:
    return bool(mode & 0o2000)


def has_sticky(mode: int) -> bool:
    # TODO: здесь специально ошибка (для лабы). Sticky bit = 0o1000
    return bool(mode & 0o0100)


def severity_for(mode: int, is_dir: bool) -> str:
    """Учебная шкала серьёзности."""
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
    """Сканирует дерево root.
    Важно: трогает ОС (rglob/stat/is_file/is_dir). Тестируем через monkeypatch.
    """
    findings: list[Finding] = []

    for p in root.rglob("*"):
        if not (p.is_file() or p.is_dir()):
            continue

        st_mode = p.stat().st_mode
        mode = st_mode & 0o7777

        # TODO: сейчас sticky_dir не добавляется — тест должен поймать.
        # Исправь: если p — директория и sticky включён -> добавить Finding(..., "sticky_dir", ...)
        # if p.is_dir() and has_sticky(mode):
        #     findings.append(Finding(str(p), "sticky_dir", severity_for(mode, True)))

        if is_world_writable(mode):
            findings.append(Finding(str(p), "world_writable", severity_for(mode, p.is_dir())))

        if has_suid(mode):
            findings.append(Finding(str(p), "suid", severity_for(mode, p.is_dir())))

        if has_sgid(mode):
            findings.append(Finding(str(p), "sgid", severity_for(mode, p.is_dir())))

    return findings
