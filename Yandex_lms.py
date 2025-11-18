import sys
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLineEdit, QMessageBox,
                             QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QListWidget, QTextEdit, QTextBrowser, QFileDialog,
                             QToolButton, QMenu, QInputDialog)
from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize, QTimer
import markdown


SERVER_URL = "http://localhost:10000/api"

style_menu = """
QMenu {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 5px;
    margin-top: 5px;
}
QMenu::item {
    padding: 8px 20px;
    border-radius: 4px;
    margin: 2px;
}
QMenu::item:selected {
    background-color: #007acc;
    color: #ffffff;
}
QMenu::separator {
    height: 1px;
    background-color: #dee2e6;
    margin: 5px 0px;
}
"""

style_tool_button = """
QToolButton {
    border-radius: 20px;
    border: none;
    padding: 8px;
    background: transparent;
}
QToolButton:hover {
    background: #e0e0e0;
}
QToolButton:pressed {
    background: #d0d0d0;
}
QToolButton::menu-indicator {
    width: 0px;
}
"""

style_input_field = """
QLineEdit {
    border-radius: 10px;
    border: 2px solid #cccccc;
    padding: 10px 15px;
    font-size: 14px;
    background: #ffffff;
    color: #000000;
}
QLineEdit:focus {
    border: 2px solid #007acc;
}
"""

style_reg_button = """
QPushButton {
    border-radius: 10px;
    border: 2px solid #007acc;
    background: #007acc;
    padding: 12px 20px;
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
}
QPushButton:hover {
    background: #005a9e;
    border: 2px solid #005a9e;
}
QPushButton:pressed {
    background: #004a80;
}
"""

style_login_button = """
QPushButton {
    border-radius: 10px;
    border: 2px solid #28a745;
    background: #28a745;
    padding: 12px 20px;
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
}
QPushButton:hover {
    background: #218838;
    border: 2px solid #218838;
}
QPushButton:pressed {
    background: #1e7e34;
}
"""

style_red_button = """
QPushButton {
    border-radius: 10px;
    border: 2px solid #ff0015;
    background: #ff0015;
    padding: 12px 20px;
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
}
QPushButton:hover {
    background: #dd0013;
    border: 2px solid #dd0013;
}
QPushButton:pressed {
    background: #bb0010;
}
"""

style_mesg = """
QTextEdit {
    border-radius: 15px;
    border: 1px solid #cccccc;
    padding: 8px 12px;
    font-size: 14px;
    background: #ffffff;
}
QTextEdit:focus {
    border: 2px solid #007acc;
}
"""

style_round_btn = """
QPushButton {
    border-radius: 15px;
    border: 1px solid #cccccc;
    background: #ffffff;
    padding: 8px 12px;
}
QPushButton:hover {
    background: #f0f0f0;
}
"""

style_chat_list = """
QListWidget {
    border-radius: 15px;
    border: 1px solid #cccccc;
    background: #ffffff;
    outline: 0;
}
QListWidget::item {
    border-radius: 10px;
    padding: 10px;
    font-size: 14px;
    background: #ffffff;
    color: #000000;
    min-height: 30px;
}
QListWidget::item:selected {
    background: #e0e0e0;
    color: #000000;
}
QListWidget::item:hover {
    background: #f5f5f5;
    color: #000000;
}
"""

style_message_area1 = """
QTextBrowser {
    border-radius: 15px;
    border: 1px solid #cccccc;
    padding: 15px;
    font-size: 14px;
    background: #ffffff;
}
"""

style_hi_label = """
QLabel {
    font-size: 18px;
    color: #444444;
    font-weight: bold;
    padding: 10px;
    text-align: center;
}
"""

style_input_dialog = """
QInputDialog {
    background-color: #ffffff;
    border-radius: 10px;
}
QInputDialog QLabel {
    font-size: 15px;
    color: #333333;
    padding: 6px;
}
QInputDialog QLineEdit {
    border-radius: 8px;
    border: 2px solid #cccccc;
    padding: 8px 12px;
    font-size: 14px;
    background: #ffffff;
}
QInputDialog QLineEdit:focus {
    border: 2px solid #007acc;
}
QInputDialog QPushButton {
    border-radius: 8px;
    border: 2px solid #007acc;
    background: #007acc;
    padding: 8px 16px;
    font-size: 14px;
    color: #ffffff;
    min-width: 80px;
}
QInputDialog QPushButton:hover {
    background: #005a9e;
}
"""

# Допустимые символы
angle_alf = "abcdefghijklmnopqrstuvwxyz@!#*:?"
numbers = "1234567890"
defult_ava = "default_avatar.jpg"


