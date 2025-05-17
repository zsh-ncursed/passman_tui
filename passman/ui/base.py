import curses
import os
import pyperclip

class BaseWindow:
    """Base class for TUI interface windows"""
    
    def __init__(self, stdscr):
        """Initialization of the base window"""
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        
        # If the terminal size is not defined correctly, set reasonable default values
        if self.height <= 1:
            self.height = 24
        if self.width <= 1:
            self.width = 80
            
        self.min_height = 10
        self.min_width = 40
        
        # Check the minimum window size
        if self.height < self.min_height or self.width < self.min_width:
            raise ValueError(f"Terminal size is too small. Minimum is {self.min_width}x{self.min_height}, current {self.width}x{self.height}")
        
        # Initialize colors
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, -1)  # Header
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Highlight
        curses.init_pair(3, curses.COLOR_GREEN, -1)  # Success
        curses.init_pair(4, curses.COLOR_RED, -1)  # Error
        curses.init_pair(5, curses.COLOR_YELLOW, -1)  # Warning
        curses.init_pair(6, curses.COLOR_CYAN, -1)  # Information
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Footer
        
        # Set keyboard mode
        curses.cbreak()
        curses.noecho()
        stdscr.keypad(True)
        curses.curs_set(0)  # Hide cursor
        
        # Clear screen
        stdscr.clear()
    
    def draw_header(self, title):
        """Drawing window header"""
        try:
            # Limit string length to prevent errors
            self.stdscr.addstr(0, 0, " " * (self.width - 1), curses.color_pair(1))
            self.stdscr.addstr(0, (self.width - len(title)) // 2, title[:self.width-1], curses.color_pair(1))
        except:
            # If an error occurs, try again with a shorter string
            try:
                self.stdscr.addstr(0, 0, " " * (self.width - 2), curses.color_pair(1))
                if len(title) > self.width - 2:
                    title = title[:self.width - 5] + "..."
                self.stdscr.addstr(0, 1, title, curses.color_pair(1))
            except:
                pass
    
    def draw_footer(self, commands=None):
        """Drawing bottom panel with hints"""
        if commands is None:
            commands = ["[↑↓] - Navigation", "[Enter] - Select", "[Esc] - Back"]
        
        footer_text = " | ".join(commands)
        try:
            self.stdscr.addstr(self.height - 1, 0, " " * (self.width - 1), curses.color_pair(1))
            if len(footer_text) > self.width - 2:
                footer_text = footer_text[:self.width - 5] + "..."
            self.stdscr.addstr(self.height - 1, (self.width - len(footer_text)) // 2, footer_text, curses.color_pair(1))
        except:
            try:
                self.stdscr.addstr(self.height - 1, 0, " " * (self.width - 2), curses.color_pair(1))
                self.stdscr.addstr(self.height - 1, 1, "Menu", curses.color_pair(1))
            except:
                pass
    
    def draw_menu(self, items, selected_index, start_y=2, start_x=2):
        """Drawing menu with highlighted selected item"""
        for i, item in enumerate(items):
            y = start_y + i
            if y >= self.height - 1:
                break
            
            item_str = str(item)
            # Limit string length
            max_width = self.width - start_x - 2
            if len(item_str) > max_width:
                item_str = item_str[:max_width-3] + "..."
                
            try:
                if i == selected_index:
                    self.stdscr.addstr(y, start_x, item_str.ljust(max_width), curses.color_pair(2))
                else:
                    self.stdscr.addstr(y, start_x, item_str)
            except:
                # Error handling during drawing
                pass
    
    def draw_message(self, message, y=None, x=None, color_pair=0):
        """Drawing message"""
        if y is None:
            y = self.height // 2
        
        # Limit message length
        max_width = self.width - 4
        if len(message) > max_width:
            message = message[:max_width-3] + "..."
            
        if x is None:
            x = (self.width - len(message)) // 2
            if x < 1:
                x = 1
                
        try:
            self.stdscr.addstr(y, x, message, curses.color_pair(color_pair))
        except:
            # Error handling during drawing
            try:
                self.stdscr.addstr(y, 1, message[:self.width-4], curses.color_pair(color_pair))
            except:
                pass
    
    def get_string_input(self, prompt, y, x, mask=False, max_length=50, show_footer=True):
        curses.echo()
        curses.curs_set(1)
        max_length = min(max_length, self.width - x - len(prompt) - 2)
        result = ""
        current_pos = 0
        try:
            self.stdscr.addstr(y, x, prompt)
            input_x = x + len(prompt)
        except:
            try:
                short_prompt = ">"
                self.stdscr.addstr(y, x, short_prompt)
                input_x = x + len(short_prompt)
            except:
                return ""
        while True:
            try:
                display = '*' * len(result) if mask else result
                self.stdscr.addstr(y, input_x, display + " " * (max_length - len(result)))
                self.stdscr.move(y, input_x + current_pos)
                if show_footer:
                    self.draw_footer(["[Enter] - Save", "[Esc] - Cancel", "[F2] - Insert from buffer"])
            except:
                pass
            key = self.stdscr.get_wch()  # Use get_wch for Unicode support
            if isinstance(key, str):
                if key == '\n' or key == '\r':
                    break
                elif key == '\x1b':  # Escape
                    result = ""
                    break
                elif key == '\x7f':  # Backspace
                    if current_pos > 0:
                        result = result[:current_pos-1] + result[current_pos:]
                        current_pos -= 1
                elif key == '\b':
                    if current_pos > 0:
                        result = result[:current_pos-1] + result[current_pos:]
                        current_pos -= 1
                elif len(result) < max_length and key.isprintable():
                    result = result[:current_pos] + key + result[current_pos:]
                    current_pos += 1
            elif isinstance(key, int):
                if key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                    if current_pos > 0:
                        result = result[:current_pos-1] + result[current_pos:]
                        current_pos -= 1
                elif key == curses.KEY_DC:
                    if current_pos < len(result):
                        result = result[:current_pos] + result[current_pos+1:]
                elif key == curses.KEY_LEFT and current_pos > 0:
                    current_pos -= 1
                elif key == curses.KEY_RIGHT and current_pos < len(result):
                    current_pos += 1
                elif key == curses.KEY_HOME:
                    current_pos = 0
                elif key == curses.KEY_END:
                    current_pos = len(result)
                elif key == curses.KEY_F2:
                    try:
                        clip = pyperclip.paste()
                        if clip:
                            insert = clip[:max_length-len(result)]
                            result = result[:current_pos] + insert + result[current_pos:]
                            current_pos += len(insert)
                    except Exception:
                        pass
        curses.noecho()
        curses.curs_set(0)
        return result
    
    def wait_for_key(self, allowed_keys=None):
        """Waiting for key press"""
        while True:
            key = self.stdscr.getch()
            if allowed_keys is None or key in allowed_keys:
                return key
    
    def refresh(self):
        """Screen update"""
        self.stdscr.refresh()
    
    def clear(self):
        """Clearing screen"""
        self.stdscr.clear()
    
    def resize(self):
        """Updating window size when terminal size changes"""
        self.height, self.width = self.stdscr.getmaxyx()
        self.clear()
        self.refresh() 