import json
import pygame

class SyncManager:
    def __init__(self):
        self.clients = []                    # List of client sockets
        self.player_positions = {}           # player_name -> {"x": int, "y": int}
        self.objects = {}                    # object_id -> object data
        self.door_unlocked = False
        self.passed_door = {}                # player_name -> bool
        self.socket_map = {}                 # player_name -> client_socket

    def broadcast(self, message_dict, sender_socket=None):
        message_json = json.dumps(message_dict).encode()
        for client in list(self.clients):
            try:
                client.sendall(message_json + b"\n")
            except:
                self.clients.remove(client)

    def handle_join(self, client_socket, message_dict):
        player_name = message_dict.get("player")
        x, y = 100, 100

        if player_name in self.player_positions:
            print(f"Player {player_name} already joined.")
            return

        self.clients.append(client_socket)
        self.player_positions[player_name] = {"x": x, "y": y}
        self.passed_door[player_name] = False
        self.socket_map[player_name] = client_socket
        if not self.objects:
            self.objects["key1"] = {
                "id": "key1",
                "type": "pushable",
                "x": 800,
                "y": 800,
                "possessed_by": None
            }
            self.objects["door1"] = {
                "id": "door1",
                "type": "door",
                "x": 400,
                "y": 400,
                "locked": True
            }

        print(f"Player {player_name} joined the game at ({x}, {y})")

        self.broadcast({
            "type": "sync_positions",
            "players": self.player_positions
        })
        self.sync_objects()

    def handle_move(self, client_socket, message_dict):
        player_name = message_dict.get("player")
        position = message_dict.get("position")

        if player_name in self.player_positions:
            self.player_positions[player_name] = {"x": position[0], "y": position[1]}
        else:
            print(f"Error: Player {player_name} not found")
            return

        self.broadcast({
            "type": "sync_positions",
            "players": self.player_positions
        })

    def handle_objects(self, client_socket, message_dict):
        player_name = message_dict.get("player")
        position = message_dict.get("position")
        object_id = message_dict.get("object_id")
        possessed_by = message_dict.get("possessed_by")

        if object_id not in self.objects:
            return

        obj = self.objects[object_id]
        obj["x"] = position[0]
        obj["y"] = position[1]
        obj["possessed_by"] = possessed_by

        if object_id == "key1":
            door = self.objects.get("door1")
            if door and door["locked"] and self.is_near(door, obj):
                door["locked"] = False
                self.door_unlocked = True
                print("Door unlocked!")
                del self.objects["key1"]
                print("Key removed after unlocking the door.")

        if self.door_unlocked:
            door = self.objects.get("door1")
            if door:
                for pname, pos in self.player_positions.items():
                    player_rect = pygame.Rect(pos["x"], pos["y"], 50, 50)
                    door_rect = pygame.Rect(door["x"], door["y"], 50, 50)
                    if player_rect.colliderect(door_rect) and not self.passed_door[pname]:
                        print(f"Player {pname} passed through the door!")
                        self.passed_door[pname] = True
                        self.broadcast({
                            "type": "player_passed_door",
                            "player": pname,
                            "door_id": door["id"],
                            "passed": True
                        })
                        self.check_all_players_passed_door()

        self.sync_objects()

    def check_all_players_passed_door(self):
        if all(self.passed_door.values()):
            self.broadcast({
                "type": "game_pass",
                "message": "All players passed through the door!"
            })

    def is_near(self, door, key):
        door_rect = pygame.Rect(door["x"], door["y"], 50, 50)
        key_rect = pygame.Rect(key["x"], key["y"], 50, 50)
        return door_rect.colliderect(key_rect)

    def sync_objects(self):
        self.broadcast({
            "type": "sync_objects",
            "objects": self.objects
        })

    def handle_disconnect(self, client_socket):
        if client_socket in self.clients:
            self.clients.remove(client_socket)

        # Find the player name associated with this socket
        disconnected_player = None
        for name, sock in self.socket_map.items():
            if sock == client_socket:
                disconnected_player = name
                del self.socket_map[name]
                break

        if disconnected_player:
            print(f"Player {disconnected_player} disconnected.")
            
            # Remove player from position and door tracking
            del self.player_positions[disconnected_player]
            if disconnected_player in self.passed_door:
                del self.passed_door[disconnected_player]

            # Release any objects they were possessing
            for obj in self.objects.values():
                if obj.get("possessed_by") == disconnected_player:
                    obj["possessed_by"] = None

            # Check if no players remain and reset the game state
            if not self.player_positions:  # If no players are left
                print("No players remaining. Resetting the game state.")
                self.reset_game_state()

            # Broadcast updated game state
            self.broadcast({
                "type": "sync_positions",
                "players": self.player_positions
            })
            self.sync_objects()

    def reset_game_state(self):
        """Reset all game data, objects, and status for a fresh start."""
        # Clear player positions
        self.player_positions.clear()

        # Reset door and other game objects
        self.objects.clear()
        self.door_unlocked = False
        self.passed_door.clear()

        # Optionally, reinitialize the objects (if necessary)
        self.objects["key1"] = {
            "id": "key1",
            "type": "pushable",
            "x": 800,
            "y": 800,
            "possessed_by": None
        }
        self.objects["door1"] = {
            "id": "door1",
            "type": "door",
            "x": 400,
            "y": 400,
            "locked": True
        }
        print("Game state reset complete.")

