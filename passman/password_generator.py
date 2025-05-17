import string
import secrets

class PasswordGenerator:
    """Password generator"""
    
    def __init__(self):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.special_chars = "!@#$%^&*()_+{}[]<>?/~"
    
    def generate_password(self, length=16, include_lowercase=True, include_uppercase=True, 
                         include_digits=True, include_special=True):
        """Generate a password with specified parameters"""
        if length < 4 and (include_lowercase + include_uppercase + include_digits + include_special) > length:
            raise ValueError("Password length is too small for the specified requirements")
        
        if not any([include_lowercase, include_uppercase, include_digits, include_special]):
            raise ValueError("At least one character type must be selected")
        
        # Form the character pool
        char_pool = ""
        if include_lowercase:
            char_pool += self.lowercase
        if include_uppercase:
            char_pool += self.uppercase
        if include_digits:
            char_pool += self.digits
        if include_special:
            char_pool += self.special_chars
        
        # Ensure the password contains at least one character from each selected type
        password = []
        if include_lowercase:
            password.append(secrets.choice(self.lowercase))
        if include_uppercase:
            password.append(secrets.choice(self.uppercase))
        if include_digits:
            password.append(secrets.choice(self.digits))
        if include_special:
            password.append(secrets.choice(self.special_chars))
        
        # Add remaining random characters
        for _ in range(length - len(password)):
            password.append(secrets.choice(char_pool))
        
        # Shuffle the password
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        
        return ''.join(password_list) 