# simple_input.py
import sys
import threading
import time
import queue

class InputHandler:
    """Simpler input handler using queue for messages"""
    
    def __init__(self, messager):
        self.messager = messager
        self.input_queue = queue.Queue()
        self.running = True
        self.input_thread = None
    
    def _input_loop(self):
        """Thread function to read input"""
        while self.running:
            try:
                user_input = sys.stdin.readline()
                if user_input:
                    self.input_queue.put(user_input.strip())
            except:
                break
    
    def _print_message(self, text, prefix="[i]"):
        """Print message without breaking input"""
        # Save cursor position
        sys.stdout.write('\r\033[K')  # Clear line
        print(f"{prefix} {text}")
        sys.stdout.write("> ")
        sys.stdout.flush()
    
    def start(self):
        """Start input thread"""
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()
    
    def get_input(self):
        """Get user input (non-blocking)"""
        # Check for incoming messages
        for item in self.messager.get_messages():
            if item["type"] == "notification":
                prefix = "[!]" if item["level"] == "error" else "[✓]" if item["level"] == "success" else "[i]"
                self._print_message(item["text"], prefix)
            elif item["type"] == "message":
                self._print_message(f"{item['sender']}: {item['msg']['text']}")
        
        # Check for user input
        try:
            return self.input_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop(self):
        """Stop input handler"""
        self.running = False
