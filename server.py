# server.py
import socket
import threading
import json
from sync_manager import SyncManager

# Server will listen on all network interfaces (0.0.0.0) and this port
HOST = "0.0.0.0"
PORT = 5555

sm = SyncManager()  # Initialize the sync manager

# List to store all connected client sockets
clients = []

# Broadcasts a message (in JSON format) to all clients except the sender
def broadcast(message_dict, sender_socket, lobby_code):
    message_json = json.dumps(message_dict).encode()
    for client in sm.sessions[lobby_code]:
        try:
            client.sendall(message_json+ b"\n")
        except:
            sm.sessions[lobby_code].remove(client)  # Remove clients that failed

def handle_client(client_socket, addr):
    print(f"[+] New connection from {addr}")
    buffer = ""  # Used to store incomplete message data
    try:
        while True:
            data = client_socket.recv(1024).decode()  # Receive message chunk
            if not data:
                break  # No data means the client has disconnected
            buffer += data  # Accumulate data in buffer

            while "\n" in buffer:
                msg_json, buffer = buffer.split("\n", 1)
                #print(f"Buffer split: {msg_json}")  # Debugging line
                try:
                    message_dict = json.loads(msg_json)  # Decode JSON string to dict
                    #print(f"[RECV from {addr}] {message_dict}")  # Debugging line
                    
                    if message_dict["type"] == "join":
                        sm.handle_join(client_socket, message_dict)
                    elif message_dict["type"] in ["move", "action"]:
                        sm.handle_move(client_socket, message_dict)
                    elif message_dict["type"] == "push":
                        sm.handle_objects(client_socket, message_dict)
                    else:
                        print(f"Unknown message type received: {message_dict['type']}")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON message: {e}")
                    continue  # Skip invalid messages and keep listening
    except Exception as e:
        print(f"Error in client connection: {e}")
    finally:
        # Cleanup after client disconnects
        print(f"[-] Connection from {addr} closed.")
        clients.remove(client_socket)
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
        clients.append(client_socket)

        # Handle each client in its own thread
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()


# Entry point of the server script
if __name__ == "__main__":
    start_server()
