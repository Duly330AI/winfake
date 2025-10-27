from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QFrame, QMenu, QToolButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QAction, QPen

ROOT = Path(__file__).resolve().parents[1]
WALL = ROOT / "assets" / "wallpapers" / "win10.jpg"

# Sound-Import (optional fallback)
try:
    from core.sound import SoundPlayer
    SOUND_AVAILABLE = True
except Exception:
    SOUND_AVAILABLE = False
    SoundPlayer = None

# ---------- Avatar-Helfer ----------
def _avatar(size: int, fg="#d0d0d0", use_profile=True):
    ROOT = Path(__file__).resolve().parents[1]
    PROFILE_IMG = ROOT / "assets" / "profile" / "profile.png"
    
    # Versuche Profilbild zu laden (nur wenn use_profile=True)
    if use_profile and PROFILE_IMG.exists():
        original = QPixmap(str(PROFILE_IMG))
        if not original.isNull():
            original = original.scaledToWidth(size, Qt.SmoothTransformation)
            out = QPixmap(size, size)
            out.fill(Qt.transparent)
            path = QPainterPath()
            path.addEllipse(0, 0, size, size)
            p = QPainter(out)
            p.setRenderHint(QPainter.Antialiasing, True)
            p.setClipPath(path)
            x = (size - original.width()) // 2
            y = (size - original.height()) // 2
            p.drawPixmap(x, y, original)
            p.end()
            p = QPainter(out)
            p.setRenderHint(QPainter.Antialiasing, True)
            p.setPen(QPen(QColor("#d0d0d0"), 2))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(0, 0, size-1, size-1)
            p.end()
            return out
    
    # Fallback: Graue Silhouette
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    base = QPixmap(size, size)
    base.fill(Qt.transparent)
    p = QPainter(base)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setBrush(QColor(fg))
    p.setPen(Qt.NoPen)
    r = int(size*0.44)
    x = int((size-r)/2)
    y = int(size*0.12)
    p.drawEllipse(x, y, r, r)
    p.drawRoundedRect(int(size*0.16), int(size*0.52), int(size*0.68), int(size*0.34), 22, 22)
    p.end()
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    out = QPixmap(size, size)
    out.fill(Qt.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.Antialiasing, True)
    p.setClipPath(path)
    p.drawPixmap(0, 0, base)
    p.setPen(QPen(QColor("#d0d0d0"), 2))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(0, 0, size-1, size-1)
    p.end()
    return out

# ---------- Kachel unten links (wie Win10) ----------
class TileButton(QFrame):
    clicked = Signal()
    def __init__(self, text: str, selected=False, use_profile=True, parent=None):
        super().__init__(parent)
        self._selected = selected
        self.setFixedSize(220, 56)
        self.setCursor(Qt.PointingHandCursor)
        h = QHBoxLayout(self)
        h.setContentsMargins(12, 6, 12, 6)
        h.setSpacing(12)
        self.icon = QLabel(self)
        # Nutze Profilbild nur wenn use_profile=True
        self.icon.setPixmap(_avatar(28, use_profile=use_profile))
        self.icon.setFixedSize(28, 28)
        self.lbl = QLabel(text, self)
        self.lbl.setStyleSheet("color: white; font-size: 14px;")
        h.addWidget(self.icon, 0, Qt.AlignVCenter)
        h.addWidget(self.lbl, 1, Qt.AlignVCenter)
        h.addStretch(0)
        self._apply()
    def _apply(self):
        if self._selected:
            # Windows-10 Blau
            self.setStyleSheet("""
                TileButton { background: #136fd1; border-radius: 4px; }
                TileButton > QLabel { background: transparent; }
            """)
        else:
            self.setStyleSheet("""
                TileButton { background: rgba(0,0,0,0.25); border-radius: 4px; }
                TileButton > QLabel { background: transparent; }
            """)
    def setSelected(self, sel: bool):
        self._selected = sel
        self._apply()
    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self.clicked.emit()

