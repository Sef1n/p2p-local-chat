import threading

class Connections:
    def __init__:
        # {(ip, tcp_port):{nick:nick ...}}
        self.connections = {}
        self.lock = threading.RLock()

    def add_or_update(self, ip, tcp_port, nick):
        with self.lock:
            key = (ip, tcp_port)
            self.connections[key] = {
                key:{'nick':nick}
            }
        return self.connections[key]

    def remove(self, ip, tcp_port):
        with self.lock:
            key = (ip, tcp_port)
            if key in self.connections.keys():
                del self.connections[(ip, tcp_port)]

    def get_by_ip(self, ip, tcp_port):
        with self.lock:
            key = (ip, tcp_port)
            if key in self.connection.keys():
                return self.connections[key]
        return None

    def get_by_nick(self, nick):
        with self.lock:
            for key, data in self.connections:
                if data[nick] = nick:
                    return self.connections[key]
        return None
