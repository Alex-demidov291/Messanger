from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6 import uic
from styles import style_input_field, style_reg_button, style_login_button, angle_alf, numbers
from network import make_server_request


class RegisterWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        self.widget = uic.loadUi('reg_wind.ui')

        self.widget.Name_Input.setStyleSheet(style_input_field)
        self.widget.Log_Input.setStyleSheet(style_input_field)
        self.widget.Password_Input.setStyleSheet(style_input_field)
        self.widget.Password2_Input.setStyleSheet(style_input_field)
        self.widget.Reg_Button.setStyleSheet(style_reg_button)
        self.widget.back_reg.setStyleSheet(style_login_button)

        self.widget.Name_Input.setPlaceholderText("Введите имя")
        self.widget.Log_Input.setPlaceholderText("Введите логин")
        self.widget.Password_Input.setPlaceholderText("Введите пароль")
        self.widget.Password2_Input.setPlaceholderText("Повторите пароль")

        self.widget.Reg_Button.clicked.connect(self.check_reg)
        self.widget.back_reg.clicked.connect(self.show_login_window)

    def check_reg(self):
        login = self.widget.Log_Input.text()
        password1 = self.widget.Password_Input.text()
        name = self.widget.Name_Input.text()
        password2 = self.widget.Password2_Input.text()

        if not all([login, password1, name, password2]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        if password1 != password2:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return

        if len(name) < 3 or len(name) > 15:
            QMessageBox.warning(self, "Ошибка", "Имя должен содержать минимум 3, максимум 15 символов!")
            return

        for el in name:
            if el not in numbers and el != "_" and el not in angle_alf and el not in angle_alf.upper():
                QMessageBox.warning(self, "Ошибка", "Используются недопустимые символы в имени!")
                return

        if len(login) < 5 or len(login) > 20:
            QMessageBox.warning(self, "Ошибка", "Логин должен содержать минимум 5, максимум 20 символов!")
            return

        for el in login:
            if el not in numbers and el != "_" and el not in angle_alf and el not in angle_alf.upper():
                QMessageBox.warning(self, "Ошибка", "Используются недопустимые символы в логине!")
                return

        if len(password1) < 6 or len(password1) > 16:
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 6, максимум 16 символов!")
            return

        number_for_pass = False
        zagl_for_pass = False
        low_for_pass = False

        for el in password1:
            if el in numbers or el == "_":
                number_for_pass = True
            elif el in angle_alf:
                low_for_pass = True
            elif el in angle_alf.upper():
                zagl_for_pass = True

        if not number_for_pass or not zagl_for_pass or not low_for_pass:
            QMessageBox.warning(self, "Ошибка",
                                "Пароль должен содержать маленькие и заглавные англ. буквы, а так же цифры или _ !")
            return

        response = make_server_request('register', {
            'login': login,
            'password': password1,
            'username': name
        })

        if response and response.get('success'):
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
            self.show_login_window()
        else:
            QMessageBox.warning(self, "Ошибка", "Логин уже занят!")

    def show_login_window(self):
        self.main_window.show_login_window()

    def get_widget(self):
        return self.widget