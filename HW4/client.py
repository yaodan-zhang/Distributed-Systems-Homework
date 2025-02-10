import requests
import sys

def main():
    if len(sys.argv) != 4:
        print("Usage: python client.py <port> <md5_password> <max_password_length>")
        sys.exit(1)
    
    port = sys.argv[1]
    md5_password = sys.argv[2]
    max_length = sys.argv[3]
    
    # Construct the URL for the REST endpoint.
    url = f'http://localhost:{port}/crack'
    
    # Prepare the JSON payload.
    payload = {
        "hash": md5_password,
        "max_length": max_length
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get('result'):
                print("Password found:", data['result'])
            else:
                print("Password not found. Message:", data.get('message'))
        else:
            print("Error:", response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

if __name__ == '__main__':
    main()
