import pymysql
import os
import hashlib
import datetime
from socket import *


class Controller:
    def __init__(self, conn: socket, addr: tuple):
        self.user = None
        self.conn, self.addr = conn, addr
        self.sql = SQLtool()
        self.salt = "S0m3R@nD0m5@lt"  # 添加一个随机的盐值

    def login(self, msg: str = "成功登录") -> bool:
        """
        完成客户端的登录请求
        :return:  登录成功返回True，登录返回False
        """
        login_msg = self.conn.recv(1024 * 1024)
        if login_msg == b"CLIENT CANCEL":
            return False
        login_msg = login_msg.decode().split(" ", 1)
        if not self.sql.query_user(login_msg[0]) or len(login_msg) != 2:
            self.conn.send(b'USER NOT EXIST')
            return False
        if self.sql.query_user(login_msg[0])[1] == self.__encrypt_password(login_msg[1]):
            self.conn.send(b'SUCCESS')
            self.user = login_msg[0]
            print(f"{self.addr}{msg}")
            return True
        self.conn.send(b'PWD ERROR')
        return False

    def register(self) -> bool:
        """
        完成客户端的注册请求
        :return: 注册成功返回True，否则返回False
        """
        register_msg = self.conn.recv(1024 * 1024)
        register_msg = register_msg.decode().split(" ", 1)
        if len(register_msg) != 2:
            self.conn.send(b"CLIENT MSG ERROR")
            return False
        if self.sql.insert_user(register_msg[0], self.__encrypt_password(register_msg[1])):
            self.conn.send(b"SUCCESS")
            return True
        self.conn.send(b"USER ALREADY EXIST")
        return False

    def recv_word(self):
        """
        接收客户端单词查询，并返回相应的解释
        :return:
        """
        while True:
            word_msg = self.conn.recv(1024 * 1024)
            if word_msg == b"0":
                break
            word = word_msg.decode()
            self.conn.send(self.sql.query_word(word).encode())
            self.sql.insert_history(self.user, word)

    def send_history(self):
        """
        向客户端发送历史记录
        :return:
        """
        msg = "序号\t年-月-日 时:分:秒\t\t用户\t\t查询单词\t\t\n"
        res = self.sql.query_history(self.user)
        if not res:
            msg = "当前用户无任何单词查询记录"
        count = 0
        for history in res:
            count += 1
            msg += f"{str(count)}\t\t"
            msg += "%s\t\t%s\t\t%s\n" % history
            # for h in history:
            #     msg += f"{str(h)}\t\t"
        self.conn.send(msg.encode())

    def handle_exit(self):
        """
        处理客户端申请退出程序事件
        :return:
        """
        print(f"{self.addr}退出程序")
        self.conn.send(b"OK")
        self.conn.close()

    def verify(self):
        """
        登录权限验证方法
        调用login方法，载入查词前验证用户登录是否合法，增加安全性
        :return: bool 如果用户是正常登录的，则返回True，否则返回False
        """
        return self.login("验证成功")

    def __encrypt_password(self, password: str) -> str:
        """
        Hash加密密码
        :param password: 输入密码
        :return: 加密后的值
        """
        m = hashlib.sha256()
        m.update((password + self.salt).encode("utf-8"))
        return m.hexdigest()


