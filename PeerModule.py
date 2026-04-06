import threading #TODO
import socket

class Peer:
    def __init__(self, udp_port=0):
        self.udp_port = udp_port
        self.peers = {} # {(ip, port):{'name':'name'}}

    # Start point    
    def start(self):
        self.discover_sock = socket.socket()
        self.discover_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.discover_sock.bind('', self.udp_port)
        # Start discovering
        listen_broadcast()

    def listen_broadcast(self):
        While True:
            data, addr = self.discover_sock.recvform(1024)
            if data = b'PING': #TODO DATA STRUCT
                response = f'PONG {self.my_nick} {self.my_addr}'.encode()
                sock.send(response, addr)
            elif data = b'PONG':
                continue #TODO ADD CONNECTION
