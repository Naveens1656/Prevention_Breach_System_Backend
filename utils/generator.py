import random
import string
import random


adjectives = ["Blue", "Silent", "Rapid", "Hidden", "Lucky"]
nouns = ["Tiger", "River", "Eagle", "Shadow", "Storm"]
symbols = ["@", "#", "$", "!", "%"]

def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(14))
def generate_passphrase():
    return (
        random.choice(adjectives) +
        random.choice(nouns) +
        random.choice(symbols) +
        str(random.randint(10,99))
    )