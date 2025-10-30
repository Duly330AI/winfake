from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMdiArea, QMdiSubWindow, QToolButton, QLineEdit
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QIcon, QKeySequence, QShortcut, QPalette, QBrush
from core.session import Session
from apps.notepad_app import NotepadWidget
from apps.fake_browser_app import FakeBrowserWidget
from apps.paint_app import PaintWidget
from pathlib import Path

# Sound-Import
try:
    from core.sound import SoundPlayer
    SOUND_AVAILABLE = True
except Exception:
    SOUND_AVAILABLE = False
    SoundPlayer = None

ROOT = Path(__file__).resolve().parents[1]
WALLPAPER = ROOT / "assets" / "wallpapers" / "win10.jpg"
ICONS_DIR = ROOT / "assets" / "icons" / "applications"

class DraggableIcon(QToolButton):
    """Draggbares Desktop-Icon mit Label unten"""
    def __init__(self, icon_path, label, callback, parent=None):
        super().__init__(parent)
        self.callback = callback
        self.drag_start = None
        
        if Path(icon_path).exists():
            self.setIcon(QIcon(str(icon_path)))
        self.setIconSize(QSize(48, 48))
        self.setText(label)
        self.setFixedSize(90, 90)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setStyleSheet("""
            QToolButton {
                background: transparent;
                border: none;
                color: white;
                font-size: 10px;
                font-family: 'Segoe UI';
                font-weight: normal;
                padding: 4px;
            }
            QToolButton:hover {
                background: rgba(255,255,255,0.08);
                border-radius: 4px;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self.callback)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start = event.globalPos() - self.frameGeometry().topLeft()
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if self.drag_start and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start)
            # keep icons behind other windows/widgets
            try:
                self.lower()
            except Exception:
                pass
        super().mouseMoveEvent(event)

class DesktopArea(QWidget):
    """Desktop-Bereich mit Wallpaper und Icon-Grid"""
    def __init__(self, session: Session, parent=None):
        super().__init__(parent)
        self.session = session
        self.icons = []
        self.setAutoFillBackground(True)
        # Load wallpaper pixmap and draw it in paintEvent to avoid platform
        # painting issues where palette-based backgrounds may disappear.
        self._wallpaper = None
        if WALLPAPER.exists():
            try:
                from PySide6.QtGui import QPixmap
                self._wallpaper = QPixmap(str(WALLPAPER))
            except Exception:
                self._wallpaper = None
        if not self._wallpaper:
            self.setStyleSheet("QWidget { background-color: #0b1e3a; }")
            
    def add_icon(self, icon_widget, row, col):
        """Platziere Icon in Grid-Position"""
        icon_widget.setParent(self)
        x = 20 + col * 110
        y = 20 + row * 110
        icon_widget.move(x, y)
        icon_widget.show()
        # ensure icon stays behind top-level windows
        try:
            icon_widget.lower()
        except Exception:
            pass
        self.icons.append(icon_widget)

    def paintEvent(self, event):
        # draw wallpaper scaled to cover the widget area while keeping aspect
        if getattr(self, '_wallpaper', None):
            from PySide6.QtGui import QPainter
            painter = QPainter(self)
            pix = self._wallpaper
            w, h = self.width(), self.height()
            pw, ph = pix.width(), pix.height()
            # scale preserving aspect ratio and cover
            scale = max(w / pw, h / ph)
            new_w, new_h = int(pw * scale), int(ph * scale)
            px = (w - new_w) // 2
            py = (h - new_h) // 2
            painter.drawPixmap(px, py, new_w, new_h, pix)
            painter.end()
        else:
            super().paintEvent(event)

class DesktopWindow(QWidget):
    """Echter Windows-Desktop mit MDI und draggbaren Icons"""
    def __init__(self, session: Session, parent=None):
        super().__init__(parent)
        self.session = session
        self.sound = SoundPlayer() if SOUND_AVAILABLE else None
        self.open_windows = []  # Liste offener Top-Level-Fenster
        self.taskbar_buttons = {}  # Dict: window -> taskbar_button
        
        self.setWindowTitle(f"Desktop - {session.current_user}")
        self.resize(1600, 900)
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Stacked Layout (StackAll) für sauberes Overlay von Desktop + MDI
        from PySide6.QtWidgets import QWidget as _QWidget, QStackedLayout
        stack_container = _QWidget(self)
        stack_layout = QStackedLayout(stack_container)
        stack_layout.setStackingMode(QStackedLayout.StackAll)
        # keep references so we can change stacking order later
        self._stack_container = stack_container
        self._stack_layout = stack_layout

        # Desktop-Area als Basis-Schicht
        self.desktop = DesktopArea(session, stack_container)
        stack_layout.addWidget(self.desktop)

        # MDI-Area als obere Schicht (transparent)
        self.mdi = QMdiArea(stack_container)
        
        # WICHTIG: SubWindowView mit aktiviertem RubberBandResize
        self.mdi.setViewMode(QMdiArea.SubWindowView)
        self.mdi.setOption(QMdiArea.DontMaximizeSubWindowOnActivation, True)
        
        # Komplett transparenter Hintergrund
        self.mdi.setStyleSheet("""
            QMdiArea {
                background: transparent;
                border: none;
            }
            QMdiArea QScrollBar {
                width: 0px;
                height: 0px;
            }
        """)
        # Härtere Transparenz-Einstellungen gegen dunklen Hintergrund
        try:
            self.mdi.setAttribute(Qt.WA_TranslucentBackground, True)
        except Exception:
            pass
        self.mdi.setAutoFillBackground(False)
        try:
            pal = self.mdi.palette()
            pal.setColor(QPalette.Window, Qt.transparent)
            self.mdi.setPalette(pal)
            # some Qt styles still paint background via setBackground
            self.mdi.setBackground(QBrush(Qt.transparent))
        except Exception:
            pass
        
        # Viewport transparent
        try:
            viewport = self.mdi.viewport()
            if viewport:
                viewport.setStyleSheet("background: transparent;")
                viewport.setAttribute(Qt.WA_TranslucentBackground, True)
                viewport.setAutoFillBackground(False)
        except Exception:
            pass
        
        stack_layout.addWidget(self.mdi)

        # Beide Widgets sichtbar machen (StackAll rendert alle übereinander)
        self.mdi.setVisible(False)  # MDI initial versteckt

        # Stack-Container ins Layout
        layout.addWidget(stack_container, 1)
        
        # Taskleiste
        layout.addWidget(self._taskbar(), 0)
        
        self.setLayout(layout)
        
        # Icons hinzufügen
        self._setup_desktop_icons()
        
        # Escape zum Schließen
        QShortcut(QKeySequence("Escape"), self, activated=self.close)
        
    def _setup_desktop_icons(self):
        """Erstelle Desktop-Icons für Apps im Grid-Layout"""
        # Notepad Icon
        notepad_icon = DraggableIcon(
            str(ICONS_DIR / "notepad.ico"),
            "Notepad.exe",
            self.open_notepad,
            parent=self.desktop
        )
        self.desktop.add_icon(notepad_icon, 0, 0)
            
    def _taskbar(self):
        from PySide6.QtWidgets import QFrame, QHBoxLayout
        bar = QFrame(self)
        bar.setFixedHeight(48)
        bar.setStyleSheet("""
            QFrame {
                background: rgba(32, 32, 51, 0.95);
                border-top: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)
        
        h = QHBoxLayout(bar)
        h.setContentsMargins(8, 6, 8, 6)
        h.setSpacing(8)
        
        # Windows Start Button (echtes Style)
        win_btn = QPushButton("⊞")
        win_btn.setFixedSize(46, 36)
        win_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                font-size: 16px;
                border-radius: 4px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.08);
            }
        """)
        h.addWidget(win_btn)
        
        # Suchleiste
        search = QLineEdit()
        search.setPlaceholderText("🔍 Suchen")
        search.setFixedSize(200, 32)
        search.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 4px;
                padding: 4px 8px;
                color: rgba(255, 255, 255, 0.7);
                font-size: 10px;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
        """)
        h.addWidget(search)
        
        # Taskbar-Buttons Container (für geöffnete Fenster)
        self.taskbar_container = QHBoxLayout()
        self.taskbar_container.setSpacing(4)
        h.addLayout(self.taskbar_container)
        
        h.addStretch(1)
        
        # Netzwerk-Icon
        net_btn = QPushButton("🖧")
        net_btn.setFixedSize(36, 32)
        net_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.08);
            }
        """)
        h.addWidget(net_btn)
        
        # Sound-Icon
        sound_btn = QPushButton("🔊")
        sound_btn.setFixedSize(36, 32)
        sound_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.08);
            }
        """)
        h.addWidget(sound_btn)
        
        # Uhr mit Datum
        self.clock = QLabel("--:-- --/--/----")
        self.clock.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.85);
                font-size: 11px;
                font-family: 'Segoe UI';
            }
        """)
        self.clock.setFixedWidth(120)
        h.addWidget(self.clock, 0, Qt.AlignRight | Qt.AlignVCenter)
        
        # Timer für Uhr und Datum
        t = QTimer(bar)
        t.timeout.connect(self._update_clock)
        t.start(1000)
        self._update_clock()  # Initial update
        
        return bar
    
    def _update_clock(self):
        from datetime import datetime
        now_dt = datetime.now()
        time_str = now_dt.strftime("%H:%M")
        date_str = now_dt.strftime("%d/%m/%Y")
        self.clock.setText(f"{time_str}  {date_str}")
        
    def _open(self, widget_cls, title, session=None):
        """Öffne App als MDI-Subwindow (INNERHALB des Desktop-Fensters)"""
        # Alle Apps (inklusive Notepad) als MDI-Subwindow öffnen
        # damit sie INNERHALB des Desktop-Fensters bleiben
        
        # Mache MDI sichtbar wenn erstes Fenster geöffnet wird
        if not self.mdi.isVisible():
            self.mdi.setVisible(True)
            # Ensure MDI layer is the top of the stacked overlay
            try:
                if hasattr(self, '_stack_layout'):
                    self._stack_layout.setCurrentWidget(self.mdi)
            except Exception:
                pass
        
        if session:
            w = widget_cls(session=session)
        else:
            w = widget_cls()
        
        sub = QMdiSubWindow()
        sub.setWidget(w)
        sub.setAttribute(Qt.WA_DeleteOnClose)
        sub.setWindowTitle(title)
        
        # WICHTIG: Verhindere MDI-typische Icons beim Minimieren
        # Setze Window-Flags um System-Menu und Minimize-Button zu zeigen
        flags = sub.windowFlags()
        flags |= Qt.CustomizeWindowHint
        flags |= Qt.WindowTitleHint
        flags |= Qt.WindowSystemMenuHint
        flags |= Qt.WindowMinMaxButtonsHint
        flags |= Qt.WindowCloseButtonHint
        sub.setWindowFlags(flags)
        
        # Styles
        style_active = (
            "QPushButton {"
            " background: rgba(255,255,255,0.16);"
            " color: white;"
            " border: 1px solid rgba(255,255,255,0.25);"
            " border-radius: 6px;"
            " text-align: left; padding-left: 8px; font-size: 11px;"
            "} QPushButton:hover { background: rgba(255,255,255,0.22); }"
        )
        style_dimmed = (
            "QPushButton {"
            " background: rgba(255,255,255,0.06);"
            " color: rgba(255,255,255,0.7);"
            " border: 1px solid rgba(255,255,255,0.12);"
            " border-radius: 6px;"
            " text-align: left; padding-left: 8px; font-size: 11px;"
            "} QPushButton:hover { background: rgba(255,255,255,0.12); }"
        )

        # Taskbar-Button erstellen (mit App-Icon)
        taskbar_btn = QPushButton(title[:24])
        taskbar_btn.setFixedSize(180, 36)
        # Icon ermitteln
        try:
            app_icon = QIcon()
            if widget_cls.__name__ == 'NotepadWidget':
                app_icon = QIcon(str(ICONS_DIR / 'notepad.ico'))
            taskbar_btn.setIcon(app_icon)
            taskbar_btn.setIconSize(QSize(16, 16))
        except Exception:
            pass
        taskbar_btn.setStyleSheet(style_active)
        
        # Button-Funktionen
        def toggle_window():
            if sub.isVisible():
                # Fenster verstecken (wie Windows Minimize)
                sub.hide()
                taskbar_btn.setStyleSheet(style_dimmed)
            else:
                # Fenster wiederherstellen
                sub.show()
                sub.raise_()
                sub.activateWindow()
                taskbar_btn.setStyleSheet(style_active)
        
        # Event Filter um Minimize abzufangen (QMdiSubWindow nutzt Events nicht Signals)
        from PySide6.QtCore import QEvent, QObject
        
        class MinimizeFilter(QObject):
            def __init__(self, subwin, btn):
                super().__init__()
                self.subwin = subwin
                self.btn = btn
            
            def eventFilter(self, obj, event):
                if event.type() == QEvent.WindowStateChange:
                    if self.subwin.windowState() & Qt.WindowMinimized:
                        # Verhindere Minimierung, verstecke stattdessen
                        self.subwin.hide()
                        self.subwin.setWindowState(Qt.WindowNoState)
                        # Dim button
                        self.btn.setStyleSheet(style_dimmed)
                        return True  # Event handled
                # Sichtbarkeit
                if event.type() == QEvent.Hide:
                    self.btn.setStyleSheet(style_dimmed)
                elif event.type() == QEvent.Show:
                    self.btn.setStyleSheet(style_active)
                return super().eventFilter(obj, event)
        
        minimize_filter = MinimizeFilter(sub, taskbar_btn)
        sub.installEventFilter(minimize_filter)
        # Keep reference so it doesn't get garbage collected
        sub._minimize_filter = minimize_filter
        
        def remove_taskbar_button():
            if sub in self.taskbar_buttons:
                btn = self.taskbar_buttons[sub]
                self.taskbar_container.removeWidget(btn)
                btn.deleteLater()
                del self.taskbar_buttons[sub]
            
            # MDI verstecken wenn keine Fenster mehr offen (mit Safety Check)
            try:
                if hasattr(self, 'mdi') and self.mdi and len(self.mdi.subWindowList()) == 0:
                    self.mdi.setVisible(False)
                    # Switch stacked overlay back to desktop only
                    try:
                        if hasattr(self, '_stack_layout'):
                            self._stack_layout.setCurrentWidget(self.desktop)
                    except Exception:
                        pass
            except RuntimeError:
                # MDI already deleted, ignore
                pass
        
        taskbar_btn.clicked.connect(toggle_window)
        sub.destroyed.connect(remove_taskbar_button)
        
        # Update Button-Styles anhand aktiven Subfensters
        try:
            def update_active(active_sub):
                for sw, btn in list(self.taskbar_buttons.items()):
                    btn.setStyleSheet(style_active if sw is active_sub and sw.isVisible() else style_dimmed)
            self.mdi.subWindowActivated.connect(update_active)
        except Exception:
            pass
        
        # Button zur Taskleiste hinzufügen
        self.taskbar_container.addWidget(taskbar_btn)
        self.taskbar_buttons[sub] = taskbar_btn
        
        self.mdi.addSubWindow(sub)
        sub.resize(800, 520)
        sub.show()
        w.setFocus()
        
    def open_notepad(self):
        self._open(NotepadWidget, "Notepad.exe", self.session)
        
    def open_browser(self):
        self._open(FakeBrowserWidget, "Google.exe (Demo)")
        
    def open_paint(self):
        self._open(PaintWidget, "Paint.exe (Demo)")

    def resizeEvent(self, event):
        # QStackedWidget handled layout automatisch - kein manuelles resize nötig
        return super().resizeEvent(event)
