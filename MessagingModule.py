import time
import struct
import json
import socket
import threading

class Messager:
    """Module for sending messages"""
    def __init__(self, connections, user):
        self.tcp_port = user.get_tcp_port()
        self.my_nick = user.get_nick()

        self.connections = connections
        self.running = True
        self.socket_timeout = 20
        
        # Queue for TUI thread
        self.message_queue = []
        self.queue_lock = threading.Lock()

    def send_json(self, data: dict, sock):
        """Send JSON data through socket and close it"""
        json_str = json.dumps(data, ensure_ascii=False)
        json_bytes = json_str.encode("utf-8")
        sock.send(struct.pack('!I', len(json_bytes)))
        sock.send(json_bytes)
        sock.close()

    def recv_json(self, sock):
        """Receive JSON data from socket"""
        try:
            sock.settimeout(self.socket_timeout)
            length_data = sock.recv(4)
            if not length_data:
                return None
            length = struct.unpack('!I', length_data)[0]
            
            if length > 1024 * 1024:
                return None
            
            json_bytes = b''
            while len(json_bytes) < length:
                chunk = sock.recv(min(4096, length - len(json_bytes)))
                if not chunk:
                    return None
                json_bytes += chunk
            return json.loads(json_bytes.decode('utf-8'))

        except socket.timeout:
            return None
        except Exception as error:
            print(f"recv_json error: {error}")
            return None

    def send_message(self, message: str, receiver_nick: str):
        """Send message to peer by nickname"""
        # Get receiver info by nick
        peer_info = self.connections.get_by_nick(receiver_nick)
        if not peer_info:
            self._queue_notification(f"User '{receiver_nick}' not found", "error")
            return False
        
        ip, data = peer_info
        tcp_port = data['tcp_port']
        
        # Create connection and send
        try:
            sock = socket.socket()
            sock.settimeout(5)
            sock.connect((ip, tcp_port))

            self.send_json({
                "type": "msg",
                "from": self.my_nick,
                "text": message,
                "timestamp": time.time()
            }, sock)
            
            self._queue_notification(f"Message sent to {receiver_nick}", "success")
            return True

        except socket.timeout:
            self._queue_notification(f"Connection timeout to {receiver_nick}", "error")
            return False
        except Exception as error:
            self._queue_notification(f"Send error: {error}", "error")
            return False

    def get_loop(self):
        """Accept incoming TCP connections"""
        while self.running:
            try:
                conn, addr = self.get_sock.accept()
                handle_loop_thread = threading.Thread(target=self.handle_loop, args=(conn, addr), daemon=True)
                handle_loop_thread.start()
            except Exception as error:
                if self.running:
                    print(f"error get loop: {error}")
                break

    def handle_loop(self, conn, addr: tuple[str, int]):
        """Handle incoming connection and messages"""
        try:
            while self.running:
                msg = self.recv_json(conn)
                if not msg:
                    break
                
                if msg.get("type") == "msg":
                    # Save to history
                    self.connections.history_update(addr[0], msg)
                    # Queue for UI
                    self._queue_message(msg.get('from', 'Unknown'), msg)
                    
        except Exception as error:
            if self.running:
                print(f"handle_loop error: {error}")
        finally:
            conn.close()

    def _queue_message(self, sender: str, msg: dict):
        """Add incoming message to queue for UI"""
        with self.queue_lock:
            self.message_queue.append({
                "type": "message",
                "sender": sender,
                "msg": msg
            })

    def _queue_notification(self, text: str, level: str = "info"):
        """Add notification to queue for UI"""
        with self.queue_lock:
            self.message_queue.append({
                "type": "notification",
                "text": text,
                "level": level
            })

    def get_messages(self):
        """Get all pending messages and clear queue"""
        with self.queue_lock:
            messages = self.message_queue.copy()
            self.message_queue.clear()
            return messages

    def has_messages(self):
        """Check if there are pending messages"""
        with self.queue_lock:
            return len(self.message_queue) > 0

    # Start and stop threads
    def start(self):
        """Start TCP server"""
        self.get_sock = socket.socket()
        self.get_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.get_sock.bind(('', self.tcp_port))
        self.get_sock.listen(5)

        self.get_loop_thread = threading.Thread(target=self.get_loop, daemon=True)
        self.get_loop_thread.start()

    def stop(self):
        print("Messager stopping...")
        self.running = False
        
        if self.get_sock:
            try:
                self.get_sock.close()
            except:
                pass
        
        time.sleep(0.5)
        
        with self.queue_lock:
            self.message_queue.clear()
        
        print("Messager stopped")
