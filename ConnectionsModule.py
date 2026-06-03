import threading
import time

class Connections:
    """Table for storing a list of connections"""
    def __init__(self):
        """{ip : {tcp_port:tcp_port,
                  nick:nick,
                  last_ping:last_ping,
                  history:[history, ...]}}"""
        self.connections = {}
        self.lock = threading.RLock()

    # UPDATE 
    def add_or_update(self, ip: str, tcp_port: int, nick: str, last_ping) -> dict:
        with self.lock:
            self.connections[ip] = {
                'tcp_port':tcp_port,
                'nick':nick,
                'last_ping':last_ping,
                'history':[]}
        return self.connections[ip]

    def history_update(self, ip: str, msg: dict):
        with self.lock:
            self.connections[ip]['history'].append(msg)

    # DELETE
    def remove(self, ip: str):
        with self.lock:
            if ip in self.connections.keys():
                del self.connections[ip]

    def cleanup_stale_connections(self):
        with self.lock:
            for key in self.connections:
                if self.connections[key]['last_ping'] - int(time.time()) > 5*60: #MINS
                    del self.connections[key]

    # SELECT
    def get_by_ip(self, ip) -> tuple[str, dict] | None:
        with self.lock:
            if ip in self.connections.keys():
                return (ip, self.connections[ip])
        return None

    def get_by_nick(self, nick: str) -> tuple[str, dict] | None:
        with self.lock:
            for key, data in self.connections:
                if data[nick] == nick:
                    return (key, self.connections[key])
        return None

