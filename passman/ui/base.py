import curses
import os
import pyperclip

KEYBINDINGS = {
    "NAVIGATE_UP": curses.KEY_UP,
    "NAVIGATE_DOWN": curses.KEY_DOWN,
    "NAVIGATE_LEFT": curses.KEY_LEFT,
    "NAVIGATE_RIGHT": curses.KEY_RIGHT,
    "SELECT": [curses.KEY_ENTER, 10, 13],
    "BACK_CANCEL": [curses.KEY_EXIT, 27], # Escape key
    "COPY": ord('c'), # General copy, context-dependent
    "COPY_USERNAME": ord('l'), # 'l' for login/username
    "COPY_PASSWORD": ord('p'),
    "COPY_NOTE": ord('n'),
    "EDIT": ord('e'),
    "DELETE_ENTRY": [curses.KEY_DC, ord('d')], # For deleting a whole entry
    "DELETE_CHAR": curses.KEY_DC, # For deleting a character in input
    "BACKSPACE": [curses.KEY_BACKSPACE, 127, 8],
    "NEW": ord('n'), # 'n' for new entry in some contexts, conflicts with copy_note. Will need careful usage.
                     # For EntryDetailsWindow, ord('n') is for copy_note.
                     # For global actions, ord('n') might be for "New".
                     # This implies actions for draw_footer should be context-specific.
    "SAVE": ord('s'),
    "GENERATE": ord('g'),
    "SETTINGS": ord('S'),
    "SHOW_HIDE": ord('v'), # 'v' for view/toggle visibility
    "HELP": [ord('h'), curses.KEY_F1],
    "PASTE_FROM_BUFFER": curses.KEY_F2,
    "HOME": curses.KEY_HOME,
    "END": curses.KEY_END,
}

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
    
    def _get_key_display_name(self, key_name):
        """Helper function to get display names for keys."""
        key_values = KEYBINDINGS.get(key_name)
        if not key_values:
            return ""

        if not isinstance(key_values, list):
            key_values = [key_values]

        names = []
        for val in key_values:
            if val == curses.KEY_UP:
                names.append("↑")
            elif val == curses.KEY_DOWN:
                names.append("↓")
            elif val == curses.KEY_LEFT:
                names.append("←")
            elif val == curses.KEY_RIGHT:
                names.append("→")
            elif val in [curses.KEY_ENTER, 10, 13]:
                if "Enter" not in names: # Avoid duplicates like [Enter, Enter]
                    names.append("Enter")
            elif val in [curses.KEY_EXIT, 27]: # Escape
                if "Esc" not in names:
                    names.append("Esc")
            elif key_name == "DELETE_CHAR" and val == curses.KEY_DC: # Distinguish from DELETE_ENTRY
                names.append("Del")
            elif key_name == "DELETE_ENTRY" and val == curses.KEY_DC:
                 if "Del" not in names: names.append("Del") # Avoid Del/Del if 'd' is also there
            elif val == curses.KEY_DC and key_name != "DELETE_CHAR" and key_name != "DELETE_ENTRY": # Generic KEY_DC if used by other actions
                 if "Del" not in names: names.append("Del")
            elif val in KEYBINDINGS.get("BACKSPACE", []): # Check against the list for BACKSPACE
                 if "Bksp" not in names:
                    names.append("Bksp")
            elif curses.KEY_F0 <= val <= curses.KEY_F12:
                names.append(f"F{val - curses.KEY_F0}")
            elif isinstance(val, int) and 32 <= val <= 126: # Printable ASCII
                names.append(chr(val))
            # Add more specific key names if needed
        
        if not names: # Fallback for unhandled keys
            if isinstance(key_values[0], int):
                return f"Key({key_values[0]})" # e.g. for unmapped ord()
            return "?"

        return "/".join(names)


    def draw_footer(self, available_actions=None):
        """Drawing bottom panel with hints based on available actions."""
        if available_actions is None:
            # Default actions if none are provided for a specific window
            available_actions = ["NAVIGATE_UP", "NAVIGATE_DOWN", "SELECT", "BACK_CANCEL"]

        commands_list = []
        for action_name in available_actions:
            key_display = self._get_key_display_name(action_name)
            if key_display:
                # Make action name more readable, e.g., NAVIGATE_UP -> Navigate Up
                readable_action_name = action_name.replace("_", " ").title()
                commands_list.append(f"[{key_display}] - {readable_action_name}")
        
        footer_text = " | ".join(commands_list)
        try:
            self.stdscr.addstr(self.height - 1, 0, " " * (self.width - 1), curses.color_pair(1))
            if len(footer_text) > self.width - 2:
                # Attempt to intelligently shorten if too long
                if len(commands_list) > 1 :
                    condensed_list = []
                    max_len_per_command = (self.width - 2 - (len(commands_list) -1) * 3) // len(commands_list)
                    for cmd_full_text in commands_list:
                        if len(cmd_full_text) > max_len_per_command:
                            parts = cmd_full_text.split(" - ")
                            action_part = parts[1] if len(parts)>1 else parts[0]
                            condensed_list.append(f"{parts[0]} - {action_part[:max_len_per_command - len(parts[0]) -5]}...")
                        else:
                            condensed_list.append(cmd_full_text)
                    footer_text = " | ".join(condensed_list)
                else: # Single command, just truncate
                     footer_text = footer_text[:self.width - 5] + "..."

            self.stdscr.addstr(self.height - 1, (self.width - len(footer_text)) // 2, footer_text, curses.color_pair(1))
        except:
            try:
                self.stdscr.addstr(self.height - 1, 0, " " * (self.width - 2), curses.color_pair(1))
                # Fallback to a generic message if specific commands can't be drawn
                self.stdscr.addstr(self.height - 1, 1, "Actions available", curses.color_pair(1))
            except:
                pass # Final fallback: do nothing if screen is too small even for generic message
    
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
                    self.draw_footer(["SAVE", "BACK_CANCEL", "PASTE_FROM_BUFFER"])
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
                # Input handling in get_string_input using KEYBINDINGS
                if key in KEYBINDINGS.get("BACKSPACE", []) :
                    if current_pos > 0:
                        result = result[:current_pos-1] + result[current_pos:]
                        current_pos -= 1
                elif key == KEYBINDINGS.get("DELETE_CHAR"): # Using DELETE_CHAR for single char deletion
                    if current_pos < len(result):
                        result = result[:current_pos] + result[current_pos+1:]
                elif key == KEYBINDINGS.get("NAVIGATE_LEFT") and current_pos > 0:
                    current_pos -= 1
                elif key == KEYBINDINGS.get("NAVIGATE_RIGHT") and current_pos < len(result):
                    current_pos += 1
                elif key == KEYBINDINGS.get("HOME"):
                    current_pos = 0
                elif key == KEYBINDINGS.get("END"):
                    current_pos = len(result)
                elif key == KEYBINDINGS.get("PASTE_FROM_BUFFER"):
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
    
    def wait_for_key(self, allowed_actions=None):
        """Waiting for key press.
        'allowed_actions' is a list of action names from KEYBINDINGS.
        If None, any key press is returned.
        """
        target_keys = None
        if allowed_actions is not None:
            target_keys = []
            for action in allowed_actions:
                bound_keys = KEYBINDINGS.get(action)
                if bound_keys:
                    if isinstance(bound_keys, list):
                        target_keys.extend(bound_keys)
                    else:
                        target_keys.append(bound_keys)
            if not target_keys: # If allowed_actions were specified but none were valid/found
                # This case should ideally not happen if KEYBINDINGS and calls are correct.
                # Decide behavior: either allow all, or allow none (block until valid key for *something*).
                # For now, let's stick to allowing any key if the list ends up empty.
                pass


        while True:
            key = self.stdscr.getch() # Consider get_wch() for wider compatibility if issues arise
            if target_keys is None or key in target_keys:
                # To return the action name instead of the key code:
                # for action, keys in KEYBINDINGS.items():
                #     if action in (allowed_actions or []):
                #         if (isinstance(keys, list) and key in keys) or key == keys:
                #             return action
                return key # Returning the raw key is simpler for now.
                           # Callers can then check which action it corresponds to.
    
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