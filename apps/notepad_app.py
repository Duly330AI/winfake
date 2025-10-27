from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton, QFileDialog, QMessageBox

SANDBOX = Path(__file__).resolve().parents[1] / "sandbox"; SANDBOX.mkdir(parents=True, exist_ok=True)

class NotepadWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self)
        self.edit = QPlainTextEdit(self); v.addWidget(self.edit, 1)
        row = QHBoxLayout()
        newb = QPushButton("Neu"); openb = QPushButton("Öffnen..."); saveb = QPushButton("Speichern")
        row.addWidget(newb); row.addStretch(1); row.addWidget(openb); row.addWidget(saveb); v.addLayout(row)
        newb.clicked.connect(lambda: self.edit.setPlainText(""))
        openb.clicked.connect(self.load_file)
        saveb.clicked.connect(self.save_file)

    def save_file(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Datei speichern", str(SANDBOX / "note.txt"), "Text (*.txt)")
        if fn:
            with open(fn, "w", encoding="utf-8") as f: f.write(self.edit.toPlainText())
            QMessageBox.information(self, "Gespeichert", fn)

    def load_file(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Datei öffnen", str(SANDBOX), "Text (*.txt)")
        if fn:
            with open(fn, "r", encoding="utf-8") as f: self.edit.setPlainText(f.read())
