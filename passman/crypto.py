import os
import json
import gnupg
import base64
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


class CryptoManager:
    """Data encryption manager"""
    
    ALGORITHMS = {
        'AES-256': 'aes256',
        'ChaCha20': 'chacha20',
        'Camellia': 'camellia256'
    }
    
    def __init__(self, password, algorithm='AES-256'):
        """Data encryption manager initialization"""
        self.password = password
        self.algorithm = algorithm
        
        # Directory for storing passwords
        home = str(Path.home())
        self.storage_dir = Path(home) / '.passman'
        self.storage_dir.mkdir(exist_ok=True)
        
        # GPG initialization
        self.gpg = gnupg.GPG(gnupghome=str(self.storage_dir))
        
    def encrypt_data(self, data):
        """Encrypting data"""
        json_data = json.dumps(data)
        encrypted_data = self.gpg.encrypt(
            json_data, 
            recipients=None, 
            symmetric=self.ALGORITHMS.get(self.algorithm, 'aes256'),
            passphrase=self.password
        )
        return str(encrypted_data)
    
    def decrypt_data(self, encrypted_data):
        """Decrypting data"""
        decrypted_data = self.gpg.decrypt(
            encrypted_data, 
            passphrase=self.password
        )
        
        if not decrypted_data.ok:
            raise ValueError("Failed to decrypt data. Check your password.")
        
        return json.loads(str(decrypted_data))
    
    def save_to_file(self, data, filename):
        """Saving data to file"""
        encrypted = self.encrypt_data(data)
        filepath = self.storage_dir / f"{filename}.gpg"
        
        with open(filepath, 'w') as f:
            f.write(encrypted)
    
    def load_from_file(self, filename):
        """Loading data from file"""
        filepath = self.storage_dir / f"{filename}.gpg"
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r') as f:
            encrypted_data = f.read()
        
        return self.decrypt_data(encrypted_data) 