class LoginDialog(QDialog):
    def __init__(self, users, parent=None):
        super().__init__(parent)

        # Sound-Player initialisieren
        self.sound = SoundPlayer() if SOUND_AVAILABLE else None

        # Fenstergröße/Look
        self.setWindowTitle("Windows-Anmeldung")
        self.setFixedSize(1920, 1080)
        if WALL.exists():
            self.setStyleSheet(f"""
                QDialog {{
                    background-image: url("{WALL.as_posix().replace('\\', '/')}");
                    background-position: center;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                    background-color: #0b1e3a;
                    font-family: 'Segoe UI';
                }}
            """)
        else:
            self.setStyleSheet("QDialog{background:#0b1e3a;font-family:'Segoe UI';}")

        # Benutzer & Passwörter
        self._user_to_pwd = {u["username"]: u.get("password","") for u in users}
        self._current_user = next(iter(self._user_to_pwd.keys()), "Benutzer")

        # ===== Layout-Gerüst =====
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 32, 48, 24)
        root.setSpacing(0)
        root.addStretch(2)

        # ----- Zentrum (Avatar, Name, Passwort+Pfeil) -----
        center = QVBoxLayout()
        center.setSpacing(12)

        avatar_lbl = QLabel(self)
        avatar_lbl.setPixmap(_avatar(120, use_profile=True))
        avatar_lbl.setFixedSize(120, 120)
        avatar_lbl.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        center.addWidget(avatar_lbl, 0, Qt.AlignHCenter)

        self.user_lbl = QLabel(self._current_user, self)
        self.user_lbl.setAlignment(Qt.AlignHCenter)
        self.user_lbl.setStyleSheet("color:white;")
        self.user_lbl.setFont(QFont("Segoe UI", 28))
        center.addWidget(self.user_lbl, 0, Qt.AlignHCenter)

        # Passwortbox mit integriertem Pfeil (wie Win10)
        pw_row = QHBoxLayout()
        pw_row.setSpacing(0)
        pw_container = QFrame(self)
        pw_container.setObjectName("pwbox")
        pw_container.setStyleSheet("""
            #pwbox { 
                background: white; 
                border: 1px solid #ccc; 
                border-radius: 3px; 
            }
            #pwedit { 
                border: none; 
                padding: 8px 12px; 
                color: black; 
                font-size: 14px; 
                background: white;
                selection-background-color: #0078d4; 
            }
            #pwedit::placeholder { 
                color: #999; 
            }
            #arrow { 
                border-left: 1px solid #ddd; 
                background: white; 
                color: black; 
                font-size: 16px; 
            }
            #arrow:hover { 
                background: #f0f0f0; 
            }
        """)
        pw_container.setObjectName("pwbox")
        h = QHBoxLayout(pw_container)
        h.setContentsMargins(6,3,6,3)
        h.setSpacing(0)
        self.pw = QLineEdit(pw_container)
        self.pw.setObjectName("pwedit")
        self.pw.setEchoMode(QLineEdit.Password)
        self.pw.setPlaceholderText("Kennwort")
        self.pw.setFixedWidth(520)
        self.pw.setFixedHeight(32)
        self.pw.returnPressed.connect(self.try_login)
        arrow = QToolButton(pw_container)
        arrow.setObjectName("arrow")
        arrow.setText("➜")  # Pfeil-Ersatz; wirkt wie eingebetteter Button
        arrow.setFixedSize(40, 32)
        arrow.clicked.connect(self.try_login)
        h.addWidget(self.pw, 0, Qt.AlignVCenter)
        h.addWidget(arrow, 0, Qt.AlignVCenter)
        pw_row.addWidget(pw_container, 0, Qt.AlignHCenter)
        center.addLayout(pw_row)

        # Fehlermeldung
        self.msg = QLabel("", self)
        self.msg.setStyleSheet("color:#ffb3b3;")
        self.msg.setAlignment(Qt.AlignHCenter)
        center.addWidget(self.msg, 0, Qt.AlignHCenter)

        root.addLayout(center)
        root.addStretch(3)

        # ----- Untere Leiste: links Kacheln, rechts Systemicons -----
        bottom = QHBoxLayout()
        bottom.setContentsMargins(0,0,0,0)

        # Links: Kacheln (aktiver Nutzer + Anderer Benutzer)
        left = QVBoxLayout()
        left.setSpacing(6)
        left.setContentsMargins(0, 0, 0, 0)
        subtitle = QLabel("Anderer Benutzer:", self)
        subtitle.setStyleSheet("color:rgba(255,255,255,0.85); font-size:12px; margin:0px;")
        left.addWidget(subtitle, 0, Qt.AlignLeft)

        self.tile_current = TileButton(self._current_user, selected=True, use_profile=True, parent=self)
        self.tile_other = TileButton("Anderer Benutzer", selected=False, use_profile=False, parent=self)
        self.tile_current.clicked.connect(lambda: self._select_user(self._current_user))
        self.tile_other.clicked.connect(self._choose_other_user)
        left.addWidget(self.tile_current, 0, Qt.AlignLeft)
        left.addWidget(self.tile_other, 0, Qt.AlignLeft)
        left.addStretch(0)
        bottom.addLayout(left, 0)

        # Rechts: Netzwerk / Ease / Power
        right = QHBoxLayout()
        right.setSpacing(8)
        def sysbtn(txt, tooltip, callback):
            b = QToolButton(self)
            b.setText(txt)
            b.setToolTip(tooltip)
            b.setFixedSize(36, 36)
            b.setStyleSheet("""
                QToolButton { color:white; background:rgba(0,0,0,0.35); border-radius:4px; }
                QToolButton:hover { background:rgba(255,255,255,0.12); }
            """)
            if callback:
                b.clicked.connect(callback)
            return b
        btn_net = sysbtn("🖧", "Netzwerk", self._creepy_network)
        btn_acc = sysbtn("♿", "Erleichterte Bedienung", self._creepy_accessibility)
        btn_pwr = sysbtn("⏻", "Ein/Aus", self._creepy_power)
        right.addWidget(btn_net)
        right.addWidget(btn_acc)
        right.addWidget(btn_pwr)
        bottom.addLayout(right, 0)

        root.addLayout(bottom)

        # Fokus
        self.pw.setFocus()

    # ---- Logik ----
    def _select_user(self, name: str):
        self._current_user = name
        self.user_lbl.setText(name)
        self.tile_current.lbl.setText(name)
        self.tile_current.setSelected(True)
        self.tile_other.setSelected(False)
        self.msg.clear()
        self.pw.clear()

    def _choose_other_user(self):
        menu = QMenu(self)
        # alle Nutzer anbieten, außer aktuellem
        for uname in self._user_to_pwd.keys():
            if uname == self._current_user:
                continue
            act = QAction(uname, menu)
            act.triggered.connect(lambda chk=False, u=uname: self._select_user(u))
            menu.addAction(act)
        if not menu.actions():
            # nur ein Nutzer vorhanden -> nichts zu wählen
            self.tile_other.setSelected(False)
            return
        # Menü unter der Kachel öffnen
        p = self.tile_other.mapToGlobal(QPoint(self.tile_other.width()//2, self.tile_other.height()))
        menu.exec(p)

    def try_login(self):
        if self._user_to_pwd.get(self._current_user, "") == self.pw.text():
            if self.sound:
                self.sound.play_unlock()
            self.accept()
        else:
            self.msg.setText("Kennwort falsch.")

    def selected_user(self):
        return self._current_user

    # ---- "Creepy" System-Button Meldungen ----
    def _creepy_network(self):
        QMessageBox.warning(self, "Netzwerk", 
            "Ihre Netzwerkaktivität wird überwacht.\n"
            "Wir wissen, wo Sie sind.")

    def _creepy_accessibility(self):
        QMessageBox.warning(self, "Erleichterte Bedienung",
            "Wir passen alles für Sie an.\n"
            "Wir passen uns allen an.")

    def _creepy_power(self):
        QMessageBox.warning(self, "Ein/Aus",
            "Der Computer schläft nie.\n"
            "Nur die Benutzer schlafen.")
        self.reject()
