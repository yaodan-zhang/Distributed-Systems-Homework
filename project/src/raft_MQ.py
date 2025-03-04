import sys
import json
import threading
import time
import random
import requests
from flask import Flask, request, jsonify
# Raft node states
FOLLOWER = "Follower"
CANDIDATE = "Candidate"
LEADER = "Leader"

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

class RaftNode:
    def __init__(self, node_index, config):
        self.node_index = node_index
        self.config = config
        self.address = config['addresses'][node_index]
        self.peers = [addr for i, addr in enumerate(config['addresses']) if i != node_index]
        self.state = FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.election_timeout = random.uniform(8, 25)
        self.last_heartbeat = time.time()
        self.lock = threading.Lock()
        self.leader_address = None
        self.log = []  # Raft log for replication
        self.commit_index = -1  # Index of the last committed log entry
        self.last_applied = -1  # Last applied log index

        threading.Thread(target=self.start_election_timer, daemon=True).start()


    def start_election_timer(self):
        while True:
            time.sleep(random.uniform(4, 7))  # Randomized timeout to prevent vote splitting
            with self.lock:
                if self.state != LEADER and (time.time() - self.last_heartbeat) > self.election_timeout:
                    self.start_election()

    def election_timer(self):
        while True:
            time.sleep(0.1)
            with self.lock:
                if self.state != LEADER and (time.time() - self.last_heartbeat) > self.election_timeout:
                    self.start_election()

    def start_election(self):
        self.state = CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_index
        self.last_heartbeat = time.time()
        print(f"Node {self.node_index} starting election for term {self.current_term}")
        votes = 1
        #print(self.peers)
        for peer in self.peers:
            #print(peer)
            try:
                #print(peer, 'inside line 80')
                response = requests.post(f"{peer['ip']}:{peer['port']}/request_vote",
                                        json={"term": self.current_term, "candidate_id": self.node_index},
                                        timeout=5)
                
                try:
                    data = response.json()  # Check if the response is valid JSON
                    if data.get("vote_granted"):
                        votes += 1
                        print(f"✅ Node {self.node_index} received vote from {peer}")
                except requests.exceptions.RequestException as e:
                    #continue
                    print(f"❌ Invalid JSON response from {peer}, skipping.", e)
                
            except requests.exceptions.RequestException as e:
                #continue
                print(f"❌ Node {self.node_index} failed to contact {peer} for vote.", e)

        print(votes, len(self.peers) // 2)
        if votes > len(self.peers) // 2:
            print('inside if')
            self.become_leader()

    def become_leader(self):
        print('inside become leader')
        
        print('become leader')
        self.state = LEADER
        self.leader_address = self.address
        print(f"Node {self.node_index} is now the leader for term {self.current_term}")
        threading.Thread(target=self.send_heartbeats, daemon=True).start()
    
    def send_heartbeats(self):
        while self.state == LEADER:
            print(f"❤️ Leader {self.node_index} sending heartbeats...")
            for peer in self.peers:
                try:
                    response = requests.post(f"{peer['ip']}:{peer['port']}/append_entries",
                                            json={"term": self.current_term, "leader_id": self.node_index,
                                                "leader_address": self.address, "log": self.log,
                                                "commit_index": self.commit_index},
                                            timeout=5)
                    if response.status_code == 200:
                        print(f"✅ Heartbeat acknowledged by {peer}")
                except requests.exceptions.RequestException:
                    print(f"❌ Failed to send heartbeat to {peer}")

            time.sleep(2)  # Adjust heartbeat frequency if needed

    def receive_heartbeat(self, leader_term, leader_address, log, commit_index):
        with self.lock:
            if leader_term >= self.current_term:
                self.state = FOLLOWER
                self.current_term = leader_term
                self.leader_address = leader_address
                self.last_heartbeat = time.time()
                self.log = log  # Update log for consistency
                self.commit_index = commit_index
                self.apply_committed_entries()
    
    def apply_committed_entries(self):
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.log[self.last_applied]

            if entry["operation"] == "create_topic":
                response = message_queue.create_topic(entry['topic'])
                if not response:
                    print("Create topic error in node ", self.address)

            elif entry["operation"] == "add_message":
                response = message_queue.add_message(entry['topic'], entry['message'])
                if not response:
                    print("Add message error in node ", self.address)

            elif entry["operation"] == "get_topics":
                pass  # No need to modify state for a read operation

            elif entry["operation"] == "get_message":
                response, _ = message_queue.pop_message(entry['topic'])
                if not response:
                    print("Get message error in node ", self.address)

    def get_status(self):
        return {"role": self.state, "term": self.current_term, "leader": self.leader_address, "commit_index": self.commit_index, "last_applied": self.last_applied}
    
# Flask app setup
app = Flask(__name__)
message_queue = MessageQueue()

@app.route('/topic', methods=['PUT'])
def create_topic():
    if raft_node.state != LEADER:
        return jsonify({"success": False, "error": "Not the leader", "leader": raft_node.leader_address}), 403
    
    data = request.get_json()
    if (not data) or ('topic' not in data):
        return jsonify({"success": False, "error": "Missing 'topic' field"}), 400
    
    # Append to Raft log first
    entry = {"term": raft_node.current_term, "topic": data["topic"], "operation": "create_topic"}
    raft_node.log.append(entry)
    raft_node.commit_index += 1
    
    # Send log to followers for replication
    for peer in raft_node.peers:
        try:
            response = requests.post(f"{peer['ip']}:{peer['port']}/append_entries",
                          json={"term": raft_node.current_term, "leader_id": raft_node.node_index,
                                "leader_address": raft_node.address, "log": raft_node.log,
                                "commit_index": raft_node.commit_index},
                          timeout=1)
            if response.status_code == 200:
                print("create topic entry posted to ", peer)
            else:
                print("error posting create topic to ", peer)

        except requests.exceptions.RequestException:
            continue
    
    # Apply topic creation after replication
    success = message_queue.create_topic(data['topic'])
    if success:
        return jsonify({"success": True}), 200
    return jsonify({"success": False, "error": "Topic already exists"}), 409 # HTTP Code: 409 Topic eixists.

@app.route('/topic', methods=['GET'])
def get_topics():
    if raft_node.state != LEADER:
        return jsonify({"success": False, "error": "Not the leader", "leader": raft_node.leader_address}), 403
    
    entry = {"term": raft_node.current_term, "operation": "get_topics"}
    raft_node.log.append(entry)
    raft_node.commit_index += 1

    # Send log to followers for replication
    for peer in raft_node.peers:
        try:
            response = requests.post(f"{peer['ip']}:{peer['port']}/append_entries",
                          json={"term": raft_node.current_term, "leader_id": raft_node.node_index,
                                "leader_address": raft_node.address, "log": raft_node.log,
                                "commit_index": raft_node.commit_index},
                          timeout=1)
            if response.status_code == 200:
                print("get topics entry posted to ", peer)
            else:
                print("error posting get topics to ", peer)

        except requests.exceptions.RequestException:
            continue

    return jsonify({"success": True, "topics": message_queue.get_topics()}), 200

@app.route('/message', methods=['PUT'])
def add_message():
    # Check leader 
    if raft_node.state != LEADER:
        return jsonify({"success": False, "error": "Not the leader", "leader": raft_node.leader_address}), 403
    
    data = request.get_json()
    if (not data) or ('topic' not in data) or ('message' not in data):
        return jsonify({"success": False, "error": "Missing fields"}), 400
    
    # Append to Raft log first
    entry = {"term": raft_node.current_term, "topic": data["topic"], "message": data["message"], 'operation':'add_message'}
    raft_node.log.append(entry)
    raft_node.commit_index += 1
    
    # Send log to followers for replication
    for peer in raft_node.peers:
        try:
            response = requests.post(f"{peer['ip']}:{peer['port']}/append_entries",
                          json={"term": raft_node.current_term, "leader_id": raft_node.node_index,
                                "leader_address": raft_node.address, "log": raft_node.log,
                                "commit_index": raft_node.commit_index},
                          timeout=1)
            if response.status_code == 200:
                print("add message entry posted to ", peer)
            else:
                print("error posting add message to ", peer)

        except requests.exceptions.RequestException as e:
            print(peer, " is not accessible!")
            continue
    
    # Apply message after replication
    success = message_queue.add_message(data['topic'], data['message'])
    if success:
        return jsonify({"success": True}), 200
    return jsonify({"success": False, "error": "Topic does not exist"}), 410

@app.route('/message/<topic>', methods=['GET'])
def get_message(topic):
    if raft_node.state != LEADER:
        return jsonify({"success": False, "error": "Not the leader", "leader": raft_node.leader_address}), 403
    
    entry = {"term": raft_node.current_term, "operation": "get_message", "topic": topic}
    raft_node.log.append(entry)
    raft_node.commit_index += 1

    # Send log to followers for replication
    for peer in raft_node.peers:
        try:
            response = requests.post(f"{peer['ip']}:{peer['port']}/append_entries",
                          json={"term": raft_node.current_term, "leader_id": raft_node.node_index,
                                "leader_address": raft_node.address, "log": raft_node.log,
                                "commit_index": raft_node.commit_index},
                          timeout=1)
            if response.status_code == 200:
                print("get message entry posted to ", peer)
            else:
                print("error posting get message to ", peer)

        except requests.exceptions.RequestException:
            continue
    
    # Apply entry after replication
    success, message = message_queue.pop_message(topic)
    if success:
        return jsonify({"success": True, "message": message}), 200
    return jsonify({"success": False, "error": "Topic does not exist or there are no messages in the topic"}), 400

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(raft_node.get_status()), 200


@app.route('/request_vote', methods=['POST'])
def request_vote():
    data = request.get_json()
    term = data.get("term")
    candidate_id = data.get("candidate_id")

    with raft_node.lock:
        if term > raft_node.current_term:
            raft_node.current_term = term
            raft_node.voted_for = None
            raft_node.state = FOLLOWER  # Reset to Follower if term is higher

        if raft_node.voted_for is None or raft_node.voted_for == candidate_id:
            raft_node.voted_for = candidate_id
            print(f"✅ Node {raft_node.node_index} voted for {candidate_id} in term {term}")
            return jsonify({"vote_granted": True}), 200

    print(f"❌ Node {raft_node.node_index} rejected vote request from {candidate_id} in term {term}")
    return jsonify({"vote_granted": False}), 403


@app.route('/append_entries', methods=['POST'])
def append_entries():
    data = request.get_json()
    leader_term = data.get("term")
    leader_address = data.get("leader_address")
    log = data.get("log", [])
    commit_index = data.get("commit_index", -1)
    raft_node.receive_heartbeat(leader_term, leader_address, log, commit_index)
    return jsonify({"success": True}), 200


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python src/node.py path_to_config index")
        sys.exit(1)
    
    config_path = sys.argv[1]
    node_index = int(sys.argv[2])
    
    with open(config_path, 'r') as file:
        config = json.load(file)
    
    raft_node = RaftNode(node_index, config)
    
    address = config['addresses'][node_index]
    
    app.run(host='0.0.0.0', port=address['port'])
