#!/usr/bin/env python3
"""
MLSwarm - Shared text file chat client.

This tool uses a simple, shared text file as a communication channel.
It embodies the core principles of the Magic Launcher Paradigm:
simplicity, speed, and cross-platform compatibility. It is a "peer-to-peer"
system where the "peers" are simply any process with access to the same file.

Part of the ML-Extras suite.
"""

import sys
import time
import os
import threading
from datetime import datetime
from pathlib import Path
import argparse
import getpass  # A more reliable way to get the username

class MLSwarm:
    """
    A class to handle the shared file chat logic.
    """
    def __init__(self, file_path='swarm.txt', nick='anon'):
        self.file_path = Path(file_path)
        self.nick = nick
        self.last_size = 0
        self.running = True
        self.lock = threading.Lock()
    
    def start(self):
        """
        Start a new swarm file, overwriting any existing one.
        """
        try:
            with open(self.file_path, 'w') as f:
                f.write(f"=== Swarm started by {self.nick} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
            print(f"Swarm file started at: {self.file_path}")
        except IOError as e:
            print(f"Error: Could not create file at {self.file_path}. Reason: {e}", file=sys.stderr)
            sys.exit(1)
        
    def send(self, message):
        """
        Append a message to the shared swarm file.
        """
        timestamp = datetime.now().strftime('%H:%M')
        try:
            with self.lock:  # Use a lock to ensure thread-safe file writing
                with open(self.file_path, 'a') as f:
                    f.write(f"[{timestamp}] <{self.nick}> {message}\n")
        except IOError as e:
            print(f"Error: Could not write to file at {self.file_path}. Reason: {e}", file=sys.stderr)

    def get_new_lines(self):
        """
        Get new lines that have been appended to the file since the last check.
        This handles potential race conditions and file changes gracefully.
        """
        if not self.file_path.exists():
            return None
            
        try:
            current_size = self.file_path.stat().st_size
            if current_size == self.last_size:
                return []
            
            # Open in 'rb' mode to handle potential non-UTF-8 characters
            with open(self.file_path, 'rb') as f:
                # Handle file truncation (e.g., if the file was reset by another user)
                if current_size < self.last_size:
                    f.seek(0)
                    self.last_size = 0
                else:
                    f.seek(self.last_size)
                    
                new_content = f.read().decode('utf-8', errors='ignore')
                
            self.last_size = current_size
            
            # Ensure we don't return an empty list if the last read was just a newline
            new_lines = new_content.splitlines()
            return new_lines if new_content.strip() else []
            
        except (IOError, OSError) as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return None
        
    def watch_thread(self):
        """
        The background thread that watches for and prints new messages.
        It uses a lock to ensure terminal output is not corrupted.
        """
        while self.running:
            new_lines = self.get_new_lines()
            if new_lines:
                with self.lock:
                    # Clear the current input line before printing new messages
                    sys.stdout.write('\r' + ' ' * (len(self.nick) + 2) + '\r')
                    print('\n'.join(new_lines))
                    sys.stdout.write(f"{self.nick}> ")
                    sys.stdout.flush()
            
            time.sleep(1)

    def watch(self):
        """
        Interactive watch mode, allowing the user to send and receive messages.
        """
        print(f"Watching {self.file_path} as {self.nick}")
        print("Type messages and press Enter. Type /quit to exit.\n")
        
        # Show existing content on startup
        if self.file_path.exists():
            with open(self.file_path, 'r') as f:
                print(f.read(), end='')
            self.last_size = self.file_path.stat().st_size
        
        # Start the watcher thread
        watcher = threading.Thread(target=self.watch_thread, daemon=True)
        watcher.start()
        
        # Input loop for sending messages
        try:
            while self.running:
                # Use a lock to ensure this print doesn't conflict with the watcher thread
                with self.lock:
                    message = input(f"{self.nick}> ")
                
                if message == '/quit':
                    break
                elif message.strip():
                    self.send(message)
                
        except (KeyboardInterrupt, EOFError):
            pass
        
        self.running = False
        print("\nExiting swarm...")

    def show_history(self):
        """
        Just display the entire contents of the swarm file.
        """
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r') as f:
                    print(f.read())
            except IOError as e:
                print(f"Error: Could not read file at {self.file_path}. Reason: {e}", file=sys.stderr)
        else:
            print(f"No swarm file found at {self.file_path}", file=sys.stderr)

def main():
    """
    Main function for command-line execution.
    """
    parser = argparse.ArgumentParser(
        description="""MLSwarm - Shared text file chat.

A simple, local-only chat client using a shared file.
Employs the Magic Launcher Paradigm of doing one thing well,
without bloat or complex dependencies.
""",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help='Commands')

    # Subparser for the 'start' command
    start_parser = subparsers.add_parser('start', help='Start a new swarm file (will overwrite an existing one)')
    start_parser.add_argument('file', nargs='?', default='swarm.txt', help='The file to use as the swarm')

    # Subparser for the 'watch' command
    watch_parser = subparsers.add_parser('watch', help='Start interactive watch mode')
    watch_parser.add_argument('file', nargs='?', default='swarm.txt', help='The file to use as the swarm')
    watch_parser.add_argument('-n', '--nick', default=getpass.getuser() if getpass.getuser() else 'anon',
                              help='Your nickname in the chat')
    
    # Subparser for the 'send' command
    send_parser = subparsers.add_parser('send', help='Send a single message and exit')
    send_parser.add_argument('message', help='The message to send')
    send_parser.add_argument('file', nargs='?', default='swarm.txt', help='The file to use as the swarm')
    send_parser.add_argument('-n', '--nick', default=getpass.getuser() if getpass.getuser() else 'anon',
                             help='Your nickname in the chat')
    
    # Subparser for the 'history' command
    history_parser = subparsers.add_parser('history', help='Display the full chat history')
    history_parser.add_argument('file', nargs='?', default='swarm.txt', help='The file to use as the swarm')
    
    args = parser.parse_args()
    
    swarm = MLSwarm(args.file, args.nick if 'nick' in args else 'anon')
    
    if args.command == 'start':
        swarm.start()
    elif args.command == 'watch':
        swarm.watch()
    elif args.command == 'send':
        swarm.send(args.message)
    elif args.command == 'history':
        swarm.show_history()

if __name__ == "__main__":
    main()

