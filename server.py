# server.py
import socket
import threading
import json

# Server will listen on all network interfaces (0.0.0.0) and this port
HOST = "0.0.0.0"
PORT = 5555

# List to store all connected client sockets
clients = []


# Broadcasts a message (in JSON format) to all clients except the sender
def broadcast(message_dict, sender_socket):
    message_json = json.dumps(message_dict).encode()
    for client in clients:
        if client != sender_socket:
            try:
                client.sendall(message_json + b"\n")
            except:
                clients.remove(client)  # Remove clients that failed


# Handles incoming messages from a specific client
def handle_client(client_socket, addr):
    print(f"[+] New connection from {addr}")
    buffer = ""  # Used to store incomplete message data
    while True:
        try:
            data = client_socket.recv(1024).decode()  # Receive message chunk
            if not data:
                break  # No data means the client has disconnected
            buffer += data  # Accumulate data in buffer
            while "\n" in buffer:
                # Split the buffer at newline to process complete JSON messages
                msg_json, buffer = buffer.split("\n", 1)
                message_dict = json.loads(msg_json)  # Decode JSON string to dict
                print(f"[RECV from {addr}] {message_dict}")
                broadcast(message_dict, client_socket)  # Relay message to others
        except:
            break  # On error (e.g., client force quit), exit loop

    # Cleanup after client disconnects
    print(f"[-] Connection from {addr} closed.")
    clients.remove(client_socket)
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
