# client.py
import socket
import threading
import json
import sys

# IP address of the server (localhost by default).
# Change this to the actual server IP when running on different machines.
SERVER_IP = "127.0.0.1"
PORT = 5555


# Receives and processes incoming messages from the server
def receive_messages(sock):
    buffer = ""  # Used to handle cases where messages come in parts
    while True:
        try:
            data = sock.recv(1024).decode()  # Receive data from server
            if not data:
                break  # Server closed connection
            buffer += data
            while "\n" in buffer:
                msg_json, buffer = buffer.split("\n", 1)
                message_dict = json.loads(msg_json)  # Parse JSON into dictionary

                # Display the message
                sys.stdout.write(f"\r[Server] {message_dict}\n")

                # Reprint input prompt cleanly
                sys.stdout.write("Enter action (e.g., move, pickup_key): ")
                sys.stdout.flush()
        except:
            print("[-] Disconnected from server.")
            break


# Connects to the server and sends actions as structured JSON messages
def main():
    # Create a TCP socket and connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))

    # Get the player name from input
    player_name = input("Enter your player name: ")

    # Start a thread to continuously receive messages from the server
    thread = threading.Thread(target=receive_messages, args=(client_socket,))
    thread.start()

    # Loop to continuously send player actions to the server
    while True:
        action = input("Enter action (e.g., move, pickup_key): ")
        message = {"type": action, "player": player_name}
        # Encode message as JSON and send with newline delimiter
        client_socket.sendall((json.dumps(message) + "\n").encode())


# Entry point of the client script
if __name__ == "__main__":
    main()
