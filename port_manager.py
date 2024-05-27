import socket
import threading
import logging
import re

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
            logging.info(f"服务器已在端口 {port} 启动")
        except OSError as e:
            logging.error(f"无法绑定端口 {port}: {e}")
            return

        try:
            while self.running.is_set():
                server_socket.settimeout(1.0)
                try:
                    client_socket, addr = server_socket.accept()
                    logging.info(f"来自 {addr} 的连接到端口 {port}")
                    client_socket.sendall("服务器的问候!\n".encode('utf-8'))
                    client_socket.close()
                except socket.timeout:
                    continue
        except Exception as e:
            logging.error(f"服务器错误在端口 {port}: {e}")

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
        logging.info("所有服务器已停止")

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

    @staticmethod
    def parse_ports(ports_input):
        ports = set()
        for part in ports_input.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                ports.update(range(start, end + 1))
            else:
                ports.add(int(part.strip()))
        return list(ports)

def print_help():
    print("""
输入以下命令来管理端口:
- 'add(a) <端口1,端口2,...>' 来增加端口
- 'remove(r) <端口1,端口2,...>' 来删除端口
- 'change(c) <端口1,端口2,...>' 来更改端口
- 'help(h)' 来显示帮助信息
- 'exit' 来退出
    """)

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

    print_help()

    command_pattern = re.compile(r'^(add|a|remove|r|change|c)\s+(.*)$', re.IGNORECASE)
    while True:
        cmd = input().strip()
        if command_pattern.match(cmd):
            action, ports_input = command_pattern.findall(cmd)[0]
            try:
                ports_input = ports_input.strip()
                if ports_input.lower() == 'all':
                    ports = list(range(1, 65536))
                else:
                    ports = port_opener.parse_ports(ports_input)
                if action.lower() in ('change', 'c'):
                    port_opener.change_ports(ports)
                elif action.lower() in ('add', 'a'):
                    port_opener.add_ports(ports)
                elif action.lower() in ('remove', 'r'):
                    port_opener.remove_ports(ports)
            except (IndexError, ValueError):
                logging.error("无效的命令或端口号。")
        elif cmd.lower() in ('help', 'h'):
            print_help()
        elif cmd.lower() == 'exit':
            port_opener.stop_servers()
            break
        else:
            logging.warning("未知命令。输入 'help' 或 'h' 查看帮助。")

if __name__ == "__main__":
    main()
