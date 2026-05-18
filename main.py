from UserModule import User
from PeerModule import Peer
from MessagingModule import Message
from ConnectionsModule import Connections

def main():
    nick = "flush" # Argv?

    whoami = User(nick)
    connections = Connections()
    peer = Peer(connections, whoami)
    message = Message(connections, whoami)

    peer.start()
    return 0

if __name__ == "main":
    main()
