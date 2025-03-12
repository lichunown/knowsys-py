import os
import secrets

def random_string(length=32):
    return os.urandom(length // 2).hex()
