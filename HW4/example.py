import itertools
import string
import hashlib
def bruteforce_password(hashed_password, max_length):
    # chars = string.printable # all printable characters
    chars = string.ascii_lowercase # lowercase characters
    for password_length in range(1, max_length+1):
        print (password_length)
        for guess in itertools.product(chars, repeat=password_length):
            guess = ''.join(guess)
            if hashlib.md5(guess.encode()).hexdigest() == hashed_password:
                return guess
    return None

print(bruteforce_password('cce6b3fb87d8237167f1c5dec15c3133', 4))
