import socket
import argparse
import curses

from UserModule import User
from PeerModule import Peer
from MessagingModule import Messager
from ConnectionsModule import Connections

def parse_args():
    """Command line args setup"""
    parser = argparse.ArgumentParser(description='Simple p2p chat for CS50 project')
    # General opts
    general = parser.add_argument_group('General options')
    general.add_argument('--nick', '-n', type=str, default=socket.gethostname(), help='User name (default your hostname: %(default)s)')
    # Network opts
    network = parser.add_argument_group('Network options')
    network.add_argument('--udp_port', type=int, default=9999, help='Udp port (default: %(default)s)')
    network.add_argument('--tcp_port', type=int, default=8000, help='Tcp_port (default: %(default)s)')

    return parser.parse_args()

def main():
    stdscr = curses.initscr()

    args = parse_args()
    user = User(args.nick, args.tcp_port, args.udp_port)
    connections = Connections()
    peer = Peer(connections, user)
    messager = Messager(connections, user)

    peer.start()
    messager.start()

    while True:
        pass
    exit(0)
 
if __name__ == "__main__":
    main()
