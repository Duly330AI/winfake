from pathlib import Path
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl

ROOT = Path(__file__).resolve().parents[1]
SFX_DIR = ROOT / "assets" / "sfx"

class SoundPlayer:
    def __init__(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(80)

    def play(self, sound_name: str):
        """Spiele einen Sound aus dem sfx-Verzeichnis"""
        sound_path = SFX_DIR / f"{sound_name}.wav"
        if not sound_path.exists():
            print(f"⚠ Sound nicht gefunden: {sound_path}")
            return
        
        self.player.setSource(QUrl.fromLocalFile(str(sound_path)))
        self.player.play()

    def play_logon(self):
        self.play("Windows Logon")

    def play_unlock(self):
        self.play("Windows Unlock")

    def play_logoff(self):
        self.play("Windows Logoff Sound")

    def play_startup(self):
        self.play("Windows Startup")
