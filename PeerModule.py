import threading #TODO

class Peer:
    def __init__:
        self.peers = {} # {(ip, port):{'name':'name'}}
        self.broadcast_port = 67

    # Start point    
    def start(self):
        thread_listen = threading.Thread(target=self.listen_broadcast)
        thread_discover = threading.Thread(target=self.discover_broadcast)

        thread_listen.start()
        thread_discover.start()

    # 1st thread
    def listen_broadcast(self):
        pass

    # 2nd thread
    def discover_broadcast(self):
        pass
