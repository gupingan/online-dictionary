import sys
from multiprocessing import Process
from controller import *


class DictServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8888, count: int = 5, init: bool = False, drop: bool = False):
        self.host, self.port, self.count = host, port, count
        self.init, self.drop = init, drop
        self.server_addr = (self.host, self.port)
        self.tcp = self.__create_socket()
        self.sql = SQLtool()

    def __create_socket(self):
        """
        创建服务端TCP套接字
        :return: 套接字
        """
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind(self.server_addr)
        sock.listen(self.count)
        return sock

    def run(self, del_users: list = None):
        """
        服务端启动方法
        :param del_users: 服务端手动删除用户，可批量删除
        :return:
        """
        try:
            if del_users:
                for user in del_users:
                    self.sql.delete_user(user)
            if self.drop:
                self.sql.drop()  # 用于清空服务所有对应的表，然后重新初始化，实例化server时，关键传参drop为True即可
            if self.init:
                self.sql.init()  # 用于初始化，实例化server时，关键传参init为True即可
            if self.sql.query_setting("词典是否加载") == "否":
                self.sql.source(self.sql.query_setting("词典路径"))  # 未加载词典时，会从对应路径加载词典文件
        except Exception as e:
            if e.args[0] == 1050:
                print("请将参数init设为False")
            elif e.args[0] == 1051:
                print("请将参数drop设为False")
            elif e.args[0] == 1146:
                print("请将参数init设为True")
            else:
                print(e.args)
            return
        finally:
            self.sql.close()
        print("服务端：开始正常运行")
        while True:
            try:
                conn, addr = self.tcp.accept()
                handle = HandleProcess(conn, addr)
                handle.start()
                print(f"{addr}建立连接")
            except KeyboardInterrupt:
                sys.exit("服务端终止运行")


class HandleProcess(Process):
    def __init__(self, conn: socket, addr: tuple):
        self.conn, self.addr = conn, addr
        self.controller = Controller(conn, addr)
        super().__init__(daemon=True)

    def run(self):
        """
        多进程并发，处理客户端的选择
        :return:
        """
        while True:
            client_msg = self.conn.recv(1024)
            client_msg = tuple(client_msg.decode().split(" ", 2))
            client_msg_len = len(client_msg)
            if client_msg_len == 1:
                if client_msg == ("",):
                    print(f"{self.addr}退出程序")
                    break
            if client_msg_len == 2:
                if client_msg == ("1", "1"):
                    self.conn.send(b"OK")
                    self.controller.login()
                elif client_msg == ("1", "2"):
                    self.conn.send(b"OK")
                    self.controller.register()
                elif client_msg == ("1", "3"):
                    self.controller.handle_exit()
                    break
            if client_msg_len == 3:
                if client_msg == ("1", "1", "1"):
                    self.conn.send(b"OK")
                    if self.controller.verify():
                        self.controller.recv_word()
                elif client_msg == ("1", "1", "2"):
                    self.controller.send_history()
                elif client_msg == ("1", "1", "3"):
                    self.conn.send(b"OK")
                    print(f"{self.addr}退出登录")


# 代码测试
if __name__ == '__main__':
    pass
