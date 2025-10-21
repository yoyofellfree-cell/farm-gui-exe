import sys, json, os
from pathlib import Path
from PySide6 import QtCore, QtWidgets, QtGui

BASE_DIR = Path(__file__).resolve().parent
TASKS_FILE = BASE_DIR / "tasks.json"

class TaskItem(QtWidgets.QWidget):
    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setContentsMargins(6,4,6,4)
        self.checkbox = QtWidgets.QCheckBox(task["title"] + f" ({task['bp']})")
        self.checkbox.setChecked(task.get("checked", False))
        self.layout.addWidget(self.checkbox)
        self.layout.addStretch()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Калькулятор фарма BP")
        self.resize(900,700)
        self.load_tasks()
        self.setup_ui()
        self.apply_styles()

    def load_tasks(self):
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                self.tasks = json.load(f)
        except Exception:
            self.tasks = []

    def setup_ui(self):
        central = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(central)
        # header
        header = QtWidgets.QWidget()
        h_layout = QtWidgets.QVBoxLayout(header)
        label_today = QtWidgets.QLabel("Сегодня: <b>0 BP</b>")
        label_done = QtWidgets.QLabel("Выполнено 0/0")
        label_total = QtWidgets.QLabel("Всего: <b>0 BP</b>")
        label_today.setAlignment(QtCore.Qt.AlignHCenter)
        label_total.setAlignment(QtCore.Qt.AlignHCenter)
        label_done.setAlignment(QtCore.Qt.AlignHCenter)
        font = label_today.font(); font.setPointSize(14); label_today.setFont(font)
        h_layout.addWidget(label_today)
        h_layout.addWidget(label_done)
        h_layout.addWidget(label_total)
        v.addWidget(header)

        # tabs
        self.tabs = QtWidgets.QTabWidget()
        self.tab_widgets = {}
        for tab in ["Одиночные","Парные","Гос","Крайм"]:
            w = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(w)
            scroll = QtWidgets.QScrollArea()
            scroll.setWidgetResizable(True)
            container = QtWidgets.QWidget()
            container_layout = QtWidgets.QVBoxLayout(container)
            container_layout.setAlignment(QtCore.Qt.AlignTop)
            # populate tasks for this tab
            for t in self.tasks:
                if t.get("tab") == tab:
                    item = TaskItem(t)
                    item.checkbox.stateChanged.connect(self.on_check_changed)
                    container_layout.addWidget(item)
            scroll.setWidget(container)
            layout.addWidget(scroll)
            self.tabs.addTab(w, tab)
            self.tab_widgets[tab] = container

        v.addWidget(self.tabs, 1)

        # footer controls
        footer = QtWidgets.QWidget()
        f_layout = QtWidgets.QHBoxLayout(footer)
        self.reset_btn = QtWidgets.QPushButton("Сбросить прогресс")
        self.export_btn = QtWidgets.QPushButton("Экспорт CSV")
        f_layout.addWidget(self.reset_btn)
        f_layout.addStretch()
        f_layout.addWidget(self.export_btn)
        v.addWidget(footer)

        self.setCentralWidget(central)

        # connections
        self.reset_btn.clicked.connect(self.reset_progress)
        self.export_btn.clicked.connect(self.export_csv)

        self.label_today = label_today
        self.label_done = label_done
        self.label_total = label_total
        self.update_counts()

    def on_check_changed(self):
        self.update_counts()

    def update_counts(self):
        total_bp = 0
        today_bp = 0
        checked_count = 0
        total_items = 0
        for tab_index in range(self.tabs.count()):
            tab_widget = self.tabs.widget(tab_index)
            # find checkboxes
            checkboxes = tab_widget.findChildren(QtWidgets.QCheckBox)
            for cb in checkboxes:
                total_items += 1
                # parse bp from label end "(n)"
                text = cb.text()
                m = text.strip().rsplit("(",1)
                bp = 0
                if len(m)==2 and m[1].endswith(")"):
                    try:
                        bp = int(m[1][:-1])
                    except:
                        bp = 0
                total_bp += bp
                if cb.isChecked():
                    checked_count += 1
                    today_bp += bp
        self.label_today.setText(f"Сегодня: <b>{today_bp} BP</b>")
        self.label_total.setText(f"Всего: <b>{total_bp} BP</b>")
        self.label_done.setText(f"Выполнено {checked_count}/{total_items}")

    def reset_progress(self):
        for tab_index in range(self.tabs.count()):
            tab_widget = self.tabs.widget(tab_index)
            checkboxes = tab_widget.findChildren(QtWidgets.QCheckBox)
            for cb in checkboxes:
                cb.setChecked(False)
        self.update_counts()

    def export_csv(self):
        # create simple CSV with title,bp,checked
        import csv
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Сохранить CSV", "farm_progress.csv", "CSV Files (*.csv)")
        if not path: return
        rows = [["title","bp","checked"]]
        for tab_index in range(self.tabs.count()):
            tab_widget = self.tabs.widget(tab_index)
            checkboxes = tab_widget.findChildren(QtWidgets.QCheckBox)
            for cb in checkboxes:
                text = cb.text()
                title = text.rsplit("(",1)[0].strip()
                bp = 0
                if "(" in text and text.endswith(")"):
                    try:
                        bp = int(text.rsplit("(",1)[1][:-1])
                    except: bp = 0
                rows.append([title,str(bp), "1" if cb.isChecked() else "0"])
        try:
            with open(path, "w", encoding="utf-8", newline='') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            QtWidgets.QMessageBox.information(self, "Экспорт", "CSV сохранён")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", str(e))

    def apply_styles(self):
        # dark theme + styling similar to screenshot
        style = """
        QWidget { background: #0f1115; color: #d6e0ea; font-family: Segoe UI, Arial; }
        QTabWidget::pane { border: none; }
        QTabBar::tab { background: #18202a; border: 1px solid #2b3440; padding: 8px 14px; margin: 2px; border-radius: 4px; }
        QTabBar::tab:selected { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #243040, stop:1 #1b2430); color: #fff; }
        QCheckBox { background: #2a2f36; padding:6px; border-radius:4px; }
        QPushButton { background: #2b3b45; padding:8px 12px; border-radius:6px; }
        QPushButton:hover { background: #3c4b55; }
        QScrollArea { background: transparent; }
        """
        self.setStyleSheet(style)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__=="__main__":
    main()
