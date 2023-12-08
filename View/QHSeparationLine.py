from PyQt5.QtWidgets import QFrame, QSizePolicy


class QHSeparationLine(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(20)
        self.setMinimumWidth(1)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
