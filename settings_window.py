from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QFileDialog, QMessageBox)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from styles import (style_round_btn, style_reg_button, style_login_button, style_red_button,
                    style_input_field, defult_ava, angle_alf, numbers)
from network import make_server_request


class SettingsWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        title_label = QLabel("Настройки профиля")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px; text-align: center;")
        main_layout.addWidget(title_label)

        # Аватар
        avatar_layout = QHBoxLayout()
        avatar_label = QLabel("Аватар:")
        avatar_label.setStyleSheet("font-size: 16px; padding: 10px;")

        self.avatarka = QPushButton()
        self.avatarka.setFixedSize(150, 150)
        self.avatarka.setStyleSheet(style_round_btn)

        response = make_server_request('info', {
            'user_token': self.main_window.user_token,
            'user_id': self.main_window.user_id
        })

        current_avatar = defult_ava
        if response and response.get('success'):
            current_avatar = response.get('avatar', defult_ava)

        icon = QIcon(current_avatar)
        self.avatarka.setIcon(icon)
        self.avatarka.setIconSize(QSize(140, 140))

        change_avatar_btn = QPushButton("Изменить аватар")
        change_avatar_btn.setStyleSheet(style_reg_button)

        avatar_layout.addWidget(avatar_label)
        avatar_layout.addWidget(self.avatarka)
        avatar_layout.addWidget(change_avatar_btn)
        main_layout.addLayout(avatar_layout)

        # Смена имени
        name_title = QLabel("Смена имени:")
        name_title.setStyleSheet("font-size: 16px; padding: 10px; font-weight: bold;")

        name_input_layout = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setStyleSheet(style_input_field)
        self.name_edit.setPlaceholderText("Введите новое имя")
        self.name_edit.setText(self.main_window.username)

        change_name_btn = QPushButton("Изменить имя")
        change_name_btn.setStyleSheet(style_reg_button)

        name_input_layout.addWidget(self.name_edit)
        name_input_layout.addWidget(change_name_btn)

        name_layout = QVBoxLayout()
        name_layout.addWidget(name_title)
        name_layout.addLayout(name_input_layout)
        main_layout.addLayout(name_layout)

        # Смена пароля
        password_title = QLabel("Смена пароля:")
        password_title.setStyleSheet("font-size: 16px; padding: 10px; font-weight: bold;")

        password_input_layout = QHBoxLayout()
        self.password_edit = QLineEdit()
        self.password_edit.setStyleSheet(style_input_field)
        self.password_edit.setPlaceholderText("Введите новый пароль")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        change_password_btn = QPushButton("Изменить пароль")
        change_password_btn.setStyleSheet(style_reg_button)

        password_input_layout.addWidget(self.password_edit)
        password_input_layout.addWidget(change_password_btn)

        password_layout = QVBoxLayout()
        password_layout.addWidget(password_title)
        password_layout.addLayout(password_input_layout)
        main_layout.addLayout(password_layout)

        back_chat_btn = QPushButton("Вернуться в чат")
        back_chat_btn.setStyleSheet(style_login_button)
        main_layout.addWidget(back_chat_btn)

        back_log_btn = QPushButton("Выйти")
        back_log_btn.setStyleSheet(style_red_button)
        main_layout.addWidget(back_log_btn)

        change_avatar_btn.clicked.connect(self.change_avatar)
        change_name_btn.clicked.connect(self.change_name)
        change_password_btn.clicked.connect(self.change_password)
        back_chat_btn.clicked.connect(self.show_chat_window)
        back_log_btn.clicked.connect(self.logout)


    def change_name(self):
        new_name = self.name_edit.text().strip()

        if not new_name:
            QMessageBox.warning(self, "Ошибка", "Имя не может быть пустым!")
            return

        response = make_server_request('update_profile', {
            'user_token': self.main_window.user_token,
            'user_id': self.main_window.user_id,
            'username': new_name
        })

        if response and response.get('success'):
            self.main_window.username = new_name
            QMessageBox.information(self, "Успех", "Имя успешно изменено!")

    def change_password(self):
        new_password = self.password_edit.text()

        if not new_password:
            QMessageBox.warning(self, "Ошибка", "Пароль не может быть пустым!")
            return

        if len(new_password) < 6 or len(new_password) > 16:
            QMessageBox.warning(self, "Ошибка", "Пароль должен содержать минимум 6, максимум 16 символов!")
            return

        number_for_pass = False
        zagl_for_pass = False
        low_for_pass = False

        for el in new_password:
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

        response = make_server_request('update_profile', {
            'user_token': self.main_window.user_token,
            'user_id': self.main_window.user_id,
            'password': new_password
        })

        if response and response.get('success'):
            self.password_edit.clear()
            QMessageBox.information(self, "Успех", "Пароль успешно изменен!")

    def show_chat_window(self):
        self.main_window.show_chat_window()

    def logout(self):
        self.main_window.logout()