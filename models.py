class Contact:
    def __init__(self, login, username, display_name=None):
        self.login = login
        self.username = username
        self.display_name = display_name or username

    def get_display_name(self):
        return self.display_name