import zmq
import sys
import threading

def receive_messages(ip, pub_port):
    """ Listens for messages from the PUB channel and prints them correctly. """
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{ip}:{pub_port}")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all messages

    while True:
        try:
            message = socket.recv_string()
            username, body, timestamp = message.split('|', 2)

            # Move cursor up and clear line before printing message
            print(f"\r{username}: {body} ({timestamp})\n> ", end="", flush=True)

        except KeyboardInterrupt:
            break

def send_messages(ip, post_port, username):
    """ Sends user input messages to the server. """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://{ip}:{post_port}")

    while True:
        try:
            message = input("> ")  # User types a message
            if message.strip().lower() == "exit":
                print("Exiting chat...")
                break
            
            formatted_message = f"{username}|{message}"
            socket.send_string(formatted_message)

            # Wait for the server's acknowledgment
            response = socket.recv_string()
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python interactive_client.py <ip> <post_port> <pub_port> <name>")
        sys.exit(1)

    ip = sys.argv[1]
    post_port = sys.argv[2]
    pub_port = sys.argv[3]
    username = sys.argv[4]

    print(f"Connected to chat as '{username}'. Type 'exit' to leave.")

    # Create threads for sending and receiving messages
    receiver_thread = threading.Thread(target=receive_messages, args=(ip, pub_port), daemon=True)
    sender_thread = threading.Thread(target=send_messages, args=(ip, post_port, username))

    # Start both threads
    receiver_thread.start()
    sender_thread.start()

    # Wait for sender thread to finish (receiver thread runs as a daemon)
    sender_thread.join()
    print("Chat client closed.")
