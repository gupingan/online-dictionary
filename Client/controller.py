import sys
from socket import *
from model import *


class DictClient:
    """
    DictClient      TCP客户端
    用于发送界面请求协议、请求登录或注册、发送查询单词
    与View层交互，实现网络传输逻辑控制
    """

    def __init__(self, host: str, port: int = 8888, user: User = None):
        self.host, self.port = host, port
        self.server_addr = (self.host, self.port)
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.user = user
        self.__connect()

    def __connect(self):
        try:
            self.sock.connect(self.server_addr)
        except ConnectionRefusedError:
            sys.exit("服务端已关闭，请等待管理员重新开启")

    def close(self):
        self.sock.close()

    def send_word(self, word: str):
        self.sock.send(word.encode())

    def execute(self, head: str, content: str):
        self.sock.send(f"{head} {content}".encode())

    def get_data(self):
        data = self.sock.recv(1024 * 1024 * 4)
        return data.decode()

    def request_login_or_register(self):
        self.sock.send(str(self.user).encode())
        return self.get_data()