class Contact:
    def __init__(self, login, username, display_name=None):
        self.login = login
        self.username = username
        self.display_name = display_name or username

    def get_display_name(self):
        return self.display_name


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_widget = None
        self.setFixedSize(470, 570)
        self.current_user = None
        self.user_token = None
        self.user_id = None
        self.username = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_messages)
        self.current_contact = None
        self.chat_widgets_initialized = False
        self.contacts = {}
        self.user_names = {}
        self.loggin_wind()

    def make_server_request(self, endpoint, data=None, method='POST'):
        url = f"{SERVER_URL}/{endpoint}"
        if method == 'POST':
            response = requests.post(url, json=data, timeout=1)
        else:
            response = requests.get(url, timeout=1)

        if response.status_code == 200:
            return response.json()
        return None

    def loggin_wind(self):
        if self.current_widget:
            self.current_widget.deleteLater()
        self.current_widget = uic.loadUi('log_wind.ui')
        self.setCentralWidget(self.current_widget)

        self.current_widget.Log_Input1.setStyleSheet(style_input_field)
        self.current_widget.Password_Input1.setStyleSheet(style_input_field)
        self.current_widget.Login_Button.setStyleSheet(style_login_button)
        self.current_widget.Reg_Button1.setStyleSheet(style_reg_button)

        self.current_widget.Login_Button.clicked.connect(self.check_log)
        self.current_widget.Log_Input1.setPlaceholderText("Введите ваш логин")
        self.current_widget.Password_Input1.setPlaceholderText("Введите ваш пароль")
        self.current_widget.Reg_Button1.clicked.connect(self.register_window)

    def check_log(self):
        login = self.current_widget.Log_Input1.text()
        password = self.current_widget.Password_Input1.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        response = self.make_server_request('login', {
            'login': login,
            'password': password
        })

        if response and response.get('success'):
            self.current_user = login
            self.user_token = response['user_token']
            self.user_id = response['user_id']
            self.username = response['username']
            self.chat_window()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

    def register_window(self):
        if self.current_widget:
            self.current_widget.deleteLater()
        self.current_widget = uic.loadUi('reg_wind.ui')
        self.setCentralWidget(self.current_widget)

        self.current_widget.Name_Input.setStyleSheet(style_input_field)
        self.current_widget.Log_Input.setStyleSheet(style_input_field)
        self.current_widget.Password_Input.setStyleSheet(style_input_field)
        self.current_widget.Password2_Input.setStyleSheet(style_input_field)
        self.current_widget.Reg_Button.setStyleSheet(style_reg_button)
        self.current_widget.back_reg.setStyleSheet(style_login_button)

        self.current_widget.Name_Input.setPlaceholderText("Введите имя")
        self.current_widget.Log_Input.setPlaceholderText("Введите логин")
        self.current_widget.Password_Input.setPlaceholderText("Введите пароль")
        self.current_widget.Password2_Input.setPlaceholderText("Повторите пароль")

        self.current_widget.Reg_Button.clicked.connect(self.check_reg)
        self.current_widget.back_reg.clicked.connect(self.loggin_wind)

    def check_reg(self):
        login = self.current_widget.Log_Input.text()
        password1 = self.current_widget.Password_Input.text()
        name = self.current_widget.Name_Input.text()
        password2 = self.current_widget.Password2_Input.text()

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

        response = self.make_server_request('register', {
            'login': login,
            'password': password1,
            'username': name
        })

        if response and response.get('success'):
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
            self.loggin_wind()
        else:
            QMessageBox.warning(self, "Ошибка", "Логин уже занят!")

    def chat_window(self):
        if self.current_widget:
            self.current_widget.deleteLater()
        self.setFixedSize(700, 600)
        self.current_widget = QWidget()
        self.setCentralWidget(self.current_widget)

        main_layout = QHBoxLayout(self.current_widget)

        left_panel = QWidget()
        left_panel.setFixedWidth(220)
        left_layout = QVBoxLayout(left_panel)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Поиск контактов")
        self.search_edit.setStyleSheet(style_input_field)

        self.chats_list_widget = QListWidget()
        self.chats_list_widget.setStyleSheet(style_chat_list)

        add_chat_btn = QPushButton("⚙ Настройки")
        dobavit_contact = QPushButton("➕ Добавить контакт")
        dobavit_contact.setStyleSheet(style_round_btn)
        add_chat_btn.setStyleSheet(style_round_btn)

        left_layout.addWidget(self.search_edit)
        left_layout.addWidget(self.chats_list_widget)
        left_layout.addWidget(dobavit_contact)
        left_layout.addWidget(add_chat_btn)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        chat_header_layout = QHBoxLayout()

        self.chat_name_label = QLabel("Выберите чат для общения")
        self.chat_name_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; ")

        self.chat_prefix_label = QPushButton()
        self.chat_prefix_label.setFixedSize(40, 40)
        self.chat_prefix_label.setStyleSheet(style_round_btn)
        icon = QIcon(defult_ava)
        self.chat_prefix_label.setIcon(icon)
        self.chat_prefix_label.setIconSize(QSize(60, 60))

        settings_tool_btn = QToolButton()
        settings_tool_btn.setFixedSize(45, 45)
        settings_tool_btn.setStyleSheet(style_tool_button)
        settings_tool_btn.setIcon(QIcon("3_points.png"))
        settings_tool_btn.setIconSize(QSize(35, 35))
        settings_tool_btn.setToolTip("Меню чата")

        settings_menu = QMenu(self)
        settings_menu.setStyleSheet(style_menu)

        del_chat = settings_menu.addAction("🗑️ Удалить из контактов")
        settings_menu.addSeparator()
        rename_chat = settings_menu.addAction("⚙ Изменить имя")

        settings_tool_btn.setMenu(settings_menu)
        settings_tool_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        chat_header_layout.addWidget(self.chat_prefix_label)
        chat_header_layout.addWidget(self.chat_name_label)
        chat_header_layout.addStretch()
        chat_header_layout.addWidget(settings_tool_btn)

        self.messages_text_browser = QTextBrowser()
        self.messages_text_browser.setStyleSheet(style_message_area1)

        input_panel_layout = QHBoxLayout()
        self.message_input_edit = QTextEdit()
        self.message_input_edit.setPlaceholderText("Введите сообщение...")
        self.message_input_edit.setStyleSheet(style_mesg)
        self.message_input_edit.setMaximumHeight(45)

        self.otpravka_btn = QPushButton()
        self.otpravka_btn.setFixedSize(40, 40)
        self.otpravka_btn.setStyleSheet(style_round_btn)
        icon = QIcon("otpravka.jpg")
        self.otpravka_btn.setIcon(icon)
        self.otpravka_btn.setIconSize(QSize(30, 30))

        input_panel_layout.addWidget(self.message_input_edit)
        input_panel_layout.addWidget(self.otpravka_btn)

        right_layout.addLayout(chat_header_layout)
        right_layout.addWidget(self.messages_text_browser)
        right_layout.addLayout(input_panel_layout)

        self.hi_label = QLabel("""Добро пожаловать в B.M.S.!

        Выберите чат для начала общения
         и начинай (соблюдая правила) !
        Договаривайся о встречах, делись файлами,
         совершай сделки и многое другое!
        """)
        self.hi_label.setStyleSheet(style_hi_label)
        self.hi_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        main_layout.addWidget(self.hi_label)

        right_panel.hide()
        self.hi_label.show()

        self.current_right_widget = self.hi_label
        self.chat_widgets_initialized = True

        self.load_all_users()
        self.load_contacts()
        self.load_contact_settings()

        self.otpravka_btn.clicked.connect(self.send_message)
        add_chat_btn.clicked.connect(self.settings)
        self.search_edit.textChanged.connect(self.update_contacts_list)
        self.chats_list_widget.itemClicked.connect(self.on_chat_selected)
        dobavit_contact.clicked.connect(self.add_contact_dialog)
        del_chat.triggered.connect(self.delete_chat)
        rename_chat.triggered.connect(self.rename_contact)

        self.timer.start(5000)
        self.message_input_edit.setFocus()

    def load_all_users(self):
        response = self.make_server_request('info', {
            'user_token': self.user_token,
            'user_id': self.user_id
        })

        if response and response.get('success') and 'users' in response:
            self.user_names = {}
            for user in response['users']:
                if user['login'] != self.current_user:
                    self.user_names[user['login']] = user['username']

    def load_contacts(self):
        response = self.make_server_request('get_contacts', {
            'user_token': self.user_token,
            'user_id': self.user_id
        })

        if response and response.get('success') and 'contacts' in response:
            self.contacts = {}
            for contact_data in response['contacts']:
                contact = Contact(
                    login=contact_data['login'],
                    username=contact_data['username']
                )
                self.contacts[contact_data['login']] = contact
        self.update_contacts_list()

    def load_contact_settings(self):
        response = self.make_server_request('get_contact_settings', {
            'user_token': self.user_token,
            'user_id': self.user_id
        })

        if response and response.get('success'):
            settings = response.get('settings', {})
            for contact_login, setting in settings.items():
                if contact_login in self.contacts:
                    display_name = setting.get('display_name')
                    if display_name:
                        self.contacts[contact_login].display_name = display_name

            self.update_contacts_list()

    def search_contacts(self, search_text):
        search_text = search_text.strip().lower()

        if not search_text:
            result = []
            for contact in self.contacts.values():
                display_name = contact.get_display_name()
                result.append(display_name)
            return result

        filtered_contacts = []
        for contact in self.contacts.values():
            display_name = contact.get_display_name().lower()
            if search_text in display_name:
                filtered_contacts.append(contact.get_display_name())

        return filtered_contacts

    def update_contacts_list(self):
        search_text = self.search_edit.text()
        filtered_contacts = self.search_contacts(search_text)

        self.chats_list_widget.clear()
        self.chats_list_widget.addItems(filtered_contacts)

        if search_text and not filtered_contacts:
            self.chats_list_widget.addItem("Контакты не найдены")

    def on_chat_selected(self, item):
        if not self.chat_widgets_initialized:
            return

        display_name = item.text()

        if display_name == "Контакты не найдены":
            return

        selected_contact = None
        for contact in self.contacts.values():
            if contact.get_display_name() == display_name:
                selected_contact = contact
                break

        if not selected_contact:
            return

        self.chat_name_label.setText(display_name)
        self.current_contact = selected_contact

        if self.current_right_widget == self.hi_label:
            self.hi_label.hide()
            main_layout = self.current_widget.layout()
            right_panel = main_layout.itemAt(1).widget()
            right_panel.show()
            self.current_right_widget = right_panel

        self.load_chat_history()
        self.message_input_edit.setFocus()

    def load_chat_history(self):
        if not self.current_contact:
            return

        response = self.make_server_request('get_messages', {
            'user_token': self.user_token,
            'user_id': self.user_id,
            'other_user_login': self.current_contact.login
        })

        if response and response.get('success'):
            self.messages_text_browser.clear()
            messages = response.get('messages', [])
            for msg in messages:
                if msg['sender_login'] == self.current_user:
                    sender = "Вы"
                else:
                    sender = self.current_contact.get_display_name()

                if 'timestamp' in msg:
                    time = msg['timestamp'][11:16]
                else:
                    time = ''

                message_text = msg['message_text']
                html_content = markdown.markdown(message_text)

                self.messages_text_browser.append(f"{time} {sender}: {html_content}")

    def add_contact_dialog(self):
        login, ok = QInputDialog.getText(self, "Добавить контакт", "Введите логин пользователя:")
        if ok and login:
            self.add_contact_by_login(login)

    def add_contact_by_login(self, contact_login):
        if not contact_login:
            QMessageBox.warning(self, "Ошибка", "Введите логин пользователя!")
            return

        if contact_login == self.current_user:
            QMessageBox.warning(self, "Ошибка", "Нельзя добавить самого себя!")
            return

        if contact_login not in self.user_names:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином не найден!")
            return

        if contact_login in self.contacts:
            QMessageBox.information(self, "Информация", "Этот контакт уже добавлен!")
            return

        response = self.make_server_request('add_contact', {
            'user_token': self.user_token,
            'user_id': self.user_id,
            'contact_login': contact_login
        })

        if response and response.get('success'):
            new_contact = Contact(
                login=contact_login,
                username=self.user_names[contact_login]
            )
            self.contacts[contact_login] = new_contact
            self.update_contacts_list()
            QMessageBox.information(self, "Успех", f"Контакт '{self.user_names[contact_login]}' добавлен!")
        else:
            QMessageBox.warning(self, "Ошибка", "Ошибка")

    def delete_chat(self):
        if not self.current_contact:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите чат для удаления!")
            return

        reply = QMessageBox.question(self, 'Удаление чатa',
                                     f'Вы уверены, что хотите удалить чат с {self.current_contact.get_display_name()}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            response = self.make_server_request('remove_contact', {
                'user_token': self.user_token,
                'user_id': self.user_id,
                'contact_login': self.current_contact.login
            })

            if response and response.get('success'):
                if self.current_contact.login in self.contacts:
                    del self.contacts[self.current_contact.login]

                self.update_contacts_list()
                self.current_contact = None
                self.chat_name_label.setText("Выберите чат для общения")
                self.messages_text_browser.clear()
                self.show_welcome_screen()
                QMessageBox.information(self, "Успех", "Чат удален!")
            else:
                QMessageBox.warning(self, "Ошибка", "Ошибка при удалении чата!")

    def rename_contact(self):
        if not self.current_contact:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите чат!")
            return

        new_name, ok = QInputDialog.getText(self, "Переименование",
                                            "Введите новое имя для контакта:",
                                            text=self.current_contact.get_display_name())

        if ok and new_name and new_name != self.current_contact.get_display_name():
            response = self.make_server_request('save_contact_settings', {
                'user_token': self.user_token,
                'user_id': self.user_id,
                'contact_login': self.current_contact.login,
                'display_name': new_name
            })

            if response and response.get('success'):
                self.current_contact.display_name = new_name
                self.chat_name_label.setText(new_name)
                self.update_contacts_list()
                QMessageBox.information(self, "Успех", "Контакт переименован!")
            else:
                QMessageBox.warning(self, "Ошибка", "Ошибка!")

    def show_welcome_screen(self):
        if self.current_right_widget != self.hi_label:
            self.current_right_widget.hide()
            self.hi_label.show()
            self.current_right_widget = self.hi_label

    def send_message(self):
        if not self.current_contact or not self.message_input_edit.toPlainText().strip():
            return

        message = self.message_input_edit.toPlainText().strip()

        response = self.make_server_request('send_message', {
            'user_token': self.user_token,
            'user_id': self.user_id,
            'receiver_login': self.current_contact.login,
            'text': message
        })

        if response and response.get('success'):
            self.message_input_edit.clear()
            self.load_chat_history()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось отправить сообщение!")

    def update_messages(self):
        if self.current_contact:
            self.load_chat_history()

    def settings(self):
        self.timer.stop()
        self.chat_widgets_initialized = False

        if self.current_widget:
            self.current_widget.deleteLater()
        self.setFixedSize(530, 600)
        self.current_widget = QWidget()
        self.setCentralWidget(self.current_widget)

        main_layout = QVBoxLayout(self.current_widget)

        title_label = QLabel("Настройки профиля")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px; text-align: center;")
        main_layout.addWidget(title_label)

        avatar_layout = QHBoxLayout()
        avatar_label = QLabel("Аватар:")
        avatar_label.setStyleSheet("font-size: 16px; padding: 10px;")

        self.avatarka = QPushButton()
        self.avatarka.setFixedSize(150, 150)
        self.avatarka.setStyleSheet(style_round_btn)

        response = self.make_server_request('info', {
            'user_token': self.user_token,
            'user_id': self.user_id
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

        name_title = QLabel("Смена имени:")
        name_title.setStyleSheet("font-size: 16px; padding: 10px; font-weight: bold;")

        name_input_layout = QHBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setStyleSheet(style_input_field)
        self.name_edit.setPlaceholderText("Введите новое имя")
        self.name_edit.setText(self.username)

        change_name_btn = QPushButton("Изменить имя")
        change_name_btn.setStyleSheet(style_reg_button)

        name_input_layout.addWidget(self.name_edit)
        name_input_layout.addWidget(change_name_btn)

        name_layout = QVBoxLayout()
        name_layout.addWidget(name_title)
        name_layout.addLayout(name_input_layout)
        main_layout.addLayout(name_layout)

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
        back_chat_btn.clicked.connect(self.chat_window)
        back_log_btn.clicked.connect(self.logout)

    def change_avatar(self):
        fname = QFileDialog.getOpenFileName(
            self, 'Выбрать аватар', '',
            'Изображения (*.jpg *.jpeg *.png *.gif *.bmp *.webp)')[0]

        if fname:
            icon = QIcon(fname)
            self.avatarka.setIcon(icon)
            self.avatarka.setIconSize(QSize(140, 140))
            QMessageBox.information(self, "Успех", "Аватарка успешно изменена!")

    def change_name(self):
        new_name = self.name_edit.text().strip()

        if not new_name:
            QMessageBox.warning(self, "Ошибка", "Имя не может быть пустым!")
            return

        response = self.make_server_request('update_profile', {
            'user_token': self.user_token,
            'user_id': self.user_id,
            'username': new_name
        })

        if response and response.get('success'):
            self.username = new_name
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

        response = self.make_server_request('update_profile', {
            'user_token': self.user_token,
            'user_id': self.user_id,
            'password': new_password
        })

        if response and response.get('success'):
            self.password_edit.clear()
            QMessageBox.information(self, "Успех", "Пароль успешно изменен!")

    def logout(self):
        self.timer.stop()
        self.current_user = None
        self.user_token = None
        self.user_id = None
        self.username = None
        self.current_contact = None
        self.chat_widgets_initialized = False
        self.contacts = {}
        self.user_names = {}
        self.loggin_wind()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_input_dialog)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())