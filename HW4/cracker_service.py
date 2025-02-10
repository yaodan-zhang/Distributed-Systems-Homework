import sys
import itertools
import string
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)

def bruteforce_password(hashed_password, max_length, chars=string.ascii_lowercase):
    """
    Attempt to brute force the password by checking all combinations of
    the provided characters up to max_length.
    """
    for password_length in range(1, max_length + 1):
        print(f"Trying passwords of length: {password_length}")
        for guess_tuple in itertools.product(chars, repeat=password_length):
            guess = ''.join(guess_tuple)
            if hashlib.md5(guess.encode()).hexdigest() == hashed_password:
                return guess
    return None

@app.route('/crack', methods=['POST'])
def crack():
    """
    Expects JSON input with keys:
      - 'hash': the MD5 hash string to crack
      - 'max_length': the maximum password length to search
    Returns a JSON response with either the cracked password or an error message.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input provided.'}), 400

    hashed_password = data.get('hash')
    max_length = data.get('max_length')

    if (not hashed_password) or (not max_length):
        return jsonify({'error': 'Missing parameters. Provide both "hash" and "max_length".'}), 400

    try:
        max_length = int(max_length)
    except ValueError:
        return jsonify({'error': '"max_length" must be an integer.'}), 400

    result = bruteforce_password(hashed_password, max_length)
    if result:
        return jsonify({'result': result})
    else:
        return jsonify({
            'result': None,
            'message': 'Password not found within the given constraints.'
        }), 200

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python cracker_service.py <port>")
        sys.exit(1)
    port = int(sys.argv[1])
    # Run on all available network interfaces so other machines can connect if needed.
    app.run(host='0.0.0.0', port=port)
