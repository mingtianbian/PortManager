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
        print(f"Server started on port {self.port}")
        self.running = True

        while self.running:
            client_socket, addr = self.server_socket.accept()
            print(f"Connection from {addr}")
            client_socket.sendall(b"Hello from server!\n")
            client_socket.close()

    def stop_server(self):
        if self.server_socket:
            self.running = False
            self.server_socket.close()
            print(f"Server stopped on port {self.port}")

    def change_port(self, new_port):
        self.stop_server()
        self.port = new_port
        self.start_server()

def main():
    port_opener = PortOpener(25565)
    server_thread = threading.Thread(target=port_opener.start_server)
    server_thread.start()

    while True:
        cmd = input("Enter 'change <port>' to change port, 'exit' to quit: ").strip()
        if cmd.startswith('change'):
            try:
                new_port = int(cmd.split()[1])
                port_opener.change_port(new_port)
            except (IndexError, ValueError):
                print("Invalid command or port number.")
        elif cmd == 'exit':
            port_opener.stop_server()
            break
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
