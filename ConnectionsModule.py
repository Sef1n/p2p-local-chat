import threading
import time

class Connections:
    """Table for storing a list of connections and chat history"""
    
    def __init__(self):
        """
        Structure of self.connections:
        {
            ip: {
                'tcp_port': int,
                'nick': str,
                'last_seen': int,  # timestamp of last PONG
                'history': []      # list of messages
            }
        }
        """
        self.connections = {}
        self.lock = threading.RLock()
        self.pending_messages = []  # queue of new messages 

    # ============ UPDATE ============
    
    def add_or_update(self, ip: str, tcp_port: int, nick: str, last_seen: int) -> dict:
        """Add or update a peer in the table"""
        with self.lock:
            if ip in self.connections:
                # Update existing peer
                self.connections[ip]['tcp_port'] = tcp_port
                self.connections[ip]['nick'] = nick
                self.connections[ip]['last_seen'] = last_seen
            else:
                # Add new peer
                self.connections[ip] = {
                    'tcp_port': tcp_port,
                    'nick': nick,
                    'last_seen': last_seen,
                    'history': []
                }
            return self.connections[ip]

    def history_update(self, ip: str, msg: dict):
        """Add a message to chat history with a specific IP"""
        with self.lock:
            if ip in self.connections:
                self.connections[ip]['history'].append(msg)
                # Add to queue for UI
                self.pending_messages.append((self.connections[ip]['nick'], msg))
            else:
                # Peer not in table (e.g., not yet discovered)
                print(f"Warning: Tried to update history for unknown IP {ip}")

    def update_last_seen(self, ip: str, timestamp: int):
        """Update last contact timestamp for a peer"""
        with self.lock:
            if ip in self.connections:
                self.connections[ip]['last_seen'] = timestamp

    # ============ DELETE ============
    
    def remove(self, ip: str):
        """Remove a peer by IP"""
        with self.lock:
            if ip in self.connections:
                nick = self.connections[ip]['nick']
                del self.connections[ip]
                print(f"[Connections] Removed {nick} ({ip})")
                return nick
        return None

    def remove_by_nick(self, nick: str):
        """Remove a peer by nickname"""
        with self.lock:
            for ip, data in list(self.connections.items()):
                if data['nick'] == nick:
                    del self.connections[ip]
                    print(f"[Connections] Removed {nick} ({ip})")
                    return ip
        return None

    def cleanup_stale_connections(self, timeout_seconds: int = 300):
        """Remove peers that haven't sent PONG for more than timeout_seconds (default 5 minutes)"""
        with self.lock:
            now = int(time.time())
            stale = []
            for ip, data in self.connections.items():
                if now - data['last_seen'] > timeout_seconds:
                    stale.append(ip)
            
            for ip in stale:
                nick = self.connections[ip]['nick']
                del self.connections[ip]
                print(f"[Connections] Cleaned up stale connection: {nick} ({ip})")
            
            return len(stale)

    # ============ SELECT ============
    
    def get_by_ip(self, ip: str) -> tuple[str, dict] | None:
        """Return (ip, data) for a given IP"""
        with self.lock:
            if ip in self.connections:
                return (ip, self.connections[ip].copy())
        return None

    def get_by_nick(self, nick: str) -> tuple[str, dict] | None:
        """Return (ip, data) for a given nickname"""
        with self.lock:
            for ip, data in self.connections.items():
                if data['nick'] == nick:
                    return (ip, data.copy())
        return None

    def get_all(self) -> dict:
        """Return a copy of all connections"""
        with self.lock:
            return self.connections.copy()

    def get_all_nicks(self) -> list:
        """Return a list of all online peer nicknames"""
        with self.lock:
            return [data['nick'] for data in self.connections.values()]

    def get_history(self, nick: str) -> list:
        """Return chat history with a specific user by nickname"""
        with self.lock:
            for ip, data in self.connections.items():
                if data['nick'] == nick:
                    return data['history'].copy()
        return []

    def get_history_by_ip(self, ip: str) -> list:
        """Return chat history with a specific user by IP"""
        with self.lock:
            if ip in self.connections:
                return self.connections[ip]['history'].copy()
        return []

    # ============ QUEUE FOR TUI ============
    
    def get_pending_messages(self) -> list:
        """Return and clear the queue of new messages for UI"""
        with self.lock:
            messages = self.pending_messages.copy()
            self.pending_messages.clear()
            return messages

    def has_pending_messages(self) -> bool:
        """Check if there are new messages pending"""
        with self.lock:
            return len(self.pending_messages) > 0

    # ============ UTILS ============
    
    def size(self) -> int:
        """Return the number of active connections"""
        with self.lock:
            return len(self.connections)

    def is_online(self, nick: str) -> bool:
        """Check if a peer with given nickname is online"""
        with self.lock:
            for data in self.connections.values():
                if data['nick'] == nick:
                    return True
            return False
