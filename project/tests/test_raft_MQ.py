import requests
import time
import json

# Define node addresses from config.json
NODES = [
    "http://127.0.0.1:8567",
    "http://127.0.0.1:9123",
    "http://127.0.0.1:8889"
]

# Utility function to find the leader
def get_leader():
    for node in NODES:
        try:
            response = requests.get(f"{node}/status", timeout=1)
            if response.status_code == 200 and response.json()["role"] == "Leader":
                return node
        except requests.exceptions.RequestException:
            continue
    return None

# Test Committed Index: Checking committed log entries on all nodes -1
print("=== Verifying Committed Log Entries ===")
for node in NODES:
    try:
        response = requests.get(f"{node}/status", timeout=1)
        if response.status_code == 200:
            print(f"Node {node} committed index: {response.json()['commit_index']}")
    except requests.exceptions.RequestException:
        print(f"Node {node} is unreachable.")


# Test: Leader election and failover
print("=== Testing Leader Election and Failover ===")
leader = get_leader()
print(f"Initial leader: {leader}")

if leader:
    # Simulate leader failure (shutdown manually or via a termination command if applicable)
    print(f"Simulating failure of {leader}... Please manually stop the leader node.")
    time.sleep(30)  # Wait for new leader election
    new_leader = get_leader()
    print(f"New leader elected: {new_leader}")
    # Expected Output: A new leader should be elected within timeout.

# Test Committed Index: Checking committed log entries on all nodes -1
print("=== Verifying Committed Log Entries ===")
for node in NODES:
    try:
        response = requests.get(f"{node}/status", timeout=1)
        if response.status_code == 200:
            print(f"Node {node} committed index: {response.json()['commit_index']}")
    except requests.exceptions.RequestException:
        print(f"Node {node} is unreachable.")


# Test: Client redirection to leader
print("=== Testing Client Redirection ===")
for node in NODES:
    try:
        response = requests.put(f"{node}/topic", json={"topic": "news"}, timeout=1)
        if response.status_code == 403:
            print(f"{node} correctly redirected client to leader: {response.json()['leader']}")
        elif response.status_code == 200:
            print(f"{node} is the leader and created the topic successfully.")
    except requests.exceptions.RequestException:
        continue
# Expected Output: Followers should return 403 with leader's address. Only the leader should process writes.

# Test Committed Index: Checking committed log entries on all nodes
print("=== Verifying Committed Log Entries ===")
for node in NODES:
    try:
        response = requests.get(f"{node}/status", timeout=1)
        if response.status_code == 200:
            print(f"Node {node} committed index: {response.json()['commit_index']}")
    except requests.exceptions.RequestException:
        print(f"Node {node} is unreachable.")


# Test: Log consistency across nodes
print("=== Testing Log Consistency ===")
leader = get_leader()
if leader:
    print("Sending a message to the leader...")
    response = requests.put(f"{leader}/message", json={"topic": "news", "message": "Breaking News!"}, timeout=1)
    time.sleep(5)  # Wait for log replication
    if response.status_code == 200:
        print(f"leader created the message successfully.")
    
# Test Committed Index: Checking committed log entries on all nodes
print("=== Verifying Committed Log Entries ===")
for node in NODES:
    try:
        response = requests.get(f"{node}/status", timeout=1)
        if response.status_code == 200:
            print(f"Node {node} committed index: {response.json()['commit_index']}")
    except requests.exceptions.RequestException:
        print(f"Node {node} is unreachable.")


# Test: Handling of non-existent topics
print("=== Testing Non-Existent Topics ===")
leader = get_leader()
if leader:
    response = requests.get(f"{leader}/message/unknown_topic", timeout=1)
    print(f"Response: {response.json()}")
    # Expected Output: Should return an error indicating the topic does not exist.

# Test Committed Index: Checking committed log entries on all nodes
print("=== Verifying Committed Log Entries ===")
for node in NODES:
    try:
        response = requests.get(f"{node}/status", timeout=1)
        if response.status_code == 200:
            print(f"Node {node} committed index: {response.json()['commit_index']}")
    except requests.exceptions.RequestException:
        print(f"Node {node} is unreachable.")


# Test: Concurrent Requests
print("=== Testing Concurrent Requests ===")
from threading import Thread

def send_message():
    leader = get_leader()
    if leader:
        response = requests.put(f"{leader}/message", json={"topic": "news", "message": "Update!"}, timeout=1)
        if response.status_code == 200:
            print('leader put message success!')

threads = [Thread(target=send_message) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("Sent multiple concurrent messages.")
# Expected Output: The leader should handle 5 multiple concurrent requests without inconsistency.

# Test Committed Index: Checking committed log entries on all nodes
print("=== Verifying Committed Log Entries ===")
for node in NODES:
    try:
        response = requests.get(f"{node}/status", timeout=1)
        if response.status_code == 200:
            print(f"Node {node} committed index: {response.json()['commit_index']}")
    except requests.exceptions.RequestException:
        print(f"Node {node} is unreachable.")

print("=== All tests completed! ===")