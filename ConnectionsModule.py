import threading
import time

class Connections:
    def __init__(self):
        # {(ip, tcp_port):{nick:nick ...}}
        self.connections = {}
        self.lock = threading.RLock()

    def add_or_update(self, ip, tcp_port, nick, last_ping):
        with self.lock:
            self.connections[ip] = {
                'tcp_port':tcp_port,
                'nick':nick,
                'last_ping':last_ping}
        return self.connections[ip]

    def remove(self, ip, tcp_port):
        with self.lock:
            if ip in self.connections.keys():
                del self.connections[ip]

    def cleanup_stale_connetcions(self):
        with self.lock:
            for key in self.connections:
                if self.connections[key]['last_ping'] - int(time.time()) > 5*60: #MINS
                    del self.connections[key]

    def get_by_ip(self, ip):
        with self.lock:
            if ip in self.connections.keys():
                return self.connections[ip]
        return None

    def get_by_nick(self, nick):
        with self.lock:
            for key, data in self.connections:
                if data[nick] == nick:
                    return self.connections[key]
        return None
