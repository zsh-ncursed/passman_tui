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
        """Display the main menu (optimized redraw)"""
        prev_selected = -1
        prev_size = (self.height, self.width)
        dirty = True
        while True:
            # Перерисовываем только если изменился выбор или размер окна
            if dirty or self.selected_index != prev_selected or (self.height, self.width) != prev_size:
                self.clear()
                self.draw_header("Password manager")
                self.draw_footer()
                self.draw_menu(self.menu_items, self.selected_index)
                self.refresh()
                prev_selected = self.selected_index
                prev_size = (self.height, self.width)
                dirty = False
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
                dirty = True
            # Если изменился выбор — пометить как dirty
            if self.selected_index != prev_selected or dirty:
                continue 