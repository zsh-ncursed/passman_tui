import curses
from .base import BaseWindow

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
        """Display Password Generator Window (optimized redraw)"""
        if not self.password:
            self.generate_password()
        prev_config_index = -1
        prev_config_mode = None
        prev_password = None
        prev_size = (self.height, self.width)
        dirty = True
        while True:
            if dirty or self.config_index != prev_config_index or self.config_mode != prev_config_mode or self.password != prev_password or (self.height, self.width) != prev_size:
                self.clear()
                self.draw_header("Password Generator")
                if self.config_mode:
                    self.draw_footer(["[↑↓] - Navigation", "[Enter] - Select", "[Esc] - Back", "[←→] - Change"])
                    self.draw_menu(self.config_items, self.config_index)
                else:
                    self.draw_footer(["[c] - Copy", "[g] - New Password", "[s] - Settings", "[Esc] - Back"])
                    if self.password:
                        password_msg = f"Generated Password: {self.password}"
                        self.draw_message(password_msg, self.height // 2 - 1, None, 3)
                        copy_msg = "Press 'c' to copy password to clipboard"
                        self.draw_message(copy_msg, self.height // 2 + 1, None, 6)
                    else:
                        error_msg = f"Password Generation Error: {self.error_message}"
                        self.draw_message(error_msg, self.height // 2, None, 4)
                self.refresh()
                prev_config_index = self.config_index
                prev_config_mode = self.config_mode
                prev_password = self.password
                prev_size = (self.height, self.width)
                dirty = False
            key = self.stdscr.getch()
            if self.config_mode:
                if key == curses.KEY_UP and self.config_index > 0:
                    self.config_index -= 1
                elif key == curses.KEY_DOWN and self.config_index < len(self.config_items) - 1:
                    self.config_index += 1
                elif key == 10 or key == 13:  # Enter
                    if self.config_index == 5:  # Generate Password
                        self.generate_password()
                        self.config_mode = False
                        dirty = True
                    elif self.config_index == 6:  # Back
                        self.config_mode = False
                        dirty = True
                    elif self.config_index == 0:  # Password Length
                        pass  # Handled by left/right keys
                    else:  # Toggle switches
                        attribute_names = ["include_lowercase", "include_uppercase", "include_digits", "include_special"]
                        attr_name = attribute_names[self.config_index - 1]
                        setattr(self, attr_name, not getattr(self, attr_name))
                        self.update_config_items()
                        dirty = True
                elif key == 27:  # Escape
                    self.config_mode = False
                    dirty = True
                elif key == curses.KEY_LEFT and self.config_index == 0:
                    if self.password_length > 4:
                        self.password_length -= 1
                        self.update_config_items()
                        dirty = True
                elif key == curses.KEY_RIGHT and self.config_index == 0:
                    if self.password_length < 64:
                        self.password_length += 1
                        self.update_config_items()
                        dirty = True
            else:
                if key == ord('c'):
                    return self.password
                elif key == ord('g'):
                    self.generate_password()
                    dirty = True
                elif key == ord('s'):
                    self.config_mode = True
                    self.config_index = 0
                    dirty = True
                elif key == 27:
                    return None
            if key == curses.KEY_RESIZE:
                self.resize()
                dirty = True
            if self.config_index != prev_config_index or self.config_mode != prev_config_mode or self.password != prev_password or (self.height, self.width) != prev_size or dirty:
                continue 