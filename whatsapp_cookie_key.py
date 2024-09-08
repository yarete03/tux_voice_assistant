import keyring
from base64 import b64decode, b64encode
from random import choices
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2


def whatsapp_cookie_key_store():
    salt = get_random_bytes(32)
    cipher_iv = get_random_bytes(32)
    password = choices("abcdefghijknmñopkrstuvwxyzABCDEFGHIJKNMÑOPKRSTUVWXYZ1234567890'¡.,*?¿_:;", k=20)
    password = "".join([letter for letter in password])

    key = PBKDF2(password, salt, dkLen=32)

    key = b64encode(key).decode('utf-8')
    cipher_iv = b64encode(cipher_iv).decode('utf-8')

    print(key)

    keyring.set_password("system", "whatsapp_cookie_key", key)
    keyring.set_password("system", "whatsapp_cipher_iv", cipher_iv)


def whatsapp_cookie_key_retrieve():
    key = keyring.get_password("system", "whatsapp_cookie_key")
    cipher_iv = keyring.get_password("system", "whatsapp_cipher_iv")

    key = b64decode(key.encode('utf-8'))
    cipher_iv = b64decode(cipher_iv.encode('utf-8'))
    return key, cipher_iv
