import socket
import pickle
import sys
# Client Code
def client(port, player, command):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", port))

    if command == "restart":
        request = {"type": "restart"}
    else:
        coordinate = tuple(map(int, command.strip("()").split(",")))
        request = {"type": "move", "player": player, "coordinate": coordinate}

    client_socket.send(pickle.dumps(request))
    response = pickle.loads(client_socket.recv(1024))
    client_socket.close()

    if "error" in response and response["error"]:
        print(response["error"])
    else:
        for row in response["board"]:
            print(" | ".join(row))
        if response.get("winner"):
            print(f"Game over! Winner: {response['winner']}")
    if "message" in response:
        print(response["message"])

if __name__ == "__main__":
    port = int(sys.argv[1])
    
    if len(sys.argv)>3:
        player = sys.argv[2]
        command = sys.argv[3]
        client(port, player, command)
    # Restart the Game.
    else:
        player = None
        command = sys.argv[2]
        client(port, player, command)
