import sys

from PyQt5 import Qt

from View.MainWindow import MainWindow
from backups.backup_MainWindow import MainWindow as BackupMainWindow

if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    debug = True

    if debug:
        window = MainWindow()
    else:
        window = BackupMainWindow()

    sys.exit(app.exec_())
