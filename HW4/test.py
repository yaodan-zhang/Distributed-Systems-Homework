import itertools
import string

charset = string.ascii_lowercase
for l in range(1, 3):
    full_guess_space = itertools.product(charset, repeat=l)
    print("------"+str(l)+"------")
    for guess in list(full_guess_space)[0:10]:
        print(''.join(guess))
        
