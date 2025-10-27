from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import Qt, QPoint

class PaintWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.stage = 0
        self.layers = [QPixmap(800, 480) for _ in range(3)]
        # Fallback: leere Stages mit einfachen Markierungen (später echte PNG-Layer aus assets/brushes laden)
        for i, pm in enumerate(self.layers):
            pm.fill(Qt.transparent)
            p = QPainter(pm); p.setPen(Qt.black); p.drawText(20, 40, f"Stage {i+1}"); p.end()

        v = QVBoxLayout(self)
        self.canvas = QLabel(self); self.canvas.setFixedSize(780, 460); v.addWidget(self.canvas, 0, Qt.AlignCenter)
        self._render()

    def _render(self):
        # Kombiniere Stages bis current stage
        out = QPixmap(780, 460); out.fill(Qt.white)
        p = QPainter(out)
        for i in range(self.stage + 1):
            p.drawPixmap(0, 0, self.layers[i].scaled(out.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        p.end()
        self.canvas.setPixmap(out)

    def mousePressEvent(self, ev): self._advance()
    def mouseMoveEvent(self, ev):  self._advance()

    def _advance(self):
        self.stage = min(self.stage + 1, len(self.layers)-1)
        self._render()
