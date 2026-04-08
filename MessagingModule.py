import socket

class Message:
    def __init__(self, connections, user):
        self.my_ip = user.get_local_ip()
        self.tcp_port = user.get_tcp_port()
        self.my_nick = user.get_nick()

        self.connections = connections
 
    def start(self):
        self.data_sock = socket.socket()
        self.data_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.data_sock.bind(('', self.tcp_port))
