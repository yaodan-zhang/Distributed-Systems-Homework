import requests
import sys
import string
import json
import threading
import queue
import itertools

def distribute_work(start_port, end_port, md5_hash, max_length):
    """Distributes password cracking work across multiple service instances by dividing length, not characters."""
    ports = list(range(start_port, end_port + 1))
    charset = string.ascii_lowercase
    num_servers = len(ports)

    chunks = []
    
    # Divide workload
    for l in range(1, max_length + 1):
        full_guess_space = list(itertools.product(charset, repeat=l))
        
        chunk_length = len(full_guess_space)//num_servers

        current_chunks = [full_guess_space[i*chunk_length:(i+1)*chunk_length] for i in range(num_servers)]

        current_chunks[-1] += full_guess_space[num_servers * chunk_length :]

        if not chunks:
            chunks = current_chunks

        else:
            for i in range(num_servers):
                chunks[i] += current_chunks[i]

    # Queue for fault tolerance (redistributes failed tasks)
    task_queue = queue.Queue()
    for i, port in enumerate(ports):
        task_queue.put((port, chunks[i]))

    found_password = None
    lock = threading.Lock()

    def query_service(i):
        """Thread function to query a service instance and handle failures."""
        nonlocal found_password
        while True:
            if found_password:
                return
            
            if task_queue.empty():
                continue

            port, guess_space = task_queue.get()
            if found_password:
                return  # Stop if password is found

            payload = {
                "hash": md5_hash,
                "guess_space": guess_space,
            }

            try:
                response = requests.post(f"http://localhost:{port}/crack", json=payload, timeout=3600)
                if response.status_code == 200 and "password" in response.json():
                    with lock:
                        found_password = response.json()["password"]
                        print(f"✅ Password found: {found_password} (from port {port})")

            except requests.exceptions.RequestException as e:
                print(f"❌ Server {port} failed! Reassigning its work...")
                print(f"Error occurred: {e}")

                # Redistribute failed workload to other servers
                for backup_port in ports:
                    if backup_port != port:
                        task_queue.put((backup_port, guess_space))  # Reassign failed task
                        return

    # Start a thread for each server
    threads = []
    for k in range(num_servers):
        thread = threading.Thread(target=query_service,args=(k,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    if not found_password:
        print("❌ Password not found.")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 client.py <start-port> <end-port> <md5_password> <max_password_length>")
        sys.exit(1)

    start_port = int(sys.argv[1])
    end_port = int(sys.argv[2])
    md5_hash = sys.argv[3]
    max_length = int(sys.argv[4])

    distribute_work(start_port, end_port, md5_hash, max_length)
