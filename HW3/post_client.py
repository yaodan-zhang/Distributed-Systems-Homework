import zmq
import sys

def send_message(ip, port, username, message):
    # Create a ZeroMQ context
    context = zmq.Context()
    socket = context.socket(zmq.REQ)  # REQ = Request
    socket.connect(f"tcp://{ip}:{port}")

    # Format the message
    formatted_message = f"{username}|{message}"

    # Send the message to the server
    socket.send_string(formatted_message)

    # Wait for the server's acknowledgment
    response = socket.recv_string()
    print(f"Server response: {response}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python post_client.py <ip> <port> <username> \"message\"")
        sys.exit(1)

    ip = sys.argv[1]
    port = sys.argv[2]
    username = sys.argv[3]
    message = sys.argv[4]  # Joins all remaining arguments as the message

    send_message(ip, port, username, message)
