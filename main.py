import sys

from PyQt5 import Qt

from View.MainWindow import MainWindow

if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
