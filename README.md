使用说明

1.启动软件：
运行程序时，会显示欢迎消息和简短描述。
程序会提示用户输入要开放的端口。

2.更改端口：
在程序运行时，可以输入change <port>来更改服务器监听的端口。

3.停止服务器：
输入exit可以停止服务器并退出程序。

运行示例
$ python port_manager.py
Welcome to PortManager
This software allows you to open and manage ports.
Please enter the port to open: 25565
Server started on port 25565
Enter 'change <port>' to change port, 'exit' to quit:

在运行过程中，可以使用telnet或nc来测试服务器。当更改端口时，输入相应命令，服务器会重新启动在新端口上。
