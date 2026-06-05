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
                'last_seen': int,
                'history': []      # list of messages
            }
        }
        """
        self.connections = {}
        self.lock = threading.RLock()
        self.pending_messages = []

    # ============ UPDATE ============
    
    def add_or_update(self, ip: str, tcp_port: int, nick: str, last_seen: int) -> dict:
        """Add or update a peer in the table"""
        with self.lock:
            if ip in self.connections:
                self.connections[ip]['tcp_port'] = int(tcp_port)
                self.connections[ip]['nick'] = nick
                self.connections[ip]['last_seen'] = last_seen
            else:
                self.connections[ip] = {
                    'tcp_port': int(tcp_port),
                    'nick': nick,
                    'last_seen': last_seen,
                    'history': []  # Will store both incoming and outgoing
                }
            return self.connections[ip]

    def add_message_to_history(self, ip: str, text: str, direction: str, timestamp: float):
        """Add message to peer's history (both sides)"""
        with self.lock:
            if ip in self.connections:
                if timestamp is None:
                    timestamp = time.time()
                
                self.connections[ip]['history'].append({
                    'text': text,
                    'timestamp': timestamp,
                    'direction': direction  # 'in' or 'out'
                })

    def history_update(self, ip: str, msg: dict):
        """Add incoming message to history"""
        with self.lock:
            if ip in self.connections:
                text = msg.get('text', '')
                timestamp = msg.get('timestamp', time.time())
                sender = msg.get('from', 'Unknown')
                
                self.connections[ip]['history'].append({
                    'text': text,
                    'timestamp': timestamp,
                    'direction': 'in',
                    'from': sender
                })
                
                # Queue for UI
                self.pending_messages.append((self.connections[ip]['nick'], msg))

    def add_outgoing_message(self, nick: str, text: str):
        """Record outgoing message in history"""
        with self.lock:
            timestamp = time.time()
            for ip, data in self.connections.items():
                if data['nick'] == nick:
                    data['history'].append({
                        'text': text,
                        'timestamp': timestamp,
                        'direction': 'out',
                        'to': nick
                    })
                    break

    # ============ DELETE ============
    
    def remove(self, ip: str):
        """Remove a peer by IP"""
        with self.lock:
            if ip in self.connections:
                nick = self.connections[ip]['nick']
                del self.connections[ip]
                return nick
        return None

    def remove_by_nick(self, nick: str):
        """Remove a peer by nickname"""
        with self.lock:
            for ip, data in list(self.connections.items()):
                if data['nick'] == nick:
                    del self.connections[ip]
                    return ip
        return None

    def cleanup_stale_connections(self, timeout_seconds: int = 300):
        """Remove peers that haven't sent PONG for more than timeout_seconds"""
        with self.lock:
            now = int(time.time())
            stale = []
            for ip, data in self.connections.items():
                if now - data['last_seen'] > timeout_seconds:
                    stale.append(ip)
            
            for ip in stale:
                nick = self.connections[ip]['nick']
                del self.connections[ip]
                print(f"[Connections] Cleaned up stale connection: {nick}")
            
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

    def get_history(self, nick: str, limit: int = 50) -> list:
        """Return chat history with a specific user by nickname"""
        with self.lock:
            for ip, data in self.connections.items():
                if data['nick'] == nick:
                    history = data['history'].copy()
                    if limit:
                        history = history[-limit:]
                    return history
        return []

    def get_full_conversation(self, nick: str) -> list:
        """Return formatted conversation with timestamps"""
        history = self.get_history(nick)
        if not history:
            return []
        
        formatted = []
        for msg in history:
            time_str = time.strftime("%H:%M:%S", time.localtime(msg['timestamp']))
            if msg['direction'] == 'out':
                formatted.append(f"[{time_str}] [me]: {msg['text']}")
            else:
                formatted.append(f"[{time_str}] [{msg.get('from', nick)}]: {msg['text']}")
        return formatted

    # ============ QUEUE FOR UI ============
    
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
