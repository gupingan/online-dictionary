from server import *

if __name__ == '__main__':
    server = DictServer(init=False, drop=False)
    # server.run(["Ronan"])  # 带参数即删除对应用户
    server.run()
