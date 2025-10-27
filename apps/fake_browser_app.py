from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem

DEMO = [
    "Result 1 – lokal generiert",
    "Result 2 – kein echtes Internet",
    "Result 3 – just for fun",
    "Result 4 – Tabs/Verlauf später"
]

class FakeBrowserWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self)
        row = QHBoxLayout()
        self.q = QLineEdit(self); self.q.setPlaceholderText("Suchbegriff")
        go = QPushButton("Suchen"); go.clicked.connect(self.search)
        row.addWidget(self.q, 1); row.addWidget(go)
        v.addLayout(row)
        self.list = QListWidget(self); v.addWidget(self.list, 1)
        self.q.returnPressed.connect(self.search)

    def search(self):
        text = (self.q.text() or "").strip()
        self.list.clear()
        if not text: return
        for base in DEMO:
            self.list.addItem(QListWidgetItem(f"{base} — Query: {text}"))
