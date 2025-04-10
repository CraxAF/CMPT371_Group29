import json
import pygame
from sprites import *
from config import *

class SyncManager:
    def __init__(self):
        self.clients = []                    # List of client sockets
        self.player_positions = {}  # player_name -> {x, y}
        self.objects = {}  # object_id -> {type, x, y, possessed_by}
        self.spawn_points = []
        self.next_object_id = 1                   # object_id -> object data
        self.door_unlocked = []
        self.passed_door = {}                # player_name -> bool
        self.socket_map = {}                 # player_name -> client_socket
        self.key_number = 0
        self.door_number = 0
        self.floor_number = 0
        self.wall_number = 0
        self.initialize_map()
        
        
    def broadcast(self, message_dict, sender_socket=None):
        message_json = json.dumps(message_dict).encode()
        for client in list(self.clients):
            try:
                client.sendall(message_json + b"\n")
            except:
                self.clients.remove(client)

    def initialize_map(self):
        from config import tile_map  # Import tile_map here
        for i, row in enumerate(tile_map):
            for j, tile in enumerate(row):
                x, y = j , i 
                if tile == "B":
                    self.objects[f"wall{self.wall_number}"] = {"id":f"wall{self.wall_number}","type": "wall", "x": x, "y": y}
                    self.wall_number += 1
                elif tile == "D":
                    self.objects[f"door{self.door_number}"] = {"id":f"door{self.door_number}","type": "door", "x": x, "y": y, "locked": True}
                    self.door_number += 1
                elif tile == "K":
                    self.objects[f"key{self.key_number}"] = {"id":f"key{self.key_number}","type": "key", "x": x, "y": y, "possessed_by": None}
                    self.key_number += 1
                elif tile == ".":
                    self.objects[f"floor{self.floor_number}"] = {"id":f"floor{self.floor_number}","type": "floor", "x": x, "y": y}
                    self.floor_number += 1
                elif tile == "P":
                    self.spawn_points.append((x, y))
        self.sync_objects()

    def handle_join(self, client_socket, message_dict):
        player_name = message_dict.get("player")
        if player_name in self.player_positions:
            print(f"Player {player_name} already joined.")
            return

        # Lazily initialize map on first player join
        if not self.player_positions:
            print("First player joined — initializing map.")
            self.initialize_map()

        # Assign spawn position
        if self.spawn_points:
            x, y = self.spawn_points[len(self.player_positions) % len(self.spawn_points)]
        else:
            x, y = 100, 100  # Fallback

        # Register player
        self.clients.append(client_socket)
        
        self.player_positions[player_name] = {"x": x, "y": y}
        self.passed_door[player_name] = False
        self.socket_map[player_name] = client_socket

        print(f"Player {player_name} joined the game at ({x}, {y})")

        # Sync state to all clients
        self.broadcast({
            "type": "sync_positions",
            "players": self.player_positions
        })
        self.sync_objects()


    def handle_move(self, client_socket, message_dict):
        player_name = message_dict.get("player")
        position = message_dict.get("position")
        sprite_counter = message_dict.get("sprite_counter")
        if player_name in self.player_positions:
            if sprite_counter is None:
                sprite_counter = self.player_positions[player_name]["sprite_counter"]
            self.player_positions[player_name] = {"x": position[0], "y": position[1], "sprite_counter": sprite_counter}
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
        type_ = message_dict.get("type")
        if object_id not in self.objects:
            return
        if(type_ == "key"):
            obj = self.objects[object_id]
            obj["possessed_by"] = possessed_by

        if(type_ == "unlock"):
            self.objects[object_id]["locked"] = False

        if(type_ == "delete_key"):
            print(f"Deleting key {object_id}")
            del self.objects[object_id]


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

        self.initialize_map()
