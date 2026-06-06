import socket
import argparse
import time
import sys
import threading
from queue import Queue

from UserModule import User
from PeerModule import Peer
from MessagingModule import Messager
from ConnectionsModule import Connections


def parse_args():
    """Command line args setup"""
    parser = argparse.ArgumentParser(description='Simple p2p chat for CS50 project')
    general = parser.add_argument_group('General options')
    general.add_argument('--nick', '-n', type=str, default=socket.gethostname(), 
                        help='User name (default your hostname: %(default)s)')
    network = parser.add_argument_group('Network options')
    network.add_argument('--udp_port', type=int, default=9999, 
                        help='Udp port (default: %(default)s)')
    network.add_argument('--tcp_port', type=int, default=8000, 
                        help='Tcp_port (default: %(default)s)')
    return parser.parse_args()


def print_help_msg():
    """Print user manual"""
    print("\n" + "=" * 50)
    print("P2P CHAT USER MANUAL")
    print("=" * 50)
    print("\n[COMMANDS]")
    print("  help, h, ?       - Show this help message")
    print("  list, who        - Show list of available users")
    print("  msg <USER> <TEXT> - Send message to user")
    print("  history <USER>   - Show chat history with user")
    print("  quit, q, exit    - Exit chat")
    print("\n[EXAMPLES]")
    print("  msg Vasya Hello, how are you?")
    print("  history Vasya")
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
            # Check if user has unread messages
            history = connections.get_history(nick, limit=1)
            unread = "[NEW]" if history and history[-1].get('direction') == 'in' else ""
            print(f"  {i}. {nick} {unread}")
    
    print("-" * 40 + "\n")


def print_history(connections, nick, limit=50):
    """Print chat history with specific user"""
    history = connections.get_history(nick, limit)
    
    if not history:
        print(f"\n[i] No messages with {nick}")
        return
    
    print(f"\n{'='*50}")
    print(f"HISTORY WITH {nick.upper()} (last {len(history)} messages)")
    print(f"{'='*50}")
    
    for msg in history:
        time_str = time.strftime("%H:%M:%S", time.localtime(msg['timestamp']))
        if msg['direction'] == 'out':
            print(f"[{time_str}] [me]: {msg['text']}")
        else:
            sender = msg.get('from', nick)
            print(f"[{time_str}] [{sender}]: {msg['text']}")
    
    print(f"{'='*50}\n")


def print_notification(text: str, level: str = "info"):
    """Print notification"""
    if level == "error":
        print(f"\n[!] {text}")
    elif level == "success":
        print(f"\n[✓] {text}")
    else:
        print(f"\n[i] {text}")


def print_incoming_message(sender: str, text: str):
    """Print incoming message"""
    print(f"\n[{sender}]: {text}")


def input_thread_function(input_queue):
    """Thread function to read user input"""
    while True:
        try:
            user_input = sys.stdin.readline()
            input_queue.put(user_input.strip())
        except:
            break


def main():
    """Main function"""
    args = parse_args()
    
    # Create objects
    user = User(args.nick, args.tcp_port, args.udp_port)
    connections = Connections()
    peer = Peer(connections, user)
    messager = Messager(connections, user)
    
    # Start modules
    peer.start()
    messager.start()
    
    print_help_msg()
    print_contacts(connections)
    
    # Queue for user input
    input_queue = Queue()
    
    # Start input thread
    input_thread = threading.Thread(target=input_thread_function, args=(input_queue,), daemon=True)
    input_thread.start()
    
    # Main loop
    try:
        while True:
            # Check for incoming messages
            for item in messager.get_messages():
                if item["type"] == "notification":
                    print_notification(item["text"], item["level"])
                elif item["type"] == "message":
                    print_incoming_message(item["sender"], item["msg"]["text"])
                
                # Redraw prompt
                print("\n> ", end="", flush=True)
            
            # Check for user input (non-blocking)
            try:
                user_input = input_queue.get_nowait()
            except:
                user_input = None
            
            if user_input is not None:
                if not user_input:
                    print("> ", end="", flush=True)
                    continue
                
                parts = user_input.split(maxsplit=1)
                cmd = parts[0].lower()
                
                # Help
                if cmd in ['help', 'h', '?']:
                    print_help_msg()
                    print("> ", end="", flush=True)
                
                # List contacts
                elif cmd in ['list', 'who']:
                    print_contacts(connections)
                    print("> ", end="", flush=True)
                
                # Send message
                elif cmd == 'msg':
                    if len(parts) < 2:
                        print("[!] Usage: msg <USER> <TEXT>")
                        print("> ", end="", flush=True)
                        continue
                    
                    subparts = parts[1].split(maxsplit=1)
                    if len(subparts) < 2:
                        print("[!] Usage: msg <USER> <TEXT>")
                        print("> ", end="", flush=True)
                        continue
                    
                    recipient = subparts[0]
                    message = subparts[1]
                    
                    messager.send_message(message, recipient)
                    print("> ", end="", flush=True)
                
                # History
                elif cmd == 'history':
                    if len(parts) < 2:
                        print("[!] Usage: history <USER>")
                        print("> ", end="", flush=True)
                        continue
                    
                    recipient = parts[1]
                    print_history(connections, recipient)
                    print("> ", end="", flush=True)
                
                # Quit
                elif cmd in ['quit', 'q', 'exit']:
                    print("[i] Goodbye!")
                    break
                
                # Unknown command
                else:
                    print(f"[!] Unknown command: '{cmd}'. Type 'help'")
                    print("> ", end="", flush=True)
            
            # Small delay to prevent CPU spinning
            time.sleep(0.05)
                
    except KeyboardInterrupt:
        print("\n[i] Goodbye!")
    except Exception as e:
        print(f"\n[!] Error: {e}")
    finally:
        # Cleanup
        peer.stop()
        messager.stop()


if __name__ == "__main__":
    main()
