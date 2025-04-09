# client.py
import socket
import threading
import json
import sys

# IP address of the server (localhost by default).
# Change this to the actual server IP when running on different machines.
SERVER_IP = "127.0.0.1"
PORT = 5555

# Game state
player_n = ""
client_socket = None
server_messages = []
player_positions = {}  # player_name -> position
game_objects = {}
player_passed_door = False
game_pass = False

def receive_messages(sock):
    global player_passed_door, game_pass
    buffer = ""
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                break
            buffer += data
            while "\n" in buffer:
                msg_json, buffer = buffer.split("\n", 1)
                message_dict = json.loads(msg_json)
                server_messages.append(message_dict)

                if message_dict["type"] == "sync_positions":
                    global player_positions
                    player_positions = message_dict["players"]

                elif message_dict["type"] == "sync_objects":
                    global game_objects
                    game_objects = message_dict["objects"]

                elif message_dict["type"] == "player_passed_door":
                    print("Player passed the door:", message_dict["player"])
                    if message_dict["player"] == player_n:
                        player_passed_door = True

                elif message_dict["type"] == "game_pass":
                    print("All players passed the door!")
                    game_pass = True

        except Exception as e:
            print("[-] Disconnected from server.")
            break

def get_player_position():
    global player_positions 
    return player_positions

def get_game_objects():
    global game_objects
    return game_objects

def get_player_passed_door():
    global player_passed_door
    return player_passed_door

def get_game_pass():
    global game_pass
    return game_pass

# Connects to the server and sends actions as structured JSON messages
def main(player_name):
    global client_socket, player_n
    player_n = player_name

    # Create a TCP socket and connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))

    # Send join message
    join_msg = {
        "type": "join",
        "player": player_name
    }
    client_socket.sendall((json.dumps(join_msg) + "\n").encode())

    # Start a thread to continuously receive messages from the server
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

def send_action(action, player_name, possessed_by, object_id=None, position=None):
    if client_socket is None or player_passed_door:
        return

    if action == "move":
        message = {
            "type": "move",
            "player": player_name,
            "position": position
        }
        send_message(message)

    elif action == "push":
        message = {
            "type": "push",
            "player": player_name,
            "possessed_by": possessed_by,
            "object_id": object_id,
            "position": position
        }
        send_message(message)

def send_message(message):
    try:
        message_str = json.dumps(message)
        client_socket.sendall((message_str + "\n").encode())
    except Exception as e:
        print(f"[!] Send error: {e}")

# Entry point of the client script
if __name__ == "__main__":
    pass 
