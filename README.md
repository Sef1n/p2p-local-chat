# P2P Local Chat

#### Video Demo: <https://youtu.be/>

#### GitHub: sef1n
#### edX: Sef1n
#### City & Country: Minsk, Belarus
#### Date: June 7, 2026

## Description

**P2P Local Chat** is a peer-to-peer messaging application for local networks that allows users to communicate directly without a central server. The project demonstrates core networking concepts, multi-threading, and distributed systems principles within a practical chat application.

Unlike traditional chat applications that rely on central servers, this implementation uses UDP broadcast for peer discovery and TCP connections for reliable message delivery. This approach showcases fundamental distributed systems patterns including service discovery, direct peer-to-peer communication, and decentralized architecture.

### Key Features

- **Peer Discovery** - Automatic detection of other chat instances on the same local network using UDP broadcast
- **Direct Messaging** - One-to-one private messaging using TCP connections
- **Chat History** - Persistent message history for each conversation (in-memory for current session)
- **Terminal User Interface** - Simple command-line interface with real-time message notifications
- **Cross-Platform** - Works on Windows and Linux

### How It Works

The application consists of several modules that work together:

**PeerModule.py** - Handles peer discovery via UDP broadcast:
- Each node periodically sends PING messages to the broadcast address
- Other nodes respond with PONG containing their nickname and TCP port
- Nodes maintain a table of active peers with timestamps
- Stale connections (no response for 5 minutes) are automatically removed

**MessagingModule.py** - Manages message exchange:
- TCP server listens for incoming messages on a configurable port
- Message protocol uses JSON with length prefix (4 bytes) for framing
- Outgoing messages open new connections (simpler than connection pooling)
- Incoming messages are queued for the UI thread

**ConnectionsModule.py** - Stores peer data and chat history:
- Thread-safe dictionary mapping IP addresses to peer information
- Maintains message history with timestamps and direction (incoming/outgoing)
- Provides methods for peer lookup by nickname or IP
- Queue system for delivering new messages to the UI

**UserModule.py** - Simple data container for user information:
- Stores nickname and network configuration (UDP/TCP ports)

**main.py** - User interface and command dispatch:
- Command-line interface with asynchronous message handling
- Separate input thread to avoid blocking on Windows
- Commands: list, msg, history, help, quit

### Technical Highlights

1. **Binary Protocol Design** - Messages are sent with a 4-byte length prefix followed by JSON data, allowing proper message framing over TCP streams.

2. **Thread Safety** - All shared data structures are protected with threading locks to prevent race conditions in multi-threaded environment.

3. **Graceful Shutdown** - Nodes send BYE messages when exiting, allowing other peers to clean up stale connections.

4. **Error Resilience** - Timeout mechanisms prevent hanging connections and zombie threads.

### File Structure
project/
├── main.py # Main entry point, CLI interface, command dispatch
├── UserModule.py # User class with nickname and port configuration
├── PeerModule.py # UDP discovery, PING/PONG broadcast mechanism
├── MessagingModule.py # TCP message sending/receiving, JSON protocol
├── ConnectionsModule.py # Peer storage, chat history, thread-safe operations
└── README.md # Project documentation

### Design Decisions

**Why UDP for discovery and TCP for messaging?**  
UDP supports broadcast which is essential for peer discovery on the local network. TCP provides reliable, ordered delivery for actual messages, which is important for chat applications.

**Why new TCP connection per message instead of persistent connections?**  
For a learning project, this simplifies the code significantly. TCP handshake overhead is negligible on local networks (1-2ms per message), and the simpler implementation reduces potential bugs. Future versions could implement connection pooling for better performance.

**Why JSON instead of a binary protocol?**  
JSON is human-readable, easy to debug, and cross-platform. The overhead is acceptable for a chat application. The protocol includes a length prefix for proper message framing over TCP.

**Why in-memory history instead of persistent storage?**  
The course scope focuses on networking concepts. Persistent storage could be added as an extension using SQLite.

### Challenges Encountered

1. **Windows select() limitation** - On Windows, `select.select()` doesn't work with `sys.stdin`. This was solved by using a separate input thread with a queue.

2. **Broadcast behavior** - UDP broadcast requires the `SO_BROADCAST` socket option and sending to the `255.255.255.255` address.

3. **Thread synchronization** - Multiple threads accessing the peer table required proper locking to prevent dictionary modification during iteration.

### Future Improvements

- **Persistent history** - Store chat history in SQLite database for cross-session persistence
- **File transfer** - Extend the protocol to support sending files alongside text messages
- **Shortcut commands** - Send messages by number (e.g., `msg 1 hello`) instead of full nickname
- **Connection pooling** - Reuse TCP connections for better performance
- **End-to-end encryption** - Add message encryption for privacy
- **Group chats** - Support multi-user conversations
- **Push notifications** - Notify users of new messages when terminal is idle

### How to Use

1. **Run the application:**
   ```bash
   python main.py --nick YourName
2. **Optional parameters**:
   ```bash
   python main.py --nick YourName --tcp_port 8000 --udp_port 9999
3. **Commands**:

        list / who - Show all online users

        msg <nick> <text> - Send a message to a user

        history <nick> - Show chat history with a user

        help - Display help message

        quit / exit - Exit the application

### Requirements

 - Python 3.7+
 - No external dependencies (uses only standard library)

### Acknowledgments

This project was developed as the final project for CS50x. It demonstrates understanding of:

 - Network programming (sockets, UDP, TCP)
 - Multi-threading and synchronization
 - Protocol design
 - Command-line interface design
 - Distributed systems concepts

The project was tested on Linux and Windows 10, ensuring cross-platform compatibility.
