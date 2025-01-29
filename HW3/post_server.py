import zmq
import sys
import time

# In-memory storage for messages
messages = []

def run_server(ip, port):
    # Create a ZeroMQ context
    context = zmq.Context()
    socket = context.socket(zmq.REP)  # REP = Reply
    socket.bind(f"tcp://{ip}:{port}")

    print(f"Server started at {ip}:{port}")

    while True:
        try:
            # Receive message from the client
            msg = socket.recv_string()
            
            # Parse the message into username and body
            username, body = msg.split('|', 1)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # Add the message to the in-memory data structure
            messages.append({"username": username, "time": timestamp, "message": body})

            # Print the received message
            print(f"[{timestamp}] {username}: {body}")

            # Send an acknowledgment back to the client
            socket.send_string("Message received")
        except KeyboardInterrupt:
            print("\nShutting down the server...")
            break
        except Exception as e:
            print(f"Error: {e}")
            socket.send_string("Error occurred")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python post_server.py <ip> <port>")
        sys.exit(1)

    ip = sys.argv[1]
    port = sys.argv[2]

    run_server(ip, port)
