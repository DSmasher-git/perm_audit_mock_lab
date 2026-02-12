# Практическая работа (90 минут) — Linux (bash)
## Тема: Mocking/monkeypatch — тестируем аудит прав доступа без реальной ФС

### 0–10 мин: старт + Git
1) Распакуй архив, открой папку проекта:
```bash
cd perm_audit_mock_lab
```
2) Инициализируй Git и сделай первый коммит:
```bash
git init
git add .
git commit -m "init: starter project"
```

### 10–15 мин: установка pytest
```bash
python3 -m pip install --user pytest
```

### 15–20 мин: отдельная ветка под тесты
```bash
git switch -c test/mock
```

### 20–30 мин: первый запуск тестов (они должны упасть)
```bash
python3 -m pytest -q
```

### 30–60 мин: исправь код (src/perm_audit.py)
Цель: чтобы все тесты стали зелёными.
Подсказки:
- В функции has_sticky() сейчас ошибка.
- В scan_tree() сейчас НЕ добавляется finding "sticky_dir", хотя тест этого ждёт.
После каждого изменения запускай:
```bash
python3 -m pytest -q
```

### 60–75 мин: допиши 2 теста (TODO в tests/test_perm_audit.py)
- тест на has_sgid()
- тест на severity_for() для критического случая (SUID/SGID + world-writable)

### 75–85 мин: Git-оформление
Делай коммиты после каждого логического шага:
```bash
git add -A
git commit -m "fix: ..."
```

### 85–90 мин: merge + tag + отчёт
1) Merge ветки в main/master:
```bash
git switch main 2>/dev/null || git switch master
git merge test/mock
```
2) Tag:
```bash
git tag v0.3
```
3) Заполни REPORT.md и закоммить:
```bash
git add REPORT.md
git commit -m "docs: add report"
```

### Что показать преподавателю
```bash
python3 -m pytest -q
git log --oneline --decorate --graph --all
git tag
```
