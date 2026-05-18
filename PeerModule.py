import threading #TODO
import socket
import time

class Peer:
    def __init__(self, connections, user):
        self.udp_port = user.get_udp_port()
        self.tcp_port = user.get_tcp_port()
        self.connections = connections
        self.running = False

        self.my_nick = user.get_my_nick()

        self.ping = f'PING'.encode()
        self.pong = f'PONG:{self.tcp_port}:{self.my_nick}'.encode()
        self.bye = f'BYE'.encode()

    def listen_broadcast(self):
        while self.running:
            data, addr = self.sock.recvfrom(1024)
            # VALIDATE
            try:
                data = data.decode()
                data = data.split(':')
            except OSError:
                break
            except UnicodeDecodeError:
                continue
            except Exception as error:
                if self.running:
                    print(f'ERROR {error}')

            if not data:
                continue
            if data[0] == 'PING':
                # SAY HELLO
                self.sock.sendto(self.pong, addr)
            elif data[0] == 'BYE':
                self.connections.remove(addr[0])
            elif data[0] == 'PONG' and len(data) == 3:
                # IP, TCP_PORT, NICK
               self.connections.add_or_update(addr[0], data[1], data[2], int(time.time()))

    def discover_broadcast(self):
        while self.running:
            self.sock.sendto(self.ping, ('255.255.255.255', self.udp_port))
            self.connections.cleanup_stale_connections()
            time.sleep(20)

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(('', self.udp_port))
        # PING
        self.ping_thread = threading.Thread(target=self.discover_broadcast, daemon=True) # Ends with main
        # PONG
        self.listen_thread = threading.Thread(target=self.listen_broadcast, daemon=True)
        # Start
        self.running = True
        self.ping_thread.start()
        self.listen_thread.start()

    def stop(self):
        print('PEER stopping')
        self.running = False
        try:
            # SAY BYE
            self.sock.sendto(self.bye, ('255.255.255.255', self.udp_port))
        except:
            pass
        try:
            self.sock.close()
        except:
            pass
        # DAEMONS
#        if self.ping_thread and self.ping_thread.is_alive():
#            self.ping_thread.join(timeout=2.0)
#        
#        if self.listen_thread and self.listen_thread.is_alive():
#            self.listen_thread.join(timeout=2.0)
        print('[Peer] stopped')
