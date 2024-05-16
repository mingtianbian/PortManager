import socket
import threading

class PortOpener:
    def __init__(self, port):
        self.port = port
        self.server_socket = None
        self.running = False

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        print(f"服务器已在端口 {self.port} 启动")
        self.running = True

        while self.running:
            client_socket, addr = self.server_socket.accept()
            print(f"来自 {addr} 的连接")
            client_socket.sendall("服务器的问候!\n".encode('utf-8'))
            client_socket.close()

    def stop_server(self):
        if self.server_socket:
            self.running = False
            self.server_socket.close()
            print(f"服务器已在端口 {self.port} 停止")

    def change_port(self, new_port):
        self.stop_server()
        self.port = new_port
        self.start_server()

def main():
    port = int(input("请输入要开放的端口: "))
    port_opener = PortOpener(port)
    server_thread = threading.Thread(target=port_opener.start_server)
    server_thread.start()

    while True:
        cmd = input("输入 'change <端口>' 来更改端口，输入 'exit' 来退出: ").strip()
        if cmd.startswith('change'):
            try:
                new_port = int(cmd.split()[1])
                port_opener.change_port(new_port)
            except (IndexError, ValueError):
                print("无效的命令或端口号。")
        elif cmd == 'exit':
            port_opener.stop_server()
            break
        else:
            print("未知命令。")

if __name__ == "__main__":
    main()
