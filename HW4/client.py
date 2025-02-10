import requests
import sys
import string
import json
import threading
import queue

def distribute_work(start_port, end_port, md5_hash, max_length):
    """Distributes password cracking work across multiple service instances by dividing length, not characters."""
    ports = list(range(start_port, end_port + 1))
    charset = string.ascii_lowercase  # All servers get full character set

    # Divide workload by password length
    length_chunks = list(range(1, max_length + 1))
    num_servers = len(ports)
    chunk_size = len(length_chunks) // num_servers

    # Distribute lengths evenly
    chunks = [length_chunks[i * chunk_size: (i + 1) * chunk_size] for i in range(num_servers)]
    
    if len(length_chunks) % num_servers != 0:
        chunks[-1] += length_chunks[num_servers * chunk_size:]

    # Queue for fault tolerance (redistributes failed tasks)
    task_queue = queue.Queue()
    for i, port in enumerate(ports):
        task_queue.put((port, chunks[i]))

    found_password = None
    lock = threading.Lock()

    def query_service():
        """Thread function to query a service instance and handle failures."""
        nonlocal found_password
        while not task_queue.empty():
            port, length_subset = task_queue.get()
            if found_password:
                return  # Stop if password is found

            payload = {
                "hash": md5_hash,
                "charset": charset,  # Send full charset
                "max_length": max(length_subset)
            }

            try:
                response = requests.post(f"http://localhost:{port}/crack", json=payload, timeout=10)
                if response.status_code == 200 and "password" in response.json():
                    with lock:
                        found_password = response.json()["password"]
                        print(f"✅ Password found: {found_password} (from port {port})")
            except requests.exceptions.RequestException:
                print(f"❌ Server {port} failed! Reassigning its work...")
                # Redistribute failed workload to other servers
                for backup_port in ports:
                    if backup_port != port:
                        task_queue.put((backup_port, length_subset))  # Reassign failed task

    # Start a thread for each server
    threads = []
    for _ in ports:
        thread = threading.Thread(target=query_service)
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    if not found_password:
        print("❌ Password not found.")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python client.py <start-port> <end-port> <md5_password> <max_password_length>")
        sys.exit(1)

    start_port = int(sys.argv[1])
    end_port = int(sys.argv[2])
    md5_hash = sys.argv[3]
    max_length = int(sys.argv[4])

    distribute_work(start_port, end_port, md5_hash, max_length)