class SQLtool:
    """
    SQLtool     服务端数据库操作工具类
    包含一系列连接、关闭、初始化、查询、增加、清空等方法
    """

    def __init__(self):
        self.kwargs = {
            "host": "localhost",
            "port": 3306,
            "user": "root",  # mysql用户名
            "passwd": "2001",  # mysql密码
            "database": "dict",  # 空数据库
            "charset": "utf8"
        }
        self.dict_path = "EnWords.sql"  # 同一目录下的sql文件（该文件中的表名需要改为words，并且字段仅有word、translation）
        self.db = pymysql.connect(**self.kwargs)
        self.cur = self.db.cursor()

    def init(self) -> None:
        """
        数据库初始化方法（首次调用，后续注释）
        创建配置表settings、词典表words、历史记录表history、用户表users
        :return:
        """
        print("初始化--创建设置表")
        sql = "create table settings(" \
              "id int primary key auto_increment," \
              "name varchar(32) not null," \
              "setting varchar(128) default '');"
        self.cur.execute(sql)
        print("初始化--加载配置")
        self.insert_setting("词典路径", os.path.join(os.path.dirname(__file__), self.dict_path))
        self.insert_setting("词典是否加载", "否")
        print("初始化--创建词典表")
        sql = "create table words(" \
              "word varchar(32) not null default ''," \
              "translation varchar(512) default null" \
              ") engine=InnoDB default charset=utf8;"
        self.cur.execute(sql)
        print("初始化--创建历史查询表")
        sql = "create table history(" \
              "id int primary key auto_increment," \
              "name varchar(32) not null default ''," \
              "word varchar(32) default null," \
              "time datetime default null" \
              ") engine=InnoDB default charset=utf8;"
        self.cur.execute(sql)
        print("初始化--创建用户表")
        sql = "create table users(" \
              "name varchar(32) primary key not null," \
              "pwd varchar(128) default '');"
        self.cur.execute(sql)
        self.db.commit()
        print("初始化完成，请在服务端server.py中run方法中注释该方法的调用")

    def close(self) -> None:
        """
        关闭数据库的连接
        :return:
        """
        self.cur.close()
        self.db.close()

    def source(self, path: str = None) -> None:
        """
        词典加载方法
        在init调用一次后，成功建表后会自动检测词典是否加载
        如果未加载，会从settings表中词典路径加载
        注意：.SQL词典文件需要放在同一路径，并且相应更改dict_path实例标量对应文件名
        :param path: 词典路径，默认路径是配置表settings中的词典路径记录
        :return:
        """
        print("加载词典--进行中")
        with open(path, "r") as fr:
            sql = fr.read()
        statements = sql.split(";\n")
        for statement in statements:
            statement = statement.strip()
            if statement:
                self.cur.execute(statement)
        sql = "update settings " \
              "set setting = '是' " \
              "where name = '词典是否加载';"
        self.cur.execute(sql)
        self.db.commit()
        print("加载词典--已完成")

    def drop(self) -> None:
        """
        删除所有初始化的数据表
        :return:
        """
        tables = ["settings", "words", "history", "users"]
        for table in tables:
            sql = "drop table " + table + ";"
            self.cur.execute(sql)
        self.db.commit()

    def insert_setting(self, name: str, setting: str) -> None:
        """
        向设置表settings中插入一对设置项
        :param name: 设置项的标签
        :param setting: 设置项对应的值
        :return:
        """
        sql = "insert into settings (name,setting) values (%s,%s);"
        self.cur.execute(sql, (name, setting))

    def query_setting(self, name: str) -> str:
        """
        查询设置表settings中的设置值
        :param name: 设置表settings中的name字段，比如“词典路径”
        :return: str 设置表settings中的setting字段，比如"/home/.../EnWords.sql"
        """
        sql = "select setting from settings where name = %s;"
        self.cur.execute(sql, (name,))
        res = self.cur.fetchone()
        return res[0]

    def query_word(self, word: str) -> str:
        """
        查询单词表words中的对应word解释
        :param word: 单词表words中的word字段，即单词，表中建立了索引，增加了查询速度
        :return: translation[0] or "未查找到该单词" 单词对应的解释
        """
        sql = "select translation from words where word = %s"
        try:
            self.cur.execute(sql, (word,))
            translation = self.cur.fetchone()
            return translation[0] if translation else "未查找到该单词"
        except Exception as e:
            print(e)
            return "未查找到该单词"

    def insert_history(self, name: str, word: str) -> None:
        """
        向历史查询记录表插入一条记录
        :param name: 用户名
        :param word: 单词
        :return:
        """
        history = self.query_history(name)
        if history and len(history) == 15:
            sql = "delete from history where id = (select id from (select min(id) as id from history) as h );"
            self.cur.execute(sql)
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = "insert into history (name,word,time) values (%s,%s,%s);"
        self.cur.execute(sql, (name, word, time))
        self.db.commit()

    def query_history(self, name: str) -> list:
        """
        查询历史查询记录表history中对应name的所有记录
        :param name: 历史查询记录表history的name字段，即用户名
        :return: [(time, name, word)...] or None 历史查询记录表history中的对应name的所有记录（根据id倒序排列）
        """
        sql = "select time,name,word from history where name = %s order by id desc;"
        self.cur.execute(sql, (name,))
        res = self.cur.fetchall()
        return res

    def insert_user(self, name: str, pwd: str) -> bool:
        """
        用于注册时插入用户表users的方法
        :param name: 用户名
        :param pwd: 密码
        :return: bool 注册失败与否
        """
        sql = "select name from users where name = %s;"
        self.cur.execute(sql, (name,))
        if self.cur.fetchone():
            return False
        sql = "insert into users (name,pwd) values (%s,%s);"
        self.cur.execute(sql, (name, pwd))
        self.db.commit()
        return True

    def delete_user(self, name) -> bool:
        sql = "select name from users where name = %s;"
        self.cur.execute(sql, (name,))
        if not self.cur.fetchone():
            print(f"用户{name}不存在")
            return False
        sql = "delete from users where name = %s;"
        self.cur.execute(sql, (name, ))
        self.db.commit()
        print(f"用户{name}被删除")
        return True

    def query_user(self, name: str) -> tuple:
        """
        查询用户表users中的对应name的一段记录
        :param name: 用户表users中的name字段，即用户名
        :return: (name, pwd) or None 用户表users中的对应name的记录
        """
        sql = "select name, pwd from users where name = %s;"
        self.cur.execute(sql, (name,))
        res = self.cur.fetchone()
        return res


# 测试区域
if __name__ == '__main__':
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
