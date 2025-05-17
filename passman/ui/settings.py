import curses
from .base import BaseWindow

class SettingsWindow(BaseWindow):
    """Settings window"""
    
    def __init__(self, stdscr, settings):
        """Initialization of settings window"""
        super().__init__(stdscr)
        self.settings = settings
        self.selected_index = 0
        self.update_menu_items()
    
    def update_menu_items(self):
        """Update menu items"""
        algorithms = ["AES-256", "ChaCha20", "Camellia"]
        current_algorithm = self.settings.get("encryption_algorithm", "AES-256")
        
        self.menu_items = [
            f"Encryption algorithm: {current_algorithm}",
            f"Clipboard clear time: {self.settings.get('clipboard_clear_time', 30)} seconds",
            "Change master password",
            "Export data",
            "Import data",
            "Save settings",
            "Back"
        ]
    
    def display(self):
        """Display settings window"""
        while True:
            self.clear()
            self.draw_header("Settings")
            self.draw_footer(["[↑↓] - Navigation", "[Enter] - Select", "[Esc] - Back", "[←→] - Edit"])
            
            # Draw menu
            self.draw_menu(self.menu_items, self.selected_index)
            
            # Input handling
            key = self.stdscr.getch()
            
            # Navigation
            if key == curses.KEY_UP and self.selected_index > 0:
                self.selected_index -= 1
            elif key == curses.KEY_DOWN and self.selected_index < len(self.menu_items) - 1:
                self.selected_index += 1
            # Select item
            elif key == 10 or key == 13:  # Enter
                # Item selection handling
                if self.selected_index == 2:  # Change master password
                    if self.change_master_password():
                        self.draw_message("Master password successfully changed", color_pair=3)
                        self.stdscr.refresh()
                        self.wait_for_key([10, 13, 27])  # Enter or Escape
                elif self.selected_index == 5:  # Save settings
                    return self.settings
                elif self.selected_index == 6:  # Back
                    return None
            # Exit
            elif key == 27:  # Escape
                return None
            
            # Edit values using left-right arrows
            elif key == curses.KEY_LEFT:
                if self.selected_index == 0:  # Encryption algorithm
                    algorithms = ["AES-256", "ChaCha20", "Camellia"]
                    current_index = algorithms.index(self.settings.get("encryption_algorithm", "AES-256"))
                    new_index = (current_index - 1) % len(algorithms)
                    self.settings["encryption_algorithm"] = algorithms[new_index]
                    self.update_menu_items()
                elif self.selected_index == 1:  # Clipboard clear time
                    clear_time = self.settings.get("clipboard_clear_time", 30)
                    if clear_time > 0:
                        self.settings["clipboard_clear_time"] = clear_time - 5
                    self.update_menu_items()
            
            elif key == curses.KEY_RIGHT:
                if self.selected_index == 0:  # Encryption algorithm
                    algorithms = ["AES-256", "ChaCha20", "Camellia"]
                    current_index = algorithms.index(self.settings.get("encryption_algorithm", "AES-256"))
                    new_index = (current_index + 1) % len(algorithms)
                    self.settings["encryption_algorithm"] = algorithms[new_index]
                    self.update_menu_items()
                elif self.selected_index == 1:  # Clipboard clear time
                    clear_time = self.settings.get("clipboard_clear_time", 30)
                    if clear_time < 60:
                        self.settings["clipboard_clear_time"] = clear_time + 5
                    self.update_menu_items()
            
            # Handle terminal resize
            elif key == curses.KEY_RESIZE:
                self.resize()
                
            self.refresh()
    
    def change_master_password(self):
        """Change master password"""
        self.clear()
        self.draw_header("Change master password")
        self.draw_footer(["[Enter] - Save", "[Esc] - Cancel"])
        
        # Ask for current password
        current_password = self.get_string_input("Current password: ", 3, 2, mask=True)
        if not current_password:
            return False
            
        # Check if current password matches master password
        if current_password != self.settings.get("master_password", ""):
            self.draw_message("Incorrect password", self.height // 2, None, 4)
            self.stdscr.refresh()
            self.wait_for_key([10, 13, 27])  # Enter or Escape
            return False
        
        # Ask for new password
        new_password = self.get_string_input("New password: ", 5, 2, mask=True)
        if not new_password:
            return False
            
        # Ask for password confirmation
        confirm_password = self.get_string_input("Confirm password: ", 7, 2, mask=True)
        if not confirm_password:
            return False
        
        # Check if new password and confirmation match
        if new_password != confirm_password:
            self.draw_message("Passwords do not match", self.height // 2, None, 4)
            self.stdscr.refresh()
            self.wait_for_key([10, 13, 27])  # Enter or Escape
            return False
        
        # Set new password
        self.settings["master_password"] = new_password
        return True 