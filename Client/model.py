class User:
    """
    本地用户类，用于当前登录用户的抽象操作
    """
    def __init__(self):
        self.name, self.pwd = None, None
        self.is_login = False

    def load_user(self, name, pwd):
        self.name, self.pwd = name, pwd

    def logout(self):
        self.is_login = False
        self.name, self.pwd = None, None

    def __str__(self):
        return f"{self.name} {self.pwd}"
