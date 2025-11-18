from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QListWidget, QTextEdit, QTextBrowser, QLineEdit, QToolButton,
                             QMenu, QInputDialog, QMessageBox)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt
from styles import (style_input_field, style_chat_list, style_message_area1, style_mesg,
                    style_round_btn, style_tool_button, style_menu, style_hi_label, defult_ava)
from network import make_server_request
from models import Contact
import markdown


class ChatWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.current_contact = None
        self.chat_widgets_initialized = False
        self.contacts = {}
        self.user_names = {}
        self.init_ui()
        self.load_all_users()
        self.load_contacts()
        self.load_contact_settings()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Левая панель
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

        # Правая панель
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

        self.hi_label = QLabel("""Добро пожаловать в QuickTalk!

Прямое общение без лишнего шума.
Быстрый поиск по всем контактам, удобное управление диалогами,
простота в использовании и минималистичный дизайн.
Наслаждайтесь чистотой коммуникации!
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

        self.otpravka_btn.clicked.connect(self.send_message)
        add_chat_btn.clicked.connect(self.show_settings)
        self.search_edit.textChanged.connect(self.update_contacts_list)
        self.chats_list_widget.itemClicked.connect(self.on_chat_selected)
        dobavit_contact.clicked.connect(self.add_contact_dialog)
        del_chat.triggered.connect(self.delete_chat)
        rename_chat.triggered.connect(self.rename_contact)

        self.message_input_edit.setFocus()

    def load_all_users(self):
        response = make_server_request('info', {
            'user_token': self.main_window.user_token,
            'user_id': self.main_window.user_id
        })

        if response and response.get('success') and 'users' in response:
            self.user_names = {}
            for user in response['users']:
                if user['login'] != self.main_window.current_user:
                    self.user_names[user['login']] = user['username']

    def load_contacts(self):
        response = make_server_request('get_contacts', {
            'user_token': self.main_window.user_token,
            'user_id': self.main_window.user_id
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
        response = make_server_request('get_contact_settings', {
            'user_token': self.main_window.user_token,
            'user_id': self.main_window.user_id
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

        display_name = item.text()

        if display_name == "Контакты не найдены":
            return

        selected_contact = None
        for cont in self.contacts.values():
            if cont.get_display_name() == display_name:
                selected_contact = cont
                break

        if not selected_contact:
            return

        self.chat_name_label.setText(display_name)
        self.current_contact = selected_contact

        if self.current_right_widget == self.hi_label:
            self.hi_label.hide()
            right_panel = self.layout().itemAt(1).widget()
            right_panel.show()
            self.current_right_widget = right_panel

        self.load_chat_history()
        self.message_input_edit.setFocus()

    def load_chat_history(self):
        response = make_server_request('get_messages', {
            'user_token': self.main_window.user_token,
            'user_id': self.main_window.user_id,
            'other_user_login': self.current_contact.login
        })

        if response and response.get('success'):
            self.messages_text_browser.clear()
            messages = response.get('messages', [])
            for msg in messages:
                if msg['sender_login'] == self.main_window.current_user:
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

        if contact_login == self.main_window.current_user:
            QMessageBox.warning(self, "Ошибка", "Нельзя добавить самого себя!")
            return

        if contact_login not in self.user_names:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином не найден!")
            return

        if contact_login in self.contacts:
            QMessageBox.information(self, "Информация", "Этот контакт уже добавлен!")
            return

        response = make_server_request('add_contact', {
            'user_token': self.main_window.user_token,
            'user_id': self.main_window.user_id,
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
        reply = QMessageBox.question(self, 'Удаление чатa',
                                     f'Вы уверены, что хотите удалить чат с {self.current_contact.get_display_name()}?')

        if reply == QMessageBox.StandardButton.Yes:
            response = make_server_request('remove_contact', {
                'user_token': self.main_window.user_token,
                'user_id': self.main_window.user_id,
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
        new_name, ok = QInputDialog.getText(self, "Переименование",
                                            "Введите новое имя для контакта:",
                                            text=self.current_contact.get_display_name())

        if ok and new_name and new_name != self.current_contact.get_display_name():
            response = make_server_request('save_contact_settings', {
                'user_token': self.main_window.user_token,
                'user_id': self.main_window.user_id,
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
        message = self.message_input_edit.toPlainText().strip()

        response = make_server_request('send_message', {
            'user_token': self.main_window.user_token,
            'user_id': self.main_window.user_id,
            'receiver_login': self.current_contact.login,
            'text': message
        })

        if response and response.get('success'):
            self.message_input_edit.clear()
            self.load_chat_history()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось отправить сообщение!")

    def show_settings(self):
        self.main_window.show_settings_window()