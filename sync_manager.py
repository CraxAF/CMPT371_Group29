import json

import pygame

class SyncManager:
    def __init__(self):
        self.sessions = {}         # lobby_code -> list of client sockets
        self.player_positions = {} # lobby_code -> {player_name: {"x": int, "y": int}}
        self.objects = {}
        self.door_state = {}
        self.passed_door = {}

    def broadcast(self, message_dict, sender_socket, lobby_code):
        message_json = json.dumps(message_dict).encode()
        if lobby_code not in self.sessions:
            print(f"[WARN] Tried to broadcast to non-existent lobby: {lobby_code}")
            return
        for client in self.sessions[lobby_code]:
                try:
                    client.sendall(message_json + b"\n")
                except:
                    self.sessions[lobby_code].remove(client)

    def handle_join(self, client_socket, message_dict):
        lobby_code = message_dict.get("lobby_code")
        player_name = message_dict.get("player")
        x, y = 100, 100

        # Initialize structures FIRST
        self.player_positions.setdefault(lobby_code, {})
        self.sessions.setdefault(lobby_code, [])
        self.passed_door.setdefault(lobby_code, {})
        if player_name in self.player_positions[lobby_code]:
            print(f"Player {player_name} already in lobby {lobby_code}")
            return

        self.player_positions[lobby_code][player_name] = {"x": x, "y": y}
        self.sessions[lobby_code].append(client_socket)
        self.passed_door[lobby_code][player_name] = False

        if lobby_code not in self.objects:
            self.objects[lobby_code] = {}
            
            self.objects[lobby_code]["key1"] = {
                "id": "key1",
                "type": "pushable",
                "x": 250,
                "y": 200,
                "possessed_by": None
            }
            self.objects[lobby_code]["door1"] = {
                "id": "door1",
                "type": "door",
                "x": 400,
                "y": 400,
                "locked": True
            }
        self.door_state[lobby_code] = {"door1": False}
        print(f"Player {player_name} joined lobby {lobby_code} at position ({x}, {y})")

        message = {
            "type": "sync_positions",
            "players": self.player_positions[lobby_code],
            "lobby_code": lobby_code
        }
        self.broadcast(message, client_socket, lobby_code)
        self.sync_objects(client_socket, lobby_code)

    def handle_move(self, client_socket, message_dict):
        lobby_code = message_dict.get("lobby_code")
        player_name = message_dict.get("player")
        position = message_dict.get("position")

        if lobby_code in self.player_positions and player_name in self.player_positions[lobby_code]:
            self.player_positions[lobby_code][player_name] = {"x": position[0], "y": position[1]}
        else:
            print(f"Error: Player {player_name} not found in lobby {lobby_code}")
            return

        message = {
            "type": "sync_positions",
            "players": self.player_positions[lobby_code],
            "lobby_code": lobby_code
        }
        self.broadcast(message, client_socket, lobby_code)

    def handle_objects(self, client_socket, message_dict):
        lobby_code = message_dict.get("lobby_code")
        player_name = message_dict.get("player")
        position = message_dict.get("position")
        object_id = message_dict.get("object_id")
        if lobby_code in self.objects and object_id in self.objects[lobby_code]:
            obj = self.objects[lobby_code][object_id]
            obj["x"] = position[0]
            obj["y"] = position[1]
            obj["possessed_by"] = player_name

            # Check if key1 is near the door and unlock the door
            if obj["id"] == "key1":
                door = self.objects[lobby_code].get("door1")
                if door and door["locked"]:
                    if self.is_near(door, obj):
                        door["locked"] = False
                        self.door_state[lobby_code]["door1"] = True
                        print(f"Door {door['id']} unlocked!")
                        del self.objects[lobby_code][object_id]
                        print(f"Key {obj['id']} removed after unlocking the door.")

            # Check if players can pass through the door
            if self.door_state[lobby_code].get("door1", False):
                door = self.objects[lobby_code].get("door1")
                if door and not door["locked"]:
                    # Check if any player walked through the door
                    for player_name, position in self.player_positions[lobby_code].items():
                        player_rect = pygame.Rect(position['x'], position['y'], 50, 50)
                        door_rect = pygame.Rect(door["x"], door["y"], 50, 50)

                        if player_rect.colliderect(door_rect) and self.passed_door[lobby_code][player_name] == False:
                            print(f"Player {player_name} passed through the door!")
                            self.passed_door[lobby_code][player_name] = True
                            message = {
                            "type": "player_passed_door",
                            "player": player_name,
                            "lobby_code": lobby_code,
                            "door_id": door["id"],
                            "passed": True
                            }
                            self.broadcast(message, client_socket, lobby_code)
                            self.check_all_players_passed_door(client_socket, lobby_code)
        self.sync_objects(client_socket, lobby_code)
    
    def check_all_players_passed_door(self, client_socket, lobby_code):
        """Check if all players in the lobby have passed through the door."""
        if lobby_code not in self.passed_door:
            return
        all_passed = True
        for player_name, passed in self.passed_door[lobby_code].items():
            if not passed:
                all_passed = False
                break
        if all_passed:
            # Send a "game pass" message to all clients in the lobby
            message = {
                "type": "game_pass",
                "lobby_code": lobby_code,
                "message": "All players have passed through the door! Game passed!"
            }
            self.broadcast(message, client_socket, lobby_code)

    def is_near(self, door, key):
        """Check if the key is near the door."""
        door_rect = pygame.Rect(door["x"], door["y"], 50, 50)
        key_rect = pygame.Rect(key["x"], key["y"], 50, 50)
        return door_rect.colliderect(key_rect)

    def sync_objects(self, client_socket, lobby_code):
        if lobby_code not in self.objects:
            return
        message = {
            "type": "sync_objects",
            "lobby_code": lobby_code,
            "objects": self.objects[lobby_code]
        }
        self.broadcast(message, client_socket, lobby_code)

    def handle_disconnect(self, client_socket):
        for lobby_code, session in list(self.sessions.items()):
            if client_socket in session:
                session.remove(client_socket)
                if not session:
                    del self.sessions[lobby_code]
                    self.player_positions.pop(lobby_code, None)

