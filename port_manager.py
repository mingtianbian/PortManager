import socket
import threading
import logging
import re

# 配置日志记录，保存到文件
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='port_manager.log', filemode='a')

def get_local_ips():
    ipv4 = []
    ipv6 = []
    hostname = socket.gethostname()
    try:
        for info in socket.getaddrinfo(hostname, None):
            family, _, _, _, sockaddr = info
            if family == socket.AF_INET:
                ip = sockaddr[0]
                if ip not in ipv4:
                    ipv4.append(ip)
            elif family == socket.AF_INET6:
                ip = sockaddr[0]
                if ip not in ipv6:
                    ipv6.append(ip)
    except Exception as e:
        logging.error(f"获取本地IP地址时出错: {e}")
    return ipv4, ipv6

class PortOpener:
    def __init__(self, ports):
        self.ports = ports
        self.server_sockets = {}
        self.running = threading.Event()
        self.threads = []
        self.started_ports = set()

    def start_server(self, port, family):
        if family == socket.AF_INET:
            bind_addr = '0.0.0.0'
            family_label = 'IPv4'
        else:
            bind_addr = '::'
            family_label = 'IPv6'

        server_socket = socket.socket(family, socket.SOCK_STREAM)
        try:
            server_socket.bind((bind_addr, port))
            server_socket.listen(5)
            self.server_sockets[(port, family)] = server_socket
            logging.info(f"服务器已在端口 {port} ({family_label}) 启动")
        except OSError as e:
            logging.error(f"无法绑定端口 {port} ({family_label}): {e}")
            return

        try:
            while self.running.is_set():
                server_socket.settimeout(1.0)
                try:
                    client_socket, addr = server_socket.accept()
                    logging.info(f"来自 {addr} 的连接到端口 {port} ({family_label})")
                    client_socket.sendall(f"服务器的问候! 你连接的是 {family_label} 服务\n".encode('utf-8'))
                    client_socket.close()
                except socket.timeout:
                    continue
        except Exception as e:
            logging.error(f"服务器错误在端口 {port} ({family_label}): {e}")

    def start_servers(self):
        self.running.set()
        for port in self.ports:
            thread_ipv4 = threading.Thread(target=self.start_server, args=(port, socket.AF_INET))
            self.threads.append(thread_ipv4)
            thread_ipv4.start()

            thread_ipv6 = threading.Thread(target=self.start_server, args=(port, socket.AF_INET6))
            self.threads.append(thread_ipv6)
            thread_ipv6.start()

        for thread in self.threads:
            thread.join(0.1)

    def stop_servers(self):
        self.running.clear()
        for (port, family), server_socket in self.server_sockets.items():
            server_socket.close()
        for thread in self.threads:
            thread.join()
        self.server_sockets.clear()
        self.threads.clear()
        self.started_ports.clear()
        logging.info("所有服务器已停止")

    def change_ports(self, new_ports):
        self.stop_servers()
        self.ports = new_ports
        self.start_servers()

    def add_ports(self, additional_ports):
        self.ports.extend(additional_ports)
        self.ports = list(set(self.ports))
        self.stop_servers()
        self.start_servers()

    def remove_ports(self, remove_ports):
        self.ports = [port for port in self.ports if port not in remove_ports]
        self.stop_servers()
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
- 'log(l)' 查看当前日志内容
- 'help(h)' 来显示帮助信息
- 'exit' 来退出
    """)

def main():
    print("欢迎使用PortManager (支持IPv4和IPv6) v1.3.2")
    print("此软件允许您打开和管理端口。")

    ipv4_list, ipv6_list = get_local_ips()
    print("本机 IPv4 地址:", ", ".join(ipv4_list) if ipv4_list else "无")
    print("本机 IPv6 地址:", ", ".join(ipv6_list) if ipv6_list else "无")

    ports_input = input("请输入要开放的端口（用逗号分隔，或输入 'all' 开放所有端口）: ")

    if ports_input.lower() == 'all':
        ports = list(range(1, 65536))
    else:
        ports = PortOpener.parse_ports(ports_input)

    port_opener = PortOpener(ports)
    port_opener.start_servers()

    print_help()

    while True:
        cmd = input().strip()
        if cmd.lower() in ('add', 'a', 'remove', 'r', 'change', 'c'):
            print("请提供端口参数，例如: add 80")
            continue

        if cmd.lower().startswith(('add ', 'a ')):
            _, ports_input = cmd.split(' ', 1)
            ports = PortOpener.parse_ports(ports_input)
            port_opener.add_ports(ports)
        elif cmd.lower().startswith(('remove ', 'r ')):
            _, ports_input = cmd.split(' ', 1)
            ports = PortOpener.parse_ports(ports_input)
            port_opener.remove_ports(ports)
        elif cmd.lower().startswith(('change ', 'c ')):
            _, ports_input = cmd.split(' ', 1)
            ports = PortOpener.parse_ports(ports_input)
            port_opener.change_ports(ports)
        elif cmd.lower() in ('log', 'l'):
            try:
                with open('port_manager.log', 'rb') as f:
                    content = f.read()
                    try:
                        decoded = content.decode('utf-8')
                        print("\n==== 日志内容 ====")
                        print(decoded)
                        print("==== 日志结束 ====")
                    except UnicodeDecodeError:
                        decoded = content.decode('gbk', errors='replace')
                        print("\n==== 日志内容 (非UTF-8，尝试按本地编码解码) ====")
                        print(decoded)
                        print("==== 日志结束 ====")
            except FileNotFoundError:
                print("当前没有日志文件。")
        elif cmd.lower() in ('help', 'h'):
            print_help()
        elif cmd.lower() == 'exit':
            port_opener.stop_servers()
            break
        else:
            print("未知命令。输入 'help' 或 'h' 查看帮助。")

if __name__ == "__main__":
    main()