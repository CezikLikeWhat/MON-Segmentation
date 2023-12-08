from enum import Enum

from PyQt5.QtWidgets import QMessageBox, QWidget


class MessageBoxType(str, Enum):
    ERROR = 'error'
    INFO = 'info'


class MessageBox:
    def __call__(self, parent: QWidget, messagebox_type: MessageBoxType, message: str) -> None:
        message_box = QMessageBox(parent)
        message_box.setWindowTitle('ERROR' if messagebox_type == MessageBoxType.ERROR else 'INFO')
        message_box.setText(message)
        message_box.setStandardButtons(self.__get_buttons_by_type(messagebox_type))
        message_box.setIcon(self.__get_icon_by_type(messagebox_type))
        message_box.exec()

    def __get_buttons_by_type(self, type_of_message: MessageBoxType) -> QMessageBox.StandardButton:
        match type_of_message:
            case MessageBoxType.ERROR:
                return QMessageBox.StandardButton.Cancel
            case MessageBoxType.INFO:
                return QMessageBox.StandardButton.Ok

    def __get_icon_by_type(self, type_of_message: MessageBoxType) -> QMessageBox.Icon:
        match type_of_message:
            case MessageBoxType.ERROR:
                return QMessageBox.Icon.Critical
            case MessageBoxType.INFO:
                return QMessageBox.Icon.NoIcon
