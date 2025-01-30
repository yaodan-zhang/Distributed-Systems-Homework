import zmq
import sys

def subscribe(ip, port):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{ip}:{port}")

    # Subscribe to all messages (empty string means "subscribe to everything")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    print(f"Subscribed to {ip}:{port}. Waiting for messages...\n")

    while True:
        try:
            # Receive a message from the publisher
            message = socket.recv_string()
            
            # Extract username, message body, and timestamp
            username, body, timestamp = message.split('|', 2)

            # Print formatted message
            print(f"{username}: {body} ({timestamp})")

        except KeyboardInterrupt:
            print("\nSubscriber shutting down...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pub_client.py <ip> <pub_port>")
        sys.exit(1)

    ip = sys.argv[1]
    pub_port = sys.argv[2]

    subscribe(ip, pub_port)
