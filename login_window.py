from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic
from styles import style_input_field, style_login_button, style_reg_button
from network import make_server_request


class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        self.widget = uic.loadUi('log_wind.ui')

        self.widget.Log_Input1.setStyleSheet(style_input_field)
        self.widget.Password_Input1.setStyleSheet(style_input_field)
        self.widget.Login_Button.setStyleSheet(style_login_button)
        self.widget.Reg_Button1.setStyleSheet(style_reg_button)

        self.widget.Login_Button.clicked.connect(self.check_log)
        self.widget.Log_Input1.setPlaceholderText("Введите ваш логин")
        self.widget.Password_Input1.setPlaceholderText("Введите ваш пароль")
        self.widget.Reg_Button1.clicked.connect(self.show_register_window)

    def check_log(self):
        login = self.widget.Log_Input1.text()
        password = self.widget.Password_Input1.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        response = make_server_request('login', {
            'login': login,
            'password': password
        })

        if response and response.get('success'):
            self.main_window.current_user = login
            self.main_window.user_token = response['user_token']
            self.main_window.user_id = response['user_id']
            self.main_window.username = response['username']
            self.main_window.show_chat_window()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

    def show_register_window(self):
        self.main_window.show_register_window()

    def get_widget(self):
        return self.widget
