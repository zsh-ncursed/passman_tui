import curses
from .base import BaseWindow, KEYBINDINGS

class MainMenu(BaseWindow):
    """Main application menu"""
    
    def __init__(self, stdscr):
        """Initialization of the main menu"""
        super().__init__(stdscr)
        self.menu_items = [
            "Show records",
            "Add record",
            "Generate password",
            "Settings",
            "Exit"
        ]
        self.selected_index = 0
    
    def display(self):
        """Display the main menu"""
        while True:
            self.clear()
            self.draw_header("Password manager")
            # Pass the specific actions for the main menu footer
            self.draw_footer(["NAVIGATE_UP", "NAVIGATE_DOWN", "SELECT", "BACK_CANCEL"])
            
            # Draw menu
            self.draw_menu(self.menu_items, self.selected_index)
            
            # Input processing
            key = self.stdscr.getch()
            
            # Navigation
            if key == KEYBINDINGS["NAVIGATE_UP"] and self.selected_index > 0:
                self.selected_index -= 1
            elif key == KEYBINDINGS["NAVIGATE_DOWN"] and self.selected_index < len(self.menu_items) - 1:
                self.selected_index += 1
            # Select item
            elif key in KEYBINDINGS["SELECT"]:
                return self.selected_index
            # Exit (mapped to BACK_CANCEL as per typical UI, or could be a specific EXIT action)
            # For main menu, Esc usually means "Exit Application" which is the last item.
            elif key in KEYBINDINGS["BACK_CANCEL"]: 
                # In this specific menu, "Exit" is an explicit option.
                # Pressing Esc should probably select "Exit" or perform its action directly.
                # Current behavior: return index of "Exit" item. This seems fine.
                return len(self.menu_items) - 1
            # Handle terminal size change
            elif key == curses.KEY_RESIZE:
                self.resize()
                
            self.refresh() 