from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QFileDialog, QMessageBox
from PySide6.QtCore import QTimer
from PySide6.QtGui import QTextCursor, QShortcut
from PySide6.QtGui import QKeySequence
from datetime import datetime

SANDBOX = Path(__file__).resolve().parents[1] / "sandbox"
SANDBOX.mkdir(parents=True, exist_ok=True)
SYSTEMLOG = SANDBOX / "systemlog.txt"

# Sound-Import
try:
    from core.sound import SoundPlayer
    SOUND_AVAILABLE = True
except Exception:
    SOUND_AVAILABLE = False
    SoundPlayer = None

class NotepadWidget(QWidget):
    def __init__(self, session=None, parent=None):
        super().__init__(parent)
        self.session = session
        self.sound = SoundPlayer() if SOUND_AVAILABLE else None
        self.close_attempts = 0
        self.manipulation_triggered = False
        
        v = QVBoxLayout(self)
        
        # Text-Editor
        self.edit = QPlainTextEdit(self)
        self.edit.setStyleSheet("""
            QPlainTextEdit {
                background: #ffffff;
                color: #000000;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                border: none;
            }
        """)
        v.addWidget(self.edit, 1)
        
        # No bottom buttons: Notepad uses standard window chrome. Provide keyboard
        # shortcuts for New/Open/Save to keep functionality.
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.new_file)
        QShortcut(QKeySequence("Ctrl+O"), self, activated=self.load_file)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self.save_file)
        
        # Autoload systemlog.txt
        self._autoload_systemlog()
        
        # Timer für Manipulation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._manipulate_text)
        self.timer.start(5000)  # Nach 5 Sekunden starten
        
    def _autoload_systemlog(self):
        """Lade oder erstelle systemlog.txt mit initialen Logs"""
        # Erstelle IMMER frischen Inhalt (keine alten Zustände laden)
        initial_log = f"""[INFO] Sitzung gestartet: {datetime.now().strftime('%H:%M')}
[INFO] Benutzer: {self.session.current_user if self.session else 'Unknown'}
[INFO] Umgebung: stabil
"""
        # Setze frischen Inhalt
        self.edit.setPlainText(initial_log)
        
        # Speichere als neuen Ausgangspunkt
        SANDBOX.mkdir(parents=True, exist_ok=True)
        SYSTEMLOG.write_text(initial_log, encoding='utf-8')
    
    def _manipulate_text(self):
        """Manipuliere Text basierend auf Zeit und Benutzer - volle FeatureNodepad Implementation"""
        if self.manipulation_triggered:
            return
        
        text = self.edit.toPlainText()
        
        # Phase 1: stabil → instabil
        if "[INFO] Umgebung: stabil" in text:
            text = text.replace(
                "[INFO] Umgebung: stabil",
                "[WARN] Umgebung: instabil"
            )
            self.edit.setPlainText(text)
            QTimer.singleShot(2000, self._phase2_manipulation)
            return
        
    def _phase2_manipulation(self):
        """Phase 2: instabil → nicht vertrauenswürdig"""
        text = self.edit.toPlainText()
        
        if "[WARN] Umgebung: instabil" in text:
            text = text.replace(
                "[WARN] Umgebung: instabil",
                "[ERROR] Umgebung: nicht vertrauenswürdig"
            )
            self.edit.setPlainText(text)
            self._trigger_glitch()
            
            # Username-Trigger für Milan
            if self.session and self.session.current_user == "Milan":
                QTimer.singleShot(1000, self._username_trigger)
            
            # Suggestive Phrasen nach 5 Sekunden
            QTimer.singleShot(5000, self._suggestive_trigger)
            
            self.manipulation_triggered = True
    
    def _username_trigger(self):
        """Spezielle Reaktion wenn Benutzer 'Milan' ist"""
        text = self.edit.toPlainText()
        trigger_text = """
        [INFO] Willkommen zurück, Milan.
        [INFO] Letzter Zugriff: 03:33 Uhr
        [INFO] Beobachtung fortgesetzt."""

        new_text = text + trigger_text
        self.edit.setPlainText(new_text)
        
        # Sound abspielen wenn "Beobachtung" erwähnt wird
        if self.sound:
            try:
                # observer.wav spielen (falls vorhanden)
                from core.sound import ROOT
                observer_sound = ROOT / "assets" / "sfx" / "observer.wav"
                if observer_sound.exists():
                    self.sound.play("observer")
            except Exception:
                pass
    
    def _suggestive_trigger(self):
        """Füge suggestive Phrasen hinzu"""
        text = self.edit.toPlainText()
        trigger = """
[INFO] Du hast dich erneut eingeloggt.
[INFO] Du weißt, dass das nicht empfohlen wurde."""
        
        self.edit.setPlainText(text + trigger)
    
    def _trigger_glitch(self):
        """Visuelle Glitch-Effekte - Cursor springt, Text blinkt"""
        # Cursor springt zu zufälliger Position
        cursor = self.edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.edit.setTextCursor(cursor)
        
        # Text-Inversion (schnelles Blinken) - mit Windows-Farben
        original_style = self.edit.styleSheet()
        
        def invert():
            self.edit.setStyleSheet("""
                QPlainTextEdit {
                    background: #000000;
                    color: #ffffff;
                    font-family: 'Consolas', 'Courier New', monospace;
                    font-size: 11px;
                    border: none;
                }
            """)
        
        def restore():
            self.edit.setStyleSheet(original_style)
        
        QTimer.singleShot(50, invert)
        QTimer.singleShot(150, restore)
        QTimer.singleShot(200, invert)
        QTimer.singleShot(300, restore)
    
    def new_file(self):
        self.edit.setPlainText("")
        self.manipulation_triggered = False
        self.timer.start(5000)
    
    def save_file(self):
        fn, _ = QFileDialog.getSaveFileName(
            self, "Datei speichern", str(SANDBOX / "note.txt"), "Text (*.txt)"
        )
        if fn:
            try:
                with open(fn, "w", encoding="utf-8") as f:
                    f.write(self.edit.toPlainText())
                QMessageBox.information(self, "Gespeichert", f"Datei gespeichert:\n{fn}")
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Fehler beim Speichern: {e}")
    
    def load_file(self):
        fn, _ = QFileDialog.getOpenFileName(
            self, "Datei öffnen", str(SANDBOX), "Text (*.txt)"
        )
        if fn:
            try:
                with open(fn, "r", encoding="utf-8") as f:
                    self.edit.setPlainText(f.read())
                self.manipulation_triggered = False
                self.timer.start(5000)
            except Exception as e:
                QMessageBox.warning(self, "Fehler", f"Fehler beim Öffnen: {e}")
    
    def close_window(self):
        """Legacy helper: call close() to trigger closeEvent logic."""
        self.close()

    def closeEvent(self, event):
        """Intercept window-close [X]. Block exit until 3 attempts have been made.
        On each blocked attempt we append an info line and play the logoff sound (if available).
        After the 3rd attempt we save and accept the event.
        """
        # increment attempts and decide
        self.close_attempts += 1
        if self.close_attempts < 3:
            # block and inform the user
            text = self.edit.toPlainText()
            blocking_msg = "\n[INFO] Beenden nicht möglich. Sitzung läuft."
            self.edit.setPlainText(text + blocking_msg)
            # try play sound
            if self.sound:
                try:
                    self.sound.play_logoff()
                except Exception:
                    pass
            event.ignore()
        else:
            # final close: stop timers, save and accept
            try:
                self.timer.stop()
            except Exception:
                pass
            try:
                with open(SYSTEMLOG, 'w', encoding='utf-8') as f:
                    f.write(self.edit.toPlainText())
            except Exception:
                pass
            event.accept()

