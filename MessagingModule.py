class Message:
    def __init__(self, nick, tcp_port=0):
        self.tcp_port = tcp_port #TODO ERROO tcp_port == udp_port
        self.nick = nick
 
    def start(self):
        self.data_sock = socket.socket()
        self.data_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.data_sock.bind('', self.tcp_port)
 
    # 1st thread
    def listen_broadcast(self):
        While True:
            data, addr = self.discover_sock.recvform(1024)
            if data = b'PING':
                response = f'PONG {self.my_nick} {self.my_addr}'.encode()
                sock.send(response, addr)
 
 
