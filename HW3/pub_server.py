import zmq
import sys
import time

# In-memory storage for messages
messages = []

def run_server(ip, post_port, pub_port):
    context = zmq.Context()

    # REP socket to receive messages from mc_client.py
    rep_socket = context.socket(zmq.REP)
    rep_socket.bind(f"tcp://{ip}:{post_port}")

    # PUB socket to broadcast messages to subscribers
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind(f"tcp://{ip}:{pub_port}")

    print(f"Server started on {ip} | POST Port: {post_port} | PUB Port: {pub_port}")

    while True:
        try:
            # Receive message from the client
            msg = rep_socket.recv_string()
            
            # Parse the message into channel, username, and body
            channel, username, body = msg.split('|', 2)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            # Add the message to in-memory storage
            messages.append({"channel": channel, "username": username, "time": timestamp, "message": body})

            # Print the message
            print(f"[{timestamp}] #{channel} {username}: {body}")

            # Publish the message to the correct channel
            pub_socket.send_string(f"{channel}|{username}|{body}|{timestamp}")

            # Send an acknowledgment back to the client
            rep_socket.send_string("Message received")

        except KeyboardInterrupt:
            print("\nShutting down the server...")
            break
        except Exception as e:
            print(f"Error: {e}")
            rep_socket.send_string("Error occurred")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python pub_server.py <ip> <post_port> <pub_port>")
        sys.exit(1)

    ip = sys.argv[1]
    post_port = sys.argv[2]
    pub_port = sys.argv[3]

    run_server(ip, post_port, pub_port)
