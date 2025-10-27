from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMdiArea, QMdiSubWindow, QMenu
from PySide6.QtCore import Qt, QTimer, QTime
from PySide6.QtGui import QKeySequence, QShortcut
from core.session import Session
from apps.notepad_app import NotepadWidget
from apps.fake_browser_app import FakeBrowserWidget
from apps.paint_app import PaintWidget

# Sound-Import (optional fallback)
try:
    from core.sound import SoundPlayer
    SOUND_AVAILABLE = True
except Exception:
    SOUND_AVAILABLE = False
    SoundPlayer = None

class DesktopWindow(QMainWindow):
    def __init__(self, session: Session, parent=None):
        super().__init__(parent)
        self.session = session
        self.sound = SoundPlayer() if SOUND_AVAILABLE else None
        self.setWindowTitle(f"Desktop - {session.current_user}")
        self.resize(1600, 900)

        QShortcut(QKeySequence("Escape"), self, activated=self.close)

        central = QWidget(self); v = QVBoxLayout(central); v.setContentsMargins(0,0,0,0); v.setSpacing(0)
        self.mdi = QMdiArea(self); v.addWidget(self.mdi, 1)
        v.addWidget(self._taskbar(), 0)
        self.setCentralWidget(central)

    def _taskbar(self):
        bar = QFrame(self); bar.setFixedHeight(44)
        h = QHBoxLayout(bar); h.setContentsMargins(8,4,8,4); h.setSpacing(8)

        start = QPushButton("Start")
        menu = QMenu(self)
        menu.addAction("Notepad.exe", self.open_notepad)
        menu.addAction("Google.exe", self.open_browser)
        menu.addAction("Paint.exe", self.open_paint)
        menu.addSeparator()
        menu.addAction("Abmelden", self.close)
        menu.addAction("Beenden", self.close)
        start.setMenu(menu)
        h.addWidget(start)

        btn1 = QPushButton("Notepad.exe"); btn1.clicked.connect(self.open_notepad); h.addWidget(btn1)
        btn2 = QPushButton("Google.exe"); btn2.clicked.connect(self.open_browser); h.addWidget(btn2)
        btn3 = QPushButton("Paint.exe"); btn3.clicked.connect(self.open_paint); h.addWidget(btn3)

        h.addStretch(1)
        self.clock = QLabel("--:--"); h.addWidget(self.clock, 0, Qt.AlignRight)
        t = QTimer(bar); t.timeout.connect(lambda: self.clock.setText(QTime.currentTime().toString("HH:mm"))); t.start(1000)
        return bar

    def _open(self, widget_cls, title):
        w = widget_cls(parent=self)
        sub = QMdiSubWindow(self.mdi); sub.setWidget(w); sub.setAttribute(Qt.WA_DeleteOnClose); sub.setWindowTitle(title)
        self.mdi.addSubWindow(sub); sub.resize(800, 520); sub.show(); w.setFocus()

    def open_notepad(self): self._open(NotepadWidget, "Notepad.exe (Demo)")
    def open_browser(self): self._open(FakeBrowserWidget, "Google.exe (Demo)")
    def open_paint(self):   self._open(PaintWidget, "Paint.exe (Demo)")
