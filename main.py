import sys
from PySide6.QtWidgets import QApplication, QDialog
from core.config import load_users, ensure_dirs
from widgets.login_dialog import LoginDialog
from desktop.main_window import DesktopWindow
from core.session import Session

def main():
    ensure_dirs()
    app = QApplication(sys.argv)
    app.setApplicationName("WinFake")
    app.setOrganizationName("FunLabs")

    users = load_users()
    if not users:
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Konfiguration fehlt", "config/users.yaml enthält keine Benutzer.")
        sys.exit(1)

    dlg = LoginDialog(users)
    if dlg.exec() == QDialog.Accepted:
        sess = Session(current_user=dlg.selected_user())
        win = DesktopWindow(session=sess)
        win.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
