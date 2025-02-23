# use node.py to start your node as specified.
import sys
import json
import threading
from flask import Flask, request, jsonify

# In-memory data structure for storing topics and messages
class MessageQueue:
    def __init__(self):
        self.data = {}  # Dictionary with topic names as keys and lists of messages as values
    
    def create_topic(self, topic):
        if topic in self.data:
            return False
        self.data[topic] = []
        return True
    
    def add_message(self, topic, message):
        if topic not in self.data:
            return False
        self.data[topic].append(message)
        return True
    
    def pop_message(self, topic):
        if (topic not in self.data) or (len(self.data[topic]) == 0):
            return False, ""
        return True, self.data[topic].pop(0)
    
    def get_topics(self) -> list:
        return list(self.data.keys())

# Flask app setup
app = Flask(__name__)
message_queue = MessageQueue()

@app.route('/topic', methods=['PUT'])
def create_topic():
    data = request.get_json()
    if (not data) or ('topic' not in data):
        return jsonify({"success": False, "error": "Missing 'topic' field"}), 400
    
    topic = data.get('topic')
    success = message_queue.create_topic(topic)
    if success:
        return jsonify({"success": True}), 200
    return jsonify({"success": False, "error": "Topic already exists"}), 409 # HTTP Code: 409 Topic eixists.

@app.route('/topic', methods=['GET'])
def get_topics():
    return jsonify({"success": True, "topics": message_queue.get_topics()}), 200 # Test: empty list

@app.route('/message', methods=['PUT'])
def add_message():
    data = request.get_json()
    if (not data) or ('topic' not in data) or ('message' not in data):
        return jsonify({"success": False, "error": "Missing 'topic' field or 'data' field"}), 400
    
    topic = data.get('topic')
    message = data.get('message')
    success = message_queue.add_message(topic, message)
    if success:
        return jsonify({"success": True}), 200
    return jsonify({"success": False, "error": "Topic does not exist"}), 410 # HTTP Code: Topic doesn't exist

@app.route('/message/<topic>', methods=['GET'])
def get_message(topic):
    success, message = message_queue.pop_message(topic)
    if success:
        return jsonify({"success": True, "message": message}), 200
    return jsonify({"success": False, "error": "Topic does not exist or there are no messages in the topic"}), 400

'''
@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(raft_node.get_status()), 200
'''

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 src/node.py path_to_config index")
        sys.exit(1)
    
    config_path = sys.argv[1]
    node_index = int(sys.argv[2])
    
    with open(config_path, 'r') as file:
        config = json.load(file)
    
    address = config['addresses'][node_index]
    
    app.run(host='0.0.0.0', port=address['port'])
