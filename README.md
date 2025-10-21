Проект: Калькулятор фарма BP (PySide6)
--------------------
В комплекте:
- main.py       (приложение PySide6)
- tasks.json    (задачи и BP)
- requirements.txt
- .github_workflows/build-windows.yml (workflow для GitHub Actions - сохраните в .github/workflows/)

Как собрать .exe без установки на ПК:
1) Создайте репозиторий на GitHub.
2) Загрузите все файлы из этой папки в корень репозитория.
3) Поместите содержимое .github_workflow.yml в .github/workflows/build-windows.yml
4) Push -> Actions автоматически соберёт exe (артефакт farm-exe).

Локальная сборка:
pip install -r requirements.txt pyinstaller
pyinstaller --onefile --add-data "tasks.json;." main.py
