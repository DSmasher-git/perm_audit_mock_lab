# Permission Audit (Linux) — Mocking/monkeypatch Lab (Python + Git)

Вы научитесь:
- писать unit-тесты для функций обработки прав (mode bits)
- тестировать "системную" функцию scan_tree() без реальной файловой системы
- использовать pytest monkeypatch (подмена rglob/stat/is_file/is_dir)
- вести работу через Git (ветка, коммиты, merge, tag)

Запуск тестов (самый надёжный способ):
    python -m pytest -q
