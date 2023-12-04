from PyQt5.QtWidgets import QMessageBox, QWidget

class MessageBox:
    def __call__(self, parent: QWidget, type_of_message: TypeOfMessage, message: str) -> None:
        message_box = QMessageBox(parent)
        message_box.setWindowTitle(type_of_message.value.capitalize())
        message_box.setText(message)
        message_box.setStandardButtons(self.__get_buttons_by_type(type_of_message))
        message_box.setIcon(self.__get_icon_by_type(type_of_message))
        message_box.exec()

    def __get_buttons_by_type(self, type_of_message: TypeOfMessage) -> QMessageBox.StandardButton:
        match type_of_message:
            case TypeOfMessage.ERROR:
                return QMessageBox.StandardButton.Cancel
            case TypeOfMessage.SUCCESS:
                return QMessageBox.StandardButton.Ok

    def __get_icon_by_type(self, type_of_message: TypeOfMessage) -> QMessageBox.Icon:
        match type_of_message:
            case TypeOfMessage.ERROR:
                return QMessageBox.Icon.Critical
            case TypeOfMessage.SUCCESS:
                return QMessageBox.Icon.NoIcon