import itertools
import string
import hashlib
import json
import sys
from flask import Flask, request, jsonify

app = Flask(__name__)

# Cache to store previously cracked passwords
cache = {}

def bruteforce_partial(hashed_password, charset, max_length):
    """Attempts to brute-force the password within a given character subset."""
    if hashed_password in cache:
        return cache[hashed_password]

    for password_length in range(1, max_length + 1):
        for guess in itertools.product(charset, repeat=password_length):
            guess = ''.join(guess)
            if hashlib.md5(guess.encode()).hexdigest() == hashed_password:
                cache[hashed_password] = guess
                return guess
    return None

@app.route('/crack', methods=['POST'])
def crack_password():
    """API endpoint to brute force crack an MD5 hashed password with a given charset range."""
    data = request.get_json()
    
    if (not data) or ('hash' not in data) or ('charset' not in data) or ('max_length' not in data):
        return jsonify({'error': 'Invalid input'}), 400

    hashed_password = data['hash']
    charset = data['charset']
    max_length = int(data['max_length'])

    password = bruteforce_partial(hashed_password, charset, max_length)

    if password:
        return jsonify({'password': password})
    else:
        return jsonify({'error': 'Password not found'}), 404

if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except (IndexError, ValueError):
        port = 5000

    app.run(host='0.0.0.0', port=port)
