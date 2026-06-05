import socket
import time
import argparse
import sys

from UserModule import User
from PeerModule import Peer
from MessagingModule import Messager
from ConnectionsModule import Connections
from InputHandler import InputHandler

def parse_args():
    """Command line args setup"""
    parser = argparse.ArgumentParser(description='Simple p2p chat for CS50 project')
    # General opts
    general = parser.add_argument_group('General options')
    general.add_argument('--nick', '-n', type=str, default=socket.gethostname(), help='User name (default your hostname: %(default)s)')
    # Network opts
    network = parser.add_argument_group('Network options')
    network.add_argument('--udp-port', type=int, default=9999, help='Udp port (default: %(default)s)')
    network.add_argument('--tcp-port', type=int, default=8000, help='Tcp port (default: %(default)s)')

    return parser.parse_args()

def print_help_msg():
    """Print user manual / help message"""
    print("\n" + "=" * 50)
    print("P2P CHAT USER MANUAL")
    print("=" * 50)
    
    print("\n[COMMANDS]")
    print("  help, h, ?        - Show this help message")
    print("  list, who         - Show list of available users")
    print("  msg <USER> <TEXT> - Send message to user")
    print("  history <USER>    - Show chat history with user")
    # print("  nick <NEW_NICK>  - Change your nickname")
    print("  unread, new       - Show list of unread messages")
    print("  quit, q, exit     - Exit chat")
    
    print("\n[NAVIGATION]")
    # print("  Up/Down arrows   - Navigate through message history")
    print("  Ctrl+C            - Force exit")
    
    print("\n[EXAMPLES]")
    print("  msg Vasya Hello, how are you?")
    print("  history Vasya")
    print("  nick CoolGuy")
    
    print("\n" + "=" * 50 + "\n")

def print_contacts(connections):
    """Print list of available contacts"""
    contacts = connections.get_all_nicks()
    
    print("\n" + "-" * 40)
    print(f"ONLINE USERS ({len(contacts)}):")
    print("-" * 40)
    
    if not contacts:
        print("  No users online")
    else:
        for i, nick in enumerate(contacts, 1):
            print(f"  {i}. {nick}")
    
    print("-" * 40 + "\n")

def print_history(connections, nick, limit=20):
    """Print chat history with specific user"""
    history = connections.get_history(nick)
    
    if not history:
        print(f"\nNo messages with {nick}\n")
        return
    
    print("\n" + "=" * 50)
    print(f"HISTORY WITH {nick.upper()}")
    print("=" * 50)
    
    # Show last N messages
    start = max(0, len(history) - limit)
    for msg in history[start:]:
        sender = msg.get('from', 'Unknown')
        text = msg.get('text', '')
        timestamp = msg.get('timestamp', 0)
        
        # Format time
        if timestamp:
            time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
        else:
            time_str = "??:??:??"
        
        # Mark outgoing messages
        direction = "→" if sender == "me" else "←"
        print(f"[{time_str}] {direction} {sender}: {text}")
    
    print("=" * 50 + "\n")

def print_message_status(success, recipient):
    """Print message sending status"""
    if success:
        print(f"[OK] Message sent to {recipient}")
    else:
        print(f"[ERROR] Failed to send message to {recipient}")

def print_unread_messages(connections):
    """Print list of unread messages"""
    unread = connections.get_unread_count()
    
    print("\n" + "-" * 40)
    print("UNREAD MESSAGES:")
    print("-" * 40)
    
    if not unread:
        print("  No unread messages")
    else:
        for nick, count in unread.items():
            print(f"  {nick}: {count} new message(s)")
    
    print("-" * 40 + "\n")

def print_error(msg: str):
    """Print error message"""
    print(f"[ERROR] {msg}")


def print_info(msg: str):
    """Print info message"""
    print(f"[INFO] {msg}")


def print_success(msg: str):
    """Print success message"""
    print(f"[OK] {msg}")

def main():
    args = parse_args()
    
    user = User(args.nick, args.tcp_port, args.udp_port)
    connections = Connections()
    peer = Peer(connections, user)
    messager = Messager(connections, user)
    
    # Start modules
    peer.start()
    messager.start()
    
    # Simple input handler
    input_handler = InputHandler(messager)
    input_handler.start()
    
    print_help_msg()
    sys.stdout.write("> ")
    sys.stdout.flush()
    
    # Main loop
    while True:
        try:
            user_input = input_handler.get_input()
            
            if user_input is None:
                time.sleep(0.1)
                continue
            
            if not user_input:
                sys.stdout.write("> ")
                sys.stdout.flush()
                continue
            
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            
            if cmd in ['help', 'h', '?']:
                print_help_msg()
            
            elif cmd in ['list', 'who']:
                print_contacts(connections)
            
            elif cmd == 'msg':
                if len(parts) < 2:
                    print("[!] Usage: msg <USER> <TEXT>")
                else:
                    subparts = parts[1].split(maxsplit=1)
                    if len(subparts) < 2:
                        print("[!] Usage: msg <USER> <TEXT>")
                    else:
                        recipient = subparts[0]
                        message = subparts[1]
                        messager.send_message(message, recipient)
            
            elif cmd == 'history':
                if len(parts) < 2:
                    print("[!] Usage: history <USER>")
                else:
                    print_history(connections, parts[1])
            
            elif cmd in ['quit', 'q', 'exit']:
                print("[i] Goodbye!")
                break
            
            else:
                print(f"[!] Unknown command: '{cmd}'. Type 'help'")
            
            sys.stdout.write("> ")
            sys.stdout.flush()
                
        except KeyboardInterrupt:
            print("\n[i] Goodbye!")
            break
        except Exception as e:
            print(f"[!] Error: {e}")
            sys.stdout.write("> ")
            sys.stdout.flush()
    
    # Cleanup
    peer.stop()
    messager.stop()
    input_handler.stop()

if __name__ == "__main__":
    main()
