import curses
from .base import BaseWindow

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
            self.draw_footer()
            
            # Draw menu
            self.draw_menu(self.menu_items, self.selected_index)
            
            # Input processing
            key = self.stdscr.getch()
            
            # Navigation
            if key == curses.KEY_UP and self.selected_index > 0:
                self.selected_index -= 1
            elif key == curses.KEY_DOWN and self.selected_index < len(self.menu_items) - 1:
                self.selected_index += 1
            # Select item
            elif key == 10 or key == 13:  # Enter
                return self.selected_index
            # Exit
            elif key == 27:  # Escape
                return len(self.menu_items) - 1  # Return index of "Exit" item
            # Handle terminal size change
            elif key == curses.KEY_RESIZE:
                self.resize()
                
            self.refresh() 