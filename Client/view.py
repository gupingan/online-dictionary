import sys
from model import User
from controller import DictClient


class View:
    """
    界面类
    负责输入输出
    """

    def __init__(self):
        self.__user = User()
        self.__sock = DictClient("127.0.0.1", user=self.__user)  # 对应服务端ip，此处为本地回环地址，测试用

    def __menu(self) -> None:
        """
        1 一级菜单
        :return:
        """
        while True:
            self.print_menu("主菜单", ("登录", "注册", "退出"))
            select = input("选择序号：")
            if select == "1":
                self.__sock.execute("1", "1")
                if self.__sock.get_data() == "OK":
                    if self.__call():
                        self.__call_login()
                    else:
                        self.__sock.execute("CLIENT", "CANCEL")
                        continue
            elif select == "2":
                self.__sock.execute("1", "2")
                if self.__sock.get_data() == "OK":
                    if self.__call():
                        self.__call_register()
                    else:
                        self.__sock.execute("CLIENT", "CANCEL")
                        continue
            elif select == "3":
                self.__sock.execute("1", "3")
                self.__exit()

    def __sub_menu(self) -> None:
        """
        1 1 二级菜单 登录后进入
        :return:
        """
        while self.__user.is_login:
            self.print_menu("词典功能区", ("查单词", "历史记录", "注销"))
            select = input("选择序号：")
            if select == "1":
                self.__sock.execute("1 1", "1")
                if self.__sock.get_data() == "OK":
                    if self.__call_verify():
                        self.__query_view()
            elif select == "2":
                self.__sock.execute("1 1", "2")
                print(self.__sock.get_data())
            elif select == "3":
                self.__sock.execute("1 1", "3")
                if self.__sock.get_data() == "OK":
                    print("注销登录\n")
                    self.__user.logout()
                    break

    def __query_view(self) -> None:
        """
        1 1 1 三级界面，单词循环查询
        :return:
        """
        print("\n当前处于：单词查询（输入0退出）")
        while True:
            word = input("单词：")
            if word == "":
                continue
            self.__sock.send_word(word)
            if word == "0":
                break
            print(self.__sock.get_data())

    def __call(self) -> bool:
        """
        呼叫注册或者登录的输入界面，并检查处理输入内容合法性以及加载本地用户对象
        :return: 注册或登录成功后返回True，否则返回False
        """
        name = input("用户名：")
        pwd = input("密  码：")
        if " " in name or not 2 <= len(name) <= 32:
            print("用户名不能包含空格且长度介于2~32\n")
            return False
        if " " in pwd or not 4 <= len(pwd) <= 32:
            print("密码不能包含空格且长度介于2~32\n")
            return False
        self.__user.load_user(name, pwd)
        return True

    def __call_verify(self) -> bool:
        """
        呼叫验证，用于登录后进入单词查询前的检查权限方法
        :return: bool 最新的本地缓存的用户登录状态
        """
        verify_response = self.__sock.request_login_or_register()
        if verify_response == "SUCCESS":
            self.__user.is_login = True
        else:
            self.__user.is_login = False
            print("验证登录权限有误，可能存在非法登录\n")
        return self.__user.is_login

    def __call_login(self) -> None:
        """
        呼叫登录，登录成功跳转下一级界面
        :return:
        """
        login_response = self.__sock.request_login_or_register()
        if login_response == "SUCCESS":
            print("登录成功\n")
            self.__user.is_login = True
            self.__sub_menu()
        elif login_response == "USER NOT EXIST":
            print("登录失败：用户不存在，请注册\n")
        elif login_response == "PWD ERROR":
            print("登录失败：密码错误\n")

    def __call_register(self) -> None:
        """
        呼叫注册
        :return:
        """
        register_response = self.__sock.request_login_or_register()
        if register_response == "SUCCESS":
            print("注册成功")
        elif register_response == "USER ALREADY EXIST":
            print("注册失败：用户名已存在")
        elif register_response == "CLIENT MSG ERROR":
            print("注册失败：请联系客服处理该问题")

    def __exit(self) -> None:
        """
        1 0 退出方法，通知服务端，双方准备完毕后退出，若出现异常强制退出
        :return:
        """
        if self.__sock.get_data() == "OK":
            self.__sock.close()
            sys.exit("退出程序")
        sys.exit("出现异常，强制退出程序")

    @staticmethod
    def print_menu(title: str, items: tuple):
        # 计算菜单项中最大的长度，用于确定每列的宽度
        max_item_len = max(len(item) for item in items)
        # 确定表格宽度和列宽度
        table_width = max(max_item_len + 8, len(title))
        column_width = table_width // 2
        # 设置表格上边框
        table_top = "┌" + "─" * (column_width + 8) + "┐"
        # 添加标题
        title_str = f"{title.center(table_width)}\n"
        title_str += table_top + "\n"
        # 添加菜单项
        item_str = ""
        for index, item in enumerate(items, start=1):
            item_str += "│ {:1d} │ {:<{width}} │\n".format(
                index, item, width=column_width)
        # 添加表格底部
        bottom_str = "└" + "─" * (column_width + 8) + "┘"
        # 打印完整菜单
        menu_str = title_str + item_str + bottom_str
        print(menu_str)

    def main(self) -> None:
        """
        main入口
        :return:
        """
        try:
            self.__menu()
        except KeyboardInterrupt:
            self.__sock.close()
            sys.exit("退出程序")
