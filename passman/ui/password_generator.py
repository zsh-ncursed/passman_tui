import curses
from .base import BaseWindow, KEYBINDINGS

class PasswordGeneratorWindow(BaseWindow):
    """Password Generator Window"""
    
    def __init__(self, stdscr, password_generator):
        """Password Generator Window Initialization"""
        super().__init__(stdscr)
        self.password_generator = password_generator
        self.password = ""
        self.password_length = 16
        self.include_lowercase = True
        self.include_uppercase = True
        self.include_digits = True
        self.include_special = True
        self.config_mode = False
        self.config_index = 0
        self.config_items = [
            f"Password Length: {self.password_length}",
            f"Lowercase Letters: {'Yes' if self.include_lowercase else 'No'}",
            f"Uppercase Letters: {'Yes' if self.include_uppercase else 'No'}",
            f"Digits: {'Yes' if self.include_digits else 'No'}",
            f"Special Characters: {'Yes' if self.include_special else 'No'}",
            "Generate Password",
            "Back"
        ]
    
    def update_config_items(self):
        """Update Configuration Items"""
        self.config_items = [
            f"Password Length: {self.password_length}",
            f"Lowercase Letters: {'Yes' if self.include_lowercase else 'No'}",
            f"Uppercase Letters: {'Yes' if self.include_uppercase else 'No'}",
            f"Digits: {'Yes' if self.include_digits else 'No'}",
            f"Special Characters: {'Yes' if self.include_special else 'No'}",
            "Generate Password",
            "Back"
        ]
    
    def generate_password(self):
        """Generate Password with Current Settings"""
        try:
            self.password = self.password_generator.generate_password(
                length=self.password_length,
                include_lowercase=self.include_lowercase,
                include_uppercase=self.include_uppercase,
                include_digits=self.include_digits,
                include_special=self.include_special
            )
            return True
        except ValueError as e:
            self.password = ""
            self.error_message = str(e)
            return False
    
    def display(self):
        """Display Password Generator Window"""
        # Generate password on first display
        if not self.password:
            self.generate_password()
        
        while True:
            self.clear()
            self.draw_header("Password Generator")
            
            if self.config_mode:
                self.draw_footer(["NAVIGATE_UP", "NAVIGATE_DOWN", "NAVIGATE_LEFT", "NAVIGATE_RIGHT", "SELECT", "BACK_CANCEL"])
                self.draw_menu(self.config_items, self.config_index)
            else:
                self.draw_footer(["COPY", "GENERATE", "SETTINGS", "BACK_CANCEL"])
                
                # Display generated password
                if self.password:
                    password_msg = f"Generated Password: {self.password}"
                    self.draw_message(password_msg, self.height // 2 - 1, None, 3)
                    copy_msg = "Press 'c' to copy password to clipboard"
                    self.draw_message(copy_msg, self.height // 2 + 1, None, 6)
                else:
                    error_msg = f"Password Generation Error: {self.error_message}"
                    self.draw_message(error_msg, self.height // 2, None, 4)
            
            # Input Handling
            key = self.stdscr.getch()
            
            if self.config_mode:
                # Configuration Mode
                if key == KEYBINDINGS["NAVIGATE_UP"]["keys"] and self.config_index > 0:
                    self.config_index -= 1
                elif key == KEYBINDINGS["NAVIGATE_DOWN"]["keys"] and self.config_index < len(self.config_items) - 1:
                    self.config_index += 1
                elif key in KEYBINDINGS["SELECT"]["keys"]:
                    if self.config_index == 5:  # Generate Password
                        self.generate_password()
                        self.config_mode = False
                    elif self.config_index == 6:  # Back
                        self.config_mode = False
                    elif self.config_index == 0:  # Password Length
                        pass  # Handled by left/right keys, no action on SELECT for this item
                    else:  # Toggle switches for include_lowercase, etc.
                        # Ensure config_index is valid for attribute_names
                        if 1 <= self.config_index <= 4:
                            attribute_names = ["include_lowercase", "include_uppercase", 
                                             "include_digits", "include_special"]
                            attr_name = attribute_names[self.config_index - 1]
                            setattr(self, attr_name, not getattr(self, attr_name))
                            self.update_config_items()
                elif key in KEYBINDINGS["BACK_CANCEL"]["keys"]:
                    self.config_mode = False
                elif key == KEYBINDINGS["NAVIGATE_LEFT"]["keys"] and self.config_index == 0:  # Decrease password length
                    if self.password_length > 4: # Assuming min length 4
                        self.password_length -= 1
                        self.update_config_items()
                elif key == KEYBINDINGS["NAVIGATE_RIGHT"]["keys"] and self.config_index == 0:  # Increase password length
                    if self.password_length < 64: # Assuming max length 64
                        self.password_length += 1
                        self.update_config_items()
            else:
                # Main display mode
                if key == KEYBINDINGS["COPY"]["keys"]:
                    return self.password # Return the password string to be copied by the caller
                elif key == KEYBINDINGS["GENERATE"]["keys"]:
                    self.generate_password()
                elif key == KEYBINDINGS["SETTINGS"]["keys"]:
                    self.config_mode = True
                    self.config_index = 0 # Reset config index when entering settings
                elif key in KEYBINDINGS["BACK_CANCEL"]["keys"]:
                    return None # Exit window
            
            # Handle terminal resize
            if key == curses.KEY_RESIZE:
                self.resize()
                
            self.refresh() 