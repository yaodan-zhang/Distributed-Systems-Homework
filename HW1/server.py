import socket
import pickle
import sys

# Define constants for the game
GRID_SIZE = 3

class GameState:
    def __init__(self):
        self.board = [[" " for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.current_turn = None
        self.winner = None

    def check_winner(self):
        # Check rows, columns, and diagonals
        for i in range(GRID_SIZE):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != " ":
                self.winner = self.board[i][0]
                return
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != " ":
                self.winner = self.board[0][i]
                return

        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            self.winner = self.board[0][0]
            return
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            self.winner = self.board[0][2]
            return

        # Check for draw
        if all(self.board[row][col] != " " for row in range(GRID_SIZE) for col in range(GRID_SIZE)):
            self.winner = "Draw"

    def make_move(self, player, row, col):
        if self.winner:
            return f"Game over. Winner: {self.winner}"
        if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
            return f"Move ({row}, {col}) is invalid because it is out of bounds."
        if self.board[row][col] != " ":
            return f"Move ({row}, {col}) is invalid because the position is already occupied."
        if (self.current_turn != None) and (player != self.current_turn):
            return f"It is not {player}'s turn."
        
        self.board[row][col] = player
        self.check_winner()
        if self.winner == None:
            if self.current_turn == None:
                if player == "X":
                    self.current_turn = "O"
                else:
                    self.current_turn = "X"

            else:
                if self.current_turn == "X":
                    self.current_turn = "O"
                else:
                    self.current_turn = "X"
        return None

    def restart(self):
        self.__init__()

# Server Code
def server(port):
    game_state = GameState()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", port))
    server_socket.listen(5)
    print(f"Server listening on port {port}...")

    while True:
        client_socket, _ = server_socket.accept()
        data = client_socket.recv(1024)
        request = pickle.loads(data)

        if request["type"] == "move":
            error = game_state.make_move(request["player"], *request["coordinate"])
            response = {"board": game_state.board, "error": error, "winner": game_state.winner}
        elif request["type"] == "restart":
            game_state.restart()
            response = {"board": game_state.board, "message": "Game has been restarted."}

        client_socket.send(pickle.dumps(response))
        client_socket.close()

if __name__ == "__main__":
    port = int(sys.argv[1])
    server(port)