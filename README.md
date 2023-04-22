# Online Dictionary

Online Dictionary 是一款基于 TCP 协议和 MySql 数据库使用 Python 开发的网络词典，支持注册、登录、查词、浏览查询记录等功能。

## 开发环境

- Python 3.10.6
- MySQL 8.0.32（InnoDB引擎）
- PyCharm 2023.1

## 知识点

- Python基础语法
    - 注释、运算符等
    - 函数、类、静态方法、实例方法等
    - 选择语句、循环语句等
    - 继承、封装等
- Python高级
    - 异常处理
    - 内置高阶函数（max、min等）
    - 文件处理、正则表达式等等
- MYSQL数据库
    - 建表
    - 增删改查等等
- 网络并发编程
    - 多进程
    - TCP传输
    - 网络并发模型
    - 请求协议与响应协议等等

## 使用

1. 克隆项目：

   ```bash
   git clone https://github.com/ITchujian/online-dictionary.git
   ```

2. 创建数据库：

   在 MySQL 中创建一个名为 `dict` 的数据库：

   ```mysql
   CREATE DATABASE dict CHARACTER SET utf8;
   ```

3. 安装依赖：

   ```bash
   cd .../OnlineDict
   pip install -r requirements.txt
   ```

4. 服务端配置：

更改数据库用户名和密码（controller.py）：

   ```python
   class SQLtool:


    def __init__(self):
        self.kwargs = {
            "host": "localhost",
            "port": 3306,
            "user": "你的mysql用户名",  # 更改为你的mysql用户名
            "passwd": "你的mysql密码",  # 更改为你的mysql密码
            "database": "dict",  # 第一步创建的数据库
            "charset": "utf8"
        }
        self.dict_path = "EnWords.sql"  # 同一目录下的sql文件（该文件中的表名需要改为words，并且字段仅有word、translation）
        self.db = pymysql.connect(**self.kwargs)
        self.cur = self.db.cursor()
   ```

首次运行，在run.py文件中更改如下代码：

   ```python
    server = DictServer(init=True, drop=False)
    # init设置为True，用于创建数据表
   ```

服务端打印“服务端正常运行”，即可启动客户端（启动前请看下一步）

5. 客户端配置

在view.py中更改如下代码：

```python
class View:
    def __init__(self):
        self.__user = User()
        self.__sock = DictClient("127.0.0.1", user=self.__user)  # 更改ip地址，对应服务端ip，此处为本地回环地址，测试用
```

6. 服务端运行：

   ```bash
   cd .../OnlineDict/Server
   python3 run.py
   ```

7. 客户端运行：

   ```bash
   cd .../OnlineDict/Clent
   python3 main.py
   ```

## 功能

- 用户注册：用户可以在应用中进行注册，注册后即可使用在线词典。
- 用户登录：已注册的用户可以登录词典，享受查询单词、查看查询历史等功能。
- 单词查询：用户可以通过在线词典查询英文单词的中文翻译。
- 查询历史：用户可以查看自己的查询历史记录。

以及若干小方法、小功能

## 协议

本项目使用 GNU General Public License v3.0 协议。
