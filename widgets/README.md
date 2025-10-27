# Widgets Module

## LoginDialog (`login_dialog.py`)

Professioneller Windows-10 Login-Dialog mit folgenden Komponenten:

### Hauptkomponenten

#### Avatar-System (`_avatar()`)
- Lädt Profilbild aus `assets/profile/profile.png`
- Zirkulärer Crop (kein Quadrat!)
- Größen: 120px (zentral) + 28px (Kacheln)
- Fallback: Graue Silhouette wenn kein Bild vorhanden
- Parameter `use_profile`: True = Profilbild laden, False = nur Silhouette

#### TileButton-Klasse
- Benutzer-Kacheln (220×56px)
- Icon + Benutzername
- Aktiv-Status mit Windows-Blau (#136fd1)
- Hover-Effekte
- Parameter: `text`, `selected`, `use_profile`

#### LoginDialog-Klasse
- Fenster: 1920×1080px (Vollbild)
- Hintergrund: Dunkles Blau (#0b1e3a) + optionales Wallpaper
- Passwortfeld: Weiß, hochgradig lesbar
- Pfeil-Button (➜) zum Login
- Benutzer-Auswahl mit Dropdown
- System-Buttons (Netzwerk, Bedienung, Power) mit Creepy-Meldungen
- Sound-Integration (Unlock bei erfolgreichem Login)

### Styling

```qss
/* Passwortbox */
#pwbox { 
    background: white; 
    border: 1px solid #ccc; 
    border-radius: 3px; 
}

/* Eingabefeld */
#pwedit { 
    border: none; 
    padding: 8px 12px; 
    color: black; 
    font-size: 14px; 
    background: white;
}

/* Pfeil-Button */
#arrow { 
    border-left: 1px solid #ddd; 
    background: white; 
}
#arrow:hover { background: #f0f0f0; }
```

### Creepy-Funktionen

- `_creepy_network()` - "Ihre Netzwerkaktivität wird überwacht..."
- `_creepy_accessibility()` - "Wir passen alles für Sie an..."
- `_creepy_power()` - "Der Computer schläft nie..." + Fenster schließt

### Sound-Integration

- Nutzt `core.sound.SoundPlayer`
- Spielt `Windows Unlock.wav` bei erfolgreichem Login
- Fallback wenn Sound nicht verfügbar

### Verwendung

```python
from widgets.login_dialog import LoginDialog
from core.config import load_users

users = load_users()
dlg = LoginDialog(users)
if dlg.exec() == QDialog.Accepted:
    user = dlg.selected_user()  # z.B. "Milan"
```
