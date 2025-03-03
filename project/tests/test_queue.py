import requests

BASE_URL = "http://127.0.0.1:8567"  # Adjust this based on the actual server address

def test_create_topic(topic):
    response = requests.put(f"{BASE_URL}/topic", json={"topic": topic})
    print(f"Create topic '{topic}':", response.json(), response.status_code)

def test_get_topics():
    response = requests.get(f"{BASE_URL}/topic")
    print("Get topics:", response.json(), response.status_code)

def test_add_message(topic, message):
    response = requests.put(f"{BASE_URL}/message", json={"topic": topic, "message": message})
    print(f"Add message to '{topic}':", response.json(), response.status_code)

def test_get_message(topic):
    response = requests.get(f"{BASE_URL}/message/{topic}")
    print(f"Get message from '{topic}':", response.json(), response.status_code)

'''def test_status():
    response = requests.get(f"{BASE_URL}/status")
    print("Get status:", response.json(), response.status_code)
'''

def run_tests():
    print("Testing API...")
    
    # Ensure we start with an empty topic list
    print("--- Testing empty topic list ---")
    test_get_topics()
    
    # Test creating topics
    print("--- Creating topics ---")
    test_create_topic("news")
    test_create_topic("sports")
    test_create_topic("news")  # Should fail (duplicate)
    
    # Verify topics
    print("--- Verifying topics ---")
    test_get_topics() # [news, sports]

    # Test adding and retrieving messages
    print("--- Adding and retrieving messages ---")
    test_add_message("news", "Breaking news: API test successful!")
    test_add_message("sports", "Sports update: Team wins championship!")
    test_add_message("unknown", "This should fail")  # Topic doesn't exist
    
    test_get_message("news")
    test_get_message("sports")
    test_get_message("sports")  # Should return empty since only one message was added
    test_get_message("unknown")  # Should fail (non-existent topic)
    
    # Test status endpoint
    '''print("--- Testing status endpoint ---")
    test_status()'''

if __name__ == "__main__":
    run_tests()
