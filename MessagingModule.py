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

    def send_json(self, data: dict, sock):
        # STR -> JSON -> BYTES
        json_str = json.dumps(data, ensure_ascii=False)
        json_bytes = json_str.encode("utf-8")
        sock.send(struct.pack('!I', len(json_bytes)))
        sock.send(json_bytes)
        sock.close()

    def recv_json(self, sock):
        # BYTES -> JSON DICT
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
            print("recv_json timeout")
            return None

        except Exception as error:
            print(f"recv_json error: {error}")
            return None

    def send_message(self, message: str, receiver: tuple[str, int]):
        # Create connection
        try:
            sock = socket.socket()
            sock.settimeout(5)
            sock.connect(receiver)

            self.send_json({
                "type": "msg",
                "from": self.my_nick,
                "text": message,
                "timestamp": time.time()
            }, sock)

            return True

        except socket.timeout:
            print(f"Connection timeout in send_message")
            return False

        except Exception as error:
            print(f"Send error: {error}")
            return False

    def get_loop(self):
        # Accept connections
        while self.running:
            try:
                conn, addr = self.get_sock.accept()
                handle_loop_thread = threading.Thread(target=self.handle_loop, args=(conn, addr), daemon=True)
                handle_loop_thread.start()
            except Exception as error:
                print(f"error get loop: {error}")
                break

    def handle_loop(self, conn, addr: tuple[str, int]):
        # Get and Add msg in hist
        try:
            while True:
                msg = self.recv_json(conn)
                if not msg:
                    break
                self.connections.history_update(addr[0], msg)
                print(f"new msg:\n {msg}")

        except Exception as error:
            print(f"handle_loop error: {error}")
        finally:
            conn.close()
                
    # Start and stop threads
    def start(self):
        self.get_sock = socket.socket()
        self.get_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.get_sock.bind(('', self.tcp_port))
        self.get_sock.listen(5)

        self.get_loop_thread = threading.Thread(target=self.get_loop, daemon=True)
        self.get_loop_thread.start()

    def stop(self):
        self.running = False
        if self.get_sock:
            self.get_sock.close()
