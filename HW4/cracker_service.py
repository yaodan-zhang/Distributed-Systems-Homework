import itertools
import string
import hashlib
import json
import sys
from flask import Flask, request, jsonify

app = Flask(__name__)

def bruteforce_partial(hashed_password, guess_space):
    """Attempts to brute-force the password within a given character subset."""
    for guess in guess_space:
        guess = ''.join(guess)
        if hashlib.md5(guess.encode()).hexdigest() == hashed_password:
            return guess
    return None

@app.route('/crack', methods=['POST'])
def crack_password():
    """API endpoint to brute force crack an MD5 hashed password with a given charset range."""
    data = request.get_json()
    
    if (not data) or ('hash' not in data) or ('guess_space' not in data):
        return jsonify({'error': 'Invalid input'}), 400

    hashed_password = data['hash']
    guess_space = data['guess_space']

    password = bruteforce_partial(hashed_password, guess_space)

    if password:
        return jsonify({'password': password})
    else:
        return jsonify({'Warning': 'Password not found'})

if __name__ == '__main__':
    try:
        port = int(sys.argv[1])

    # Assign a default port
    except (IndexError, ValueError):
        port = 5000

    app.run(host='0.0.0.0', port=port)