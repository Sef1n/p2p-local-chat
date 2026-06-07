import socket

class User:
    def __init__(self, nick: str, tcp_port: int, udp_port: int):
        self.sock = socket.socket()
        self.hostname = socket.gethostname()
        self.local_ip = socket.gethostbyname(self.hostname)

        self.nick = nick
        self.tcp_port = tcp_port 
        self.udp_port = udp_port

    def get_hostname(self):
        return self.hostname

    def get_local_ip(self):
        return self.local_ip

    def get_nick(self):
        return self.nick

    def get_tcp_port(self):
        return self.tcp_port

    def get_udp_port(self):
        return self.udp_port

