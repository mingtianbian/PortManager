import socket
import threading

class PortOpener:
    def __init__(self, ports):
        self.ports = ports
        self.server_sockets = {}
        self.running = threading.Event()
        self.threads = []

    def start_server(self, port):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_socket.bind(('0.0.0.0', port))
            server_socket.listen(5)
            self.server_sockets[port] = server_socket
            print(f"服务器已在端口 {port} 启动")
        except OSError as e:
            print(f"无法绑定端口 {port}: {e}")
            return

        try:
            while self.running.is_set():
                server_socket.settimeout(1.0)
                try:
                    client_socket, addr = server_socket.accept()
                    print(f"来自 {addr} 的连接到端口 {port}")
                    client_socket.sendall("服务器的问候!\n".encode('utf-8'))
                    client_socket.close()
                except socket.timeout:
                    continue
        except Exception as e:
            print(f"服务器错误在端口 {port}: {e}")

    def start_servers(self):
        self.running.set()
        for port in self.ports:
            thread = threading.Thread(target=self.start_server, args=(port,))
            self.threads.append(thread)
            thread.start()
        # 等待所有服务器线程启动完成
        for thread in self.threads:
            thread.join(0.1)

    def stop_servers(self):
        self.running.clear()
        for port, server_socket in self.server_sockets.items():
            server_socket.close()
        for thread in self.threads:
            thread.join()
        self.server_sockets.clear()
        self.threads.clear()
        print("所有服务器已停止")

    def change_ports(self, new_ports):
        self.stop_servers()
        self.ports = new_ports
        self.start_servers()

    def add_ports(self, additional_ports):
        self.stop_servers()
        self.ports.extend(additional_ports)
        self.ports = list(set(self.ports))  # 去重
        self.start_servers()

    def remove_ports(self, remove_ports):
        self.stop_servers()
        self.ports = [port for port in self.ports if port not in remove_ports]
        self.start_servers()

    def parse_ports(self, ports_input):
        ports = []
        for part in ports_input.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                ports.extend(range(start, end + 1))
            else:
                ports.append(int(part.strip()))
        return ports

def main():
    print("欢迎使用PortManager")
    print("此软件允许您打开和管理端口。")
    ports_input = input("请输入要开放的端口（用逗号分隔，或输入 'all' 开放所有端口）: ")

    if ports_input.lower() == 'all':
        ports = list(range(1, 65536))
    else:
        port_opener = PortOpener([])
        ports = port_opener.parse_ports(ports_input)
    
    port_opener = PortOpener(ports)
    port_opener.start_servers()

    print("""
输入以下命令来管理端口:
- 'add <端口1,端口2,...>' 来增加端口
- 'remove <端口1,端口2,...>' 来删除端口
- 'change <端口1,端口2,...>' 来更改端口
- 'exit' 来退出
    """)

    while True:
        cmd = input().strip()
        if cmd.startswith('change'):
            try:
                ports_input = cmd.split(' ', 1)[1]
                if ports_input.lower() == 'all':
                    new_ports = list(range(1, 65536))
                else:
                    new_ports = port_opener.parse_ports(ports_input)
                port_opener.change_ports(new_ports)
            except (IndexError, ValueError):
                print("无效的命令或端口号。")
        elif cmd.startswith('add'):
            try:
                ports_input = cmd.split(' ', 1)[1]
                additional_ports = port_opener.parse_ports(ports_input)
                port_opener.add_ports(additional_ports)
            except (IndexError, ValueError):
                print("无效的命令或端口号。")
        elif cmd.startswith('remove'):
            try:
                ports_input = cmd.split(' ', 1)[1]
                remove_ports = port_opener.parse_ports(ports_input)
                port_opener.remove_ports(remove_ports)
            except (IndexError, ValueError):
                print("无效的命令或端口号。")
        elif cmd == 'exit':
            port_opener.stop_servers()
            break
        else:
            print("未知命令。")

if __name__ == "__main__":
    main()
