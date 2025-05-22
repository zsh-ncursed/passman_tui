import curses
from .base import BaseWindow, KEYBINDINGS
from .. import __version__

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
            
            # Draw Passman version (example: above the menu, below header)
            version_str = f"Passman v{__version__}"
            # Center the version string if possible, or place it left-aligned
            version_x = (self.width - len(version_str)) // 2
            if version_x < 1: version_x = 1
            try:
                self.stdscr.addstr(1, version_x, version_str) # Draw on line 1
            except curses.error:
                pass # Ignore if it can't be drawn (e.g. too small window)

            self.draw_footer(["NAVIGATE_UP", "NAVIGATE_DOWN", "NAVIGATE_LEFT", "NAVIGATE_RIGHT", "SELECT", "BACK_CANCEL"])
            
            # Draw menu (adjust start_y if version string takes line 1 or 2)
            self.draw_menu(self.menu_items, self.selected_index, start_y=3) # Start menu from line 3
            
            # Input handling
            key = self.stdscr.getch()
            
            # Navigation
            if key == KEYBINDINGS["NAVIGATE_UP"] and self.selected_index > 0:
                self.selected_index -= 1
            elif key == KEYBINDINGS["NAVIGATE_DOWN"] and self.selected_index < len(self.menu_items) - 1:
                self.selected_index += 1
            # Select item
            elif key in KEYBINDINGS["SELECT"]:
                # Item selection handling
                if self.selected_index == 2:  # Change master password
                    if self.change_master_password():
                        self.draw_message("Master password successfully changed", color_pair=3)
                        self.stdscr.refresh()
                        self.wait_for_key(["SELECT", "BACK_CANCEL"]) 
                elif self.selected_index == 3:  # Export data
                    return "__EXPORT__"
                elif self.selected_index == 4:  # Import data
                    return "__IMPORT__"
                elif self.selected_index == 5:  # Save settings
                    return self.settings
                elif self.selected_index == 6:  # Back
                    return None
            # Exit / Back
            elif key in KEYBINDINGS["BACK_CANCEL"]:
                return None
            
            # Edit values using left-right arrows
            elif key == KEYBINDINGS["NAVIGATE_LEFT"]:
                if self.selected_index == 0:  # Encryption algorithm
                    algorithms = ["AES-256", "ChaCha20", "Camellia"]
                    current_algorithm_val = self.settings.get("encryption_algorithm", "AES-256")
                    current_index = algorithms.index(current_algorithm_val) if current_algorithm_val in algorithms else 0
                    new_index = (current_index - 1 + len(algorithms)) % len(algorithms)
                    self.settings["encryption_algorithm"] = algorithms[new_index]
                    self.update_menu_items()
                elif self.selected_index == 1:  # Clipboard clear time
                    clear_time = self.settings.get("clipboard_clear_time", 30)
                    if clear_time > 0: # Assuming 0 is min, or maybe 5
                        self.settings["clipboard_clear_time"] = max(0, clear_time - 5)
                    self.update_menu_items()
            
            elif key == KEYBINDINGS["NAVIGATE_RIGHT"]:
                if self.selected_index == 0:  # Encryption algorithm
                    algorithms = ["AES-256", "ChaCha20", "Camellia"]
                    current_algorithm_val = self.settings.get("encryption_algorithm", "AES-256")
                    current_index = algorithms.index(current_algorithm_val) if current_algorithm_val in algorithms else 0
                    new_index = (current_index + 1) % len(algorithms)
                    self.settings["encryption_algorithm"] = algorithms[new_index]
                    self.update_menu_items()
                elif self.selected_index == 1:  # Clipboard clear time
                    clear_time = self.settings.get("clipboard_clear_time", 30)
                    if clear_time < 120: # Assuming 120 is max, or maybe 60
                        self.settings["clipboard_clear_time"] = min(120, clear_time + 5)
                    self.update_menu_items()
            
            # Handle terminal resize
            elif key == curses.KEY_RESIZE:
                self.resize()
                
            self.refresh()
    
    def change_master_password(self):
        """Change master password"""
        self.clear()
        self.draw_header("Change master password")
        # The footer for get_string_input is ["SAVE", "BACK_CANCEL", "PASTE_FROM_BUFFER"]
        # This initial footer for the screen itself:
        self.draw_footer(["SAVE", "BACK_CANCEL"]) 
        
        # Ask for current password
        # get_string_input will draw its own footer with SAVE, BACK_CANCEL, PASTE_FROM_BUFFER
        current_password = self.get_string_input("Current password: ", 3, 2, mask=True, show_footer=True)
        if not current_password:
            return False
            
        # Check if current password matches master password
        if current_password != self.settings.get("master_password", ""):
            self.draw_message("Incorrect password", self.height // 2, None, 4)
            self.stdscr.refresh()
            self.wait_for_key(["SELECT", "BACK_CANCEL"])
            return False
        
        # Ask for new password
        # get_string_input will draw its own footer
        new_password = self.get_string_input("New password: ", 5, 2, mask=True, show_footer=True)
        if not new_password:
            return False
            
        # Ask for password confirmation
        # get_string_input will draw its own footer
        confirm_password = self.get_string_input("Confirm password: ", 7, 2, mask=True, show_footer=True)
        if not confirm_password:
            return False
        
        # Check if new password and confirmation match
        if new_password != confirm_password:
            self.draw_message("Passwords do not match", self.height // 2, None, 4)
            self.stdscr.refresh()
            self.wait_for_key(["SELECT", "BACK_CANCEL"])
            return False
        
        # Set new password
        self.settings["master_password"] = new_password
        return True 