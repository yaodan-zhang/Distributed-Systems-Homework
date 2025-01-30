import zmq
import sys
import threading

def receive_messages(ip, pub_port, channel):
    """ Listens for messages from the PUB channel and prints them correctly. """
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{ip}:{pub_port}")

    # Subscribe only to the specified channel, or to all if "ALL" is selected
    if channel == "ALL":
        socket.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all messages
    else:
        socket.setsockopt_string(zmq.SUBSCRIBE, f"{channel}|")  # Subscribe only to this channel

    print(f"Subscribed to #{channel}. Waiting for messages...\n")

    while True:
        try:
            message = socket.recv_string()
            msg_channel, username, body, timestamp = message.split('|', 3)

            # Print only messages from the subscribed channel
            print(f"\r#{msg_channel} {username}: {body} ({timestamp})\n> ", end="", flush=True)

        except KeyboardInterrupt:
            print("\nExiting chat...")
            break

def send_messages(ip, post_port, channel, username):
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
            
            formatted_message = f"{channel}|{username}|{message}"
            socket.send_string(formatted_message)

            # Wait for the server's acknowledgment
            response = socket.recv_string()
        except KeyboardInterrupt:
            print("\nExiting chat...")
            break

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python mc_client.py <ip> <post_port> <pub_port> <channel> <name>")
        sys.exit(1)

    ip = sys.argv[1]
    post_port = sys.argv[2]
    pub_port = sys.argv[3]
    channel = sys.argv[4]  # The channel the user is joining
    username = sys.argv[5]

    print(f"Connected to #{channel} as '{username}'. Type 'exit' to leave.")

    # Create and start the receive thread (always needed)
    receiver_thread = threading.Thread(target=receive_messages, args=(ip, pub_port, channel))
    receiver_thread.start()

    # Only start the send thread if the user is NOT in "ALL"
    if channel != "ALL":
        sender_thread = threading.Thread(target=send_messages, args=(ip, post_port, channel, username))
        sender_thread.start()
        sender_thread.join()  # Wait for user to exit chat before closing

    receiver_thread.join()

    print("Chat client closed.")
