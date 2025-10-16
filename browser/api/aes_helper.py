import os, uuid, random, base64, json, sys, hashlib;

#https://medium.com/@sachadehe/encrypt-decrypt-data-between-python-3-and-javascript-true-aes-algorithm-7c4e2fa3a9ff
#https://encryption-decryption.mojoauth.com/aes-256-encryption--javascript-in-browser/

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad

def chave_randomica(tamanho):
    CARACTERES = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "x", "z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "X", "Z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-", "!", "*", "#", "@", "_", "(", ")", "[", "]", "|", "=", "+", "$", ","];
    buffer = "";
    for i in range(tamanho):
        buffer = buffer + CARACTERES[random.randint(0, len(CARACTERES) - 1)];
    return buffer;

def encrypt_aes_cbc_no_iv(key, raw):
    iv = chave_randomica(16);
    return iv + encrypt_aes_cbc(key, iv, raw);
def encrypt_aes_cbc(key, iv, raw):
    if type(key) == type(""):
        key = key.encode();
    if type(iv) == type(""):
        iv = iv.encode();
    raw = pad(raw.encode(),16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(cipher.encrypt(raw)).decode("utf-8")
def decrypt_aes_cbc_no_iv(key, enc):
    iv = enc[:16];
    enc = enc[16:];
    return decrypt_aes_cbc(key, iv, enc);

def decrypt_aes_cbc(key, iv, enc):
    if type(key) == type(""):
        key = key.encode();
    if type(iv) == type(""):
        iv = iv.encode();
    enc = base64.b64decode(enc);
    cipher = AES.new(key, AES.MODE_CBC, iv)
    raw = unpad(cipher.decrypt(enc),16).decode("utf-8")
    return raw;

def encrypt_aes_ecb(key, raw):
    if type(key) == type(""):
        key = key.encode();
    raw = str(raw).encode("utf-8")
    cipher = AES.new(key, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(raw)).decode()

def decrypt_aes_ecb(key, enc):
    if type(key) == type(""):
        key = key.encode();
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.decrypt(base64.b64decode(enc)).decode()
