# server.py
import socket
import threading
import json
from sync_manager import SyncManager

# Server will listen on all network interfaces (0.0.0.0) and this port
HOST = "0.0.0.0"
PORT = 5555

sm = SyncManager()  # Single global game state

# Handles incoming messages from a specific client
def handle_client(client_socket, addr):
    print(f"[+] New connection from {addr}")
    buffer = "" # Used to store incomplete message data
    try:
        while True:
            data = client_socket.recv(1024).decode() # Receive message chunk
            if not data:
                break  # No data means the client has disconnected
            buffer += data  # Accumulate data in buffer
            while "\n" in buffer:
                # Split the buffer at newline to process complete JSON messages
                msg_json, buffer = buffer.split("\n", 1)
                try:
                    message_dict = json.loads(msg_json) # Decode JSON string to dict
                    msg_type = message_dict.get("type")
                    if msg_type == "join":
                        sm.handle_join(client_socket, message_dict)
                    elif msg_type == "move":
                        sm.handle_move(client_socket, message_dict)
                    elif msg_type == "push":
                        sm.handle_objects(client_socket, message_dict)
                    else:
                        print(f"[!] Unknown message type: {msg_type}")
                except json.JSONDecodeError as e:
                    print(f"[!] JSON decode error: {e}")
    except Exception as e:
        print(f"[!] Client error: {e}")
    finally:
        # Cleanup after client disconnects
        print(f"[-] Disconnected: {addr}")
        sm.handle_disconnect(client_socket)
        client_socket.close()

# Starts the server and listens for new connections
def start_server():
    # Create a TCP socket using IPv4
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))  # Bind the socket to host and port
    server.listen()  # Start listening for incoming client connections
    print(f"[SERVER] Listening on {HOST}:{PORT}")

    while True:
        # Accept a new client connection
        client_socket, addr = server.accept()
        # Handle each client in its own thread
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()

# Entry point of the server script
if __name__ == "__main__":
    start_server()
