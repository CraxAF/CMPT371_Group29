import socket
import threading
import json
# IP address of the server (localhost by default).
SERVER_IP = "127.0.0.1"
PORT = 5555
# Game state variables
player_n = ""
lobby_code = ""
server_messages = []
player_positions = {}
game_objects = {}
player_passed_door = False
game_pass = False
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
                message_dict = json.loads(msg_json)
                server_messages.append(message_dict)
                #print(f"Received server message: {message_dict}")  # Debugging line

                if message_dict["type"] == "sync_positions":
                    # Update player positions from server for the specific lobby
                    lobby_code = message_dict.get("lobby_code")
                    player_positions[lobby_code] = message_dict["players"]
                    #print(f"Updated player positions: {player_positions[lobby_code]}")
                elif message_dict["type"] == "sync_objects":
                    game_objects[message_dict["lobby_code"]] = message_dict["objects"]
                elif message_dict["type"] == "player_passed_door":
                    print("Player passed the door!")
                    print(f"Player: {message_dict['player']}")
                    print(player_n)
                    if(message_dict["player"] == player_n):
                        global player_passed_door
                        player_passed_door = True
                elif message_dict["type"] == "game_pass":
                    print("game passed!")
                    global game_pass
                    game_pass = True
                    print(game_pass)
        except Exception as e:
            print(f"[-] Error in receiving messages: {e}")
            break

# Connects to the server and sends actions as structured JSON messages
def main(player_name, lobby_code):
    global client_socket  # Access the global variable
    # Create a TCP socket and connect to the server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, PORT))
    global player_n
    player_n = player_name
    message = {"type": "join", "player": player_name, "lobby_code": lobby_code}
    try:
        # Send the join message
        client_socket.sendall((json.dumps(message) + "\n").encode())  # Use json.dumps to send as string
    except Exception as e:
        print(f"[-] Error sending join message: {e}")

    # Start a thread to continuously receive messages from the server
    thread = threading.Thread(target=receive_messages, args=(client_socket,))
    thread.daemon = True  # Allow thread to exit when main program exits
    thread.start()

def send_action(action, player_name, lobby_code, position=None, object_id=None):
    if client_socket is None:
        print("Error: client_socket is None, cannot send action.")
        return
    
    if action == "move" and not player_passed_door:
        message = {
            "type": action,
            "player": player_name,
            "position": position,  
            "lobby_code": lobby_code
        }
        send_message(message)
    elif action == "push" and not player_passed_door:
        message = {
            "type": action,
            "player": player_name,
            "object_id": object_id,
            "position": position,  
            "lobby_code": lobby_code
        }
        send_message(message)

def send_message(message):
    if client_socket is None:
        print("Error: client_socket is None, cannot send message.")
        return
    try:
        message_str = json.dumps(message)  
        client_socket.sendall((message_str + "\n").encode())  # Properly encode the message
    except Exception as e:
        print(f"Socket error: {e}")

if __name__ == "__main__":
    # Main program logic will be handled in game_screen.py
    pass
