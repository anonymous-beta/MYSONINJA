from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import json

class CryptoManager:
    """Encryption for payloads, sessions, and stored data"""
    
    SALT = b'mysoninja_salt_2024'
    
    @classmethod
    def derive_key(cls, password):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=cls.SALT,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    @classmethod
    def encrypt(cls, data, key):
        f = Fernet(key)
        return f.encrypt(data.encode() if isinstance(data, str) else data)
    
    @classmethod
    def decrypt(cls, data, key):
        f = Fernet(key)
        return f.decrypt(data)
    
    @classmethod
    def generate_key(cls):
        return Fernet.generate_key()
    
    @classmethod
    def xor_obfuscate(cls, data, key=0xAA):
        """Simple XOR obfuscation for payloads"""
        return bytes([b ^ key for b in data.encode() if isinstance(data, str) else data])
