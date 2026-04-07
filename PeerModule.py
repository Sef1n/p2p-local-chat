import threading #TODO
import socket

from ConnectionsModule import Connections

class Peers:
    def __init__(self, udp_port=9999, tcp_port=8000, my_nick):
        self.udp_port = udp_port
        self.tcp_port = tcp_port
        self.my_nick = my_nick
        # ping = f'PING'.encode()



    def get_my_addr(self):
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip

    def listen_broadcast(self):
        ping = f'PING:{self.my_nick}:{self.tcp_port}'.encode()
        pong = f'PONG:{self.my_nick}:{self.tcp_port}'.encode()

        while True:
            # TODO VALIDATE
            data, addr = self.discover_sock.recvform(1024)
            data = data.decode()
            data = data.split(':')

            if data[0] == 'PING':
                # SAY HELLO
                self.discover_sock.send(pong, addr)
            elif data[0] == 'PONG':
                # IP, TCP_PORT, NICK
                Connections.add_or_update(addr[0], data[2], data[1])

    # Start point    
    def start(self):
        self.discover_sock = socket.socket()
        self.discover_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.discover_sock.bind('', self.udp_port)
        # Start discovering
        listen_broadcast()
