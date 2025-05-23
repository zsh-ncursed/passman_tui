import curses
import os
import pyperclip

# KEYBINDINGS Configuration:
# This dictionary maps action names to their properties, which include:
#   - "keys": A curses key code (e.g., curses.KEY_UP) or a list of key codes
#             (e.g., [curses.KEY_ENTER, 10, 13] for Enter key variations).
#             These are the actual key values that the application will listen for.
#   - "display_name": A human-readable string describing the action (e.g., "Navigate Up").
#                     This is used for full display in the footer when space permits.
#   - "short_name": An abbreviated version of the display_name (e.g., "Sel" for "Select").
#                   Used in the footer when space is limited. Optional.
#   - "is_nav_key": A boolean flag (True/False). If True, the action is considered a
#                   primary navigation or simple editing key (like arrows, Home, End, Backspace, Del).
#                   In the footer, these are typically displayed as just their key symbol(s)
#                   (e.g., "[↑]") without the display_name, to save space. Optional, defaults to False if not present.
KEYBINDINGS = {
    "NAVIGATE_UP":       { "keys": curses.KEY_UP, "display_name": "Navigate Up", "is_nav_key": True },
    "NAVIGATE_DOWN":     { "keys": curses.KEY_DOWN, "display_name": "Navigate Down", "is_nav_key": True },
    "NAVIGATE_LEFT":     { "keys": curses.KEY_LEFT, "display_name": "Navigate Left", "is_nav_key": True },
    "NAVIGATE_RIGHT":    { "keys": curses.KEY_RIGHT, "display_name": "Navigate Right", "is_nav_key": True },
    "SELECT":            { "keys": [curses.KEY_ENTER, 10, 13], "display_name": "Select", "short_name": "Sel" },
    "BACK_CANCEL":       { "keys": [curses.KEY_EXIT, 27], "display_name": "Back/Cancel", "short_name": "Esc" },
    "COPY":              { "keys": ord('c'), "display_name": "Copy", "short_name": "Cpy" },
    "COPY_USERNAME":     { "keys": ord('l'), "display_name": "Copy User", "short_name": "User" },
    "COPY_PASSWORD":     { "keys": ord('p'), "display_name": "Copy Pass", "short_name": "Pass" },
    "COPY_NOTE":         { "keys": ord('n'), "display_name": "Copy Note", "short_name": "Note" }, # 'n'
    "EDIT":              { "keys": ord('e'), "display_name": "Edit", "short_name": "Edit" },
    "DELETE_ENTRY":      { "keys": [curses.KEY_DC, ord('D')], "display_name": "Delete Entry", "short_name": "Del" }, # Changed to 'D'
    "DELETE_CHAR":       { "keys": curses.KEY_DC, "display_name": "Delete Char", "is_nav_key": True }, # Character Del
    "BACKSPACE":         { "keys": [curses.KEY_BACKSPACE, 127, 8], "display_name": "Backspace", "is_nav_key": True },
    "NEW":               { "keys": ord('N'), "display_name": "New", "short_name": "New" }, # Changed to 'N'
    "SAVE":              { "keys": ord('s'), "display_name": "Save", "short_name": "Save" },
    "GENERATE":          { "keys": ord('g'), "display_name": "Generate", "short_name": "Gen" },
    "SETTINGS":          { "keys": ord('S'), "display_name": "Settings", "short_name": "Set" }, # Capital S
    "SHOW_HIDE":         { "keys": ord('v'), "display_name": "Show/Hide", "short_name": "View" },
    "HELP":              { "keys": [ord('h'), curses.KEY_F1], "display_name": "Help", "short_name": "Help" },
    "PASTE_FROM_BUFFER": { "keys": curses.KEY_F2, "display_name": "Paste", "short_name": "Paste" },
    "HOME":              { "keys": curses.KEY_HOME, "display_name": "Home", "is_nav_key": True },
    "END":               { "keys": curses.KEY_END, "display_name": "End", "is_nav_key": True },
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
    
    def _get_key_display_name(self, action_key_name):
        """
        Helper function to convert an action's key codes into a human-readable string of symbols.

        This function consults the `KEYBINDINGS` dictionary for the given `action_key_name`.
        It translates curses key constants (e.g., `curses.KEY_UP`) into symbols (e.g., "↑")
        and printable characters (e.g., `ord('c')`) into the character itself (e.g., "c").
        If an action has multiple keys assigned (e.g., Enter and keypad Enter), they are
        joined by "/".

        Args:
            action_key_name (str): The name of the action (a key in `KEYBINDINGS`).

        Returns:
            str: A string representing the key symbols for the action (e.g., "↑", "Esc", "c/Ctrl+C").
                 Returns an empty string if the action is not found or has no keys.
                 Returns "?" or a raw key name as a fallback for unmapped/unrecognized keys.
        """
        action_info = KEYBINDINGS.get(action_key_name)
        if not action_info or "keys" not in action_info:
            return ""

        key_codes = action_info["keys"]
        if not isinstance(key_codes, list):
            key_codes = [key_codes]

        names = []
        for val in key_codes:
            if val == curses.KEY_UP: names.append("↑")
            elif val == curses.KEY_DOWN: names.append("↓")
            elif val == curses.KEY_LEFT: names.append("←")
            elif val == curses.KEY_RIGHT: names.append("→")
            elif val in [curses.KEY_ENTER, 10, 13]:
                if "Enter" not in names: names.append("Enter")
            elif val in [curses.KEY_EXIT, 27]: # Escape
                if "Esc" not in names: names.append("Esc")
            elif val == curses.KEY_DC: # Delete Character (covers DELETE_CHAR and part of DELETE_ENTRY)
                if "Del" not in names: names.append("Del")
            elif val in [curses.KEY_BACKSPACE, 127, 8]: # Backspace
                 if "Bksp" not in names: names.append("Bksp")
            elif curses.KEY_F0 <= val <= curses.KEY_F12: names.append(f"F{val - curses.KEY_F0}")
            elif val == curses.KEY_HOME: 
                if "Home" not in names: names.append("Home")
            elif val == curses.KEY_END:
                if "End" not in names: names.append("End")
            elif isinstance(val, int) and 32 <= val <= 126: # Printable ASCII
                char_repr = chr(val)
                # Avoid duplicate char display if key is same as one from list (e.g. 'D' in DELETE_ENTRY)
                if char_repr not in names : names.append(char_repr)
        
        if not names: # Fallback
            try: 
                # For keys like KEY_DC that might not have a special char above but are valid names
                if isinstance(key_codes[0], int) and key_codes[0] > 0:
                    raw_name = curses.keyname(key_codes[0]).decode('utf-8')
                    # Make some common ones prettier
                    if raw_name.startswith('KEY_'): raw_name = raw_name[4:]
                    if raw_name == "DC": return "Del"
                    return raw_name
                return "?"
            except: return "?"
        return "/".join(names)

    def _generate_footer_segments(self, actions_to_display, use_short_names=False):
        """
        Generates a list of string segments for the footer, one for each action.

        Args:
            actions_to_display (list): A list of action names (keys from KEYBINDINGS).
            use_short_names (bool): If True, uses the 'short_name' from KEYBINDINGS
                                    for non-navigation actions. Otherwise, uses 'display_name'.

        Returns:
            list: A list of formatted strings, e.g., ["[↑]", "[Esc] - Back/Cancel"].
        """
        segments = []
        for action_name in actions_to_display:
            action_info = KEYBINDINGS.get(action_name)
            if not action_info: continue
            
            key_display = self._get_key_display_name(action_name)
            if not key_display: continue

            if action_info.get("is_nav_key"):
                segments.append(f"[{key_display}]")
            else:
                text = action_info.get("short_name") if use_short_names else action_info.get("display_name")
                if not text: text = action_name.replace("_", " ").title() # Fallback if names missing
                segments.append(f"[{key_display}] - {text}")
        return segments

    def draw_footer(self, available_actions=None):
        """
        Draws the bottom footer panel with hints, adapting to terminal width.
        The method attempts several strategies to make the footer fit:
        1. Initial Format: Displays navigation keys as symbols (e.g., "[↑]") and other
           actions with their full display name (e.g., "[S] - Save").
        2. Short Names: If the initial format is too wide, it tries using the 'short_name'
           for non-navigation actions (e.g., "[S] - Save" might use a short name if defined).
        3. Drop Non-Essential Actions: If still too wide, it iteratively removes actions
           that are not in the 'essential_actions' set (e.g., "HELP" might be dropped
           before "SELECT"). Actions are generally removed from the end of the provided list.
        4. Final Truncation: As a last resort, if the footer text is still too long
           (e.g., due to a single very long action name or an extremely narrow terminal),
           it truncates the string and appends "...".
        Error handling is included to prevent crashes on very small terminal sizes.
        """
        min_safe_width_for_generic_message = 10 # e.g., for "Menu" + padding
        if self.width < min_safe_width_for_generic_message:
            try: # Minimal possible footer for extremely tiny screen
                self.stdscr.addstr(self.height - 1, 0, " " * (self.width), curses.color_pair(1))
                if self.width > 1: self.stdscr.addstr(self.height - 1, 0, "." * self.width, curses.color_pair(1))
            except: pass
            return

        if available_actions is None or not available_actions:
            available_actions = ["NAVIGATE_UP", "NAVIGATE_DOWN", "SELECT", "BACK_CANCEL"]
        
        actions_to_render = list(available_actions) # Start with all actions

        # Attempt 1: Full names, nav keys simplified
        commands_list = self._generate_footer_segments(actions_to_render, use_short_names=False)
        footer_text = " | ".join(commands_list)

        # Attempt 2: Short names, nav keys simplified
        if len(footer_text) > self.width - 2 and len(commands_list) > 0:
            commands_list_short = self._generate_footer_segments(actions_to_render, use_short_names=True)
            footer_text_short = " | ".join(commands_list_short)
            if len(footer_text_short) <= self.width - 2 or len(footer_text_short) < len(footer_text): # Use if it fits or is shorter
                footer_text = footer_text_short
                commands_list = commands_list_short 
        
        # Attempt 3: Drop non-essential actions if still too long
        # Essential actions are less likely to be dropped.
        essential_actions = {"SELECT", "BACK_CANCEL", "SAVE", "NAVIGATE_UP", "NAVIGATE_DOWN", "NAVIGATE_LEFT", "NAVIGATE_RIGHT"}
        
        # We use the list of actions (actions_to_render) to decide who to drop,
        # then regenerate the command segments.
        temp_actions_for_dropping = list(actions_to_render)

        while len(footer_text) > self.width - 2 and len(temp_actions_for_dropping) > 1:
            dropped_an_action = False
            # Try to drop the last non-essential action
            for i in range(len(temp_actions_for_dropping) - 1, -1, -1):
                action_name_to_drop = temp_actions_for_dropping[i]
                if action_name_to_drop not in essential_actions:
                    temp_actions_for_dropping.pop(i)
                    dropped_an_action = True
                    break
            
            if not dropped_an_action: # All remaining are essential, or only one action left
                # If all are essential, just pop the last one to try to make space
                if len(temp_actions_for_dropping) > 1 : # Check to prevent emptying the list if all are essential
                     temp_actions_for_dropping.pop()
                else: # Only one item left and it's too long, break and let truncation handle it
                    break

            actions_to_render = list(temp_actions_for_dropping) # Update the list of actions to render
            commands_list = self._generate_footer_segments(actions_to_render, use_short_names=True) # Rebuild with short names
            footer_text = " | ".join(commands_list)
            if not dropped_an_action and len(temp_actions_for_dropping) <=1 : # Break if stuck
                break
        
        # Final truncation if still too long (e.g. one item is too long for screen)
        if len(footer_text) > self.width - 2:
            footer_text = footer_text[:max(0, self.width - 2 - 3)] + "..." 
            if self.width - 2 < 3: footer_text = "..." if self.width > 2 else ""

        try:
            self.stdscr.addstr(self.height - 1, 0, " " * (self.width -1), curses.color_pair(1)) # Clear line
            start_x = (self.width - len(footer_text)) // 2
            if start_x < 0: start_x = 0
            
            # Ensure the string does not exceed the screen width from start_x
            drawable_footer_text = footer_text
            if start_x + len(footer_text) > self.width -1 :
                drawable_footer_text = footer_text[:max(0, self.width - 1 - start_x)]

            if self.height - 1 >= 0 and len(drawable_footer_text) > 0 :
                 self.stdscr.addstr(self.height - 1, start_x, drawable_footer_text, curses.color_pair(1))
        except curses.error:
            try: # Fallback to a very generic message if all else fails
                self.stdscr.addstr(self.height - 1, 0, " " * (self.width-1), curses.color_pair(1))
                generic_msg = "Actions"
                if self.width -2 > len(generic_msg):
                    self.stdscr.addstr(self.height - 1, 1, generic_msg, curses.color_pair(1))
                elif self.width > 1: # even more generic if "Actions" doesn't fit
                    self.stdscr.addstr(self.height - 1, 1, "...", curses.color_pair(1))
            except:
                pass # Absolute fallback: do nothing
    
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
                # Input handling in get_string_input using new KEYBINDINGS structure
                if key in KEYBINDINGS.get("BACKSPACE", {}).get("keys", []):
                    if current_pos > 0:
                        result = result[:current_pos-1] + result[current_pos:]
                        current_pos -= 1
                elif key == KEYBINDINGS.get("DELETE_CHAR", {}).get("keys"):
                    if current_pos < len(result):
                        result = result[:current_pos] + result[current_pos+1:]
                elif key == KEYBINDINGS.get("NAVIGATE_LEFT", {}).get("keys") and current_pos > 0:
                    current_pos -= 1
                elif key == KEYBINDINGS.get("NAVIGATE_RIGHT", {}).get("keys") and current_pos < len(result):
                    current_pos += 1
                elif key == KEYBINDINGS.get("HOME", {}).get("keys"):
                    current_pos = 0
                elif key == KEYBINDINGS.get("END", {}).get("keys"):
                    current_pos = len(result)
                elif key == KEYBINDINGS.get("PASTE_FROM_BUFFER", {}).get("keys"):
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
                for action_name in allowed_actions: # allowed_actions are names like "SELECT"
                    action_info = KEYBINDINGS.get(action_name)
                    if action_info and "keys" in action_info:
                        bound_keys = action_info["keys"]
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