import curses
from .base import BaseWindow, KEYBINDINGS
from ..password_generator import PasswordGenerator
import re

class AddEntryWindow(BaseWindow):
    """Add new record window with password"""
    
    def __init__(self, stdscr):
        """Initialize add record window"""
        super().__init__(stdscr)
        self.password_generator = PasswordGenerator()
    
    def display(self):
        """Display add record window"""
        self.clear()
        self.draw_header("Add new record")
        self.draw_footer(["SAVE", "GENERATE", "BACK_CANCEL"])
        
        # Ask for service name
        service_name = self.get_string_input("Service name: ", 3, 2)
        if not service_name:
            return None
            
        # Ask for username
        username = self.get_string_input("Username: ", 5, 2)
        if not username:
            return None
            
        # Ask for password with masking
        password = ""
        while True:
            self.stdscr.move(7, 2)
            self.stdscr.clrtoeol()
            self.stdscr.addstr(7, 2, "Password: " + "*" * len(password))
            self.refresh()
            
            key = self.stdscr.getch()
            if key == KEYBINDINGS["GENERATE"]:
                password = self.password_generator.generate_password()
                # self.stdscr.addstr(7, 2 + len("Password: ") + len(password), "") # Clear potential old text, handled by clrtoeol
                continue
            elif key in KEYBINDINGS["SELECT"]:
                if password: # Require a password to save
                    break
            elif key in KEYBINDINGS["BACK_CANCEL"]:
                return None
            elif key in KEYBINDINGS["BACKSPACE"]:
                password = password[:-1]
            elif 32 <= key <= 126:  # Printable characters
                # TODO: This part could also use get_string_input for consistency,
                # but the current structure is a custom loop.
                # For now, just ensure max length for password is not exceeded.
                # Assuming a reasonable max password length, e.g., 256
                if len(password) < 256: 
                    password += chr(key)

        # Ask for note (до 50 слов)
        note = self.get_string_input("Note (up to 50 words): ", 9, 2, max_length=1000)
        if note and len(re.findall(r'\S+', note)) > 50:
            note = ' '.join(re.findall(r'\S+', note)[:50])
        
        return {
            "service_name": service_name,
            "username": username,
            "password": password,
            "note": note or ""
        }


class ViewEntriesWindow(BaseWindow):
    """View records window with passwords"""
    
    def __init__(self, stdscr, entries):
        """Initialize view records window"""
        super().__init__(stdscr)
        self.entries = entries
        self.selected_index = 0
        self.offset = 0
        self.items_per_page = self.height - 4  # Consider header and hints
    
    def display(self):
        """Display view records window"""
        while True:
            self.clear()
            self.draw_header("Records list")
            self.draw_footer(["NAVIGATE_UP", "NAVIGATE_DOWN", "SELECT", "BACK_CANCEL"])
            
            if not self.entries:
                self.draw_message("Records list is empty", self.height // 2, None, 5)
                # wait_for_key now expects action names
                self.wait_for_key(["SELECT", "BACK_CANCEL"]) 
                return None
                
            # Create list for display
            display_items = []
            for entry in self.entries:
                display_items.append(f"{entry['service_name']} ({entry['username']})")
            
            # Define visible range
            visible_items = display_items[self.offset:self.offset+self.items_per_page]
            
            # Draw list
            self.draw_menu(visible_items, self.selected_index - self.offset)
            
            # Input handling
            key = self.stdscr.getch()
            
            # Navigation
            if key == KEYBINDINGS["NAVIGATE_UP"]:
                if self.selected_index > 0:
                    self.selected_index -= 1
                    if self.selected_index < self.offset:
                        self.offset = self.selected_index
            elif key == KEYBINDINGS["NAVIGATE_DOWN"]:
                if self.selected_index < len(self.entries) - 1:
                    self.selected_index += 1
                    if self.selected_index >= self.offset + self.items_per_page:
                        self.offset += 1
            # Select record
            elif key in KEYBINDINGS["SELECT"]:
                return self.selected_index
            # Exit
            elif key in KEYBINDINGS["BACK_CANCEL"]:
                return None
            # Handle terminal size change
            elif key == curses.KEY_RESIZE:
                self.resize()
                self.items_per_page = self.height - 4
                
            self.refresh()


class EntryDetailsWindow(BaseWindow):
    """View record details window"""
    
    def __init__(self, stdscr, entry):
        """Initialize record details window"""
        super().__init__(stdscr)
        self.entry = entry
        self.menu_items = [
            "Copy login",
            "Copy password",
            "Copy note",
            "Edit record",
            "Delete record",
            "Back"
        ]
        self.selected_index = 0
        self.show_hidden = False
    
    def display(self):
        """Display record details window"""
        while True:
            self.clear()
            self.draw_header(f"Details: {self.entry['service_name']}")
            # Define actions for the footer. This might be a long list.
            footer_actions = [
                "SHOW_HIDE", "NAVIGATE_UP", "NAVIGATE_DOWN", "SELECT", "BACK_CANCEL",
                "COPY_USERNAME", "COPY_PASSWORD", "COPY_NOTE"
            ]
            self.draw_footer(footer_actions)
            
            # Display record details
            self.stdscr.addstr(2, 2, f"Service: {self.entry['service_name']}")
            self.stdscr.addstr(3, 2, f"Username: {self.entry['username']}")
            if self.show_hidden:
                self.stdscr.addstr(4, 2, f"Password: {self.entry['password']}")
            else:
                self.stdscr.addstr(4, 2, f"Password: {'*' * len(self.entry['password'])}")
            
            # Display note if it exists
            if self.entry.get('note'):
                self.stdscr.addstr(5, 2, "Note:")
                note_display = self.entry['note'] if self.show_hidden else '*' * min(len(self.entry['note']), 30)
                note_lines = note_display.split('\n')
                for i, line in enumerate(note_lines[:3]):
                    self.stdscr.addstr(6 + i, 4, line[:self.width-6])
            
            # Draw menu
            menu_start_y = 10 if self.entry.get('note') else 6
            self.draw_menu(self.menu_items, self.selected_index, start_y=menu_start_y)
            
            # Input handling
            key = self.stdscr.getch()
            
            # Navigation for the menu items
            if key == KEYBINDINGS["NAVIGATE_UP"] and self.selected_index > 0:
                self.selected_index -= 1
            elif key == KEYBINDINGS["NAVIGATE_DOWN"] and self.selected_index < len(self.menu_items) - 1:
                self.selected_index += 1
            # Select item from menu
            elif key in KEYBINDINGS["SELECT"]:
                return self.selected_index # This corresponds to actions like "Edit", "Delete", "Back"
            # Back / Cancel action
            elif key in KEYBINDINGS["BACK_CANCEL"]:
                # Typically "Back" is the last item in such menus.
                return len(self.menu_items) - 1 
            # Quick actions
            elif key == KEYBINDINGS["COPY_USERNAME"]:
                # Corresponds to "Copy login" menu item at index 0
                return 0 
            elif key == KEYBINDINGS["COPY_PASSWORD"]:
                # Corresponds to "Copy password" menu item at index 1
                return 1
            elif key == KEYBINDINGS["COPY_NOTE"]:
                # Corresponds to "Copy note" menu item at index 2
                # This was previously ord('n'), which now maps to COPY_NOTE.
                # Ensure KEYBINDINGS["NEW"] (also ord('n')) isn't active here if it's for creating new entries globally.
                return 2
            elif key == KEYBINDINGS["SHOW_HIDE"]:
                self.show_hidden = not self.show_hidden
            # Handle terminal size change
            elif key == curses.KEY_RESIZE:
                self.resize()
                
            self.refresh()


class EditEntryWindow(BaseWindow):
    """Edit record window"""
    
    def __init__(self, stdscr, entry):
        """Initialize edit record window"""
        super().__init__(stdscr)
        self.entry = entry.copy()  # Create copy of record
        self.password_generator = PasswordGenerator()
        self.fields = [
            "Service name",
            "Username",
            "Password",
            "Note",
            "Save",
            "Cancel"
        ]
        self.selected_index = 0
        
    def display(self):
        """Display edit record window"""
        while True:
            self.clear()
            self.draw_header("Edit record")
            
            # Display current values
            self.stdscr.addstr(2, 2, "Current values:")
            self.stdscr.addstr(3, 4, f"Service: {self.entry['service_name']}")
            self.stdscr.addstr(4, 4, f"Username: {self.entry['username']}")
            self.stdscr.addstr(5, 4, f"Password: {'*' * len(self.entry['password'])}")
            if self.entry.get('note'):
                note_preview = self.entry['note'][:30] + '...' if len(self.entry['note']) > 30 else self.entry['note']
                self.stdscr.addstr(6, 4, f"Note: {note_preview}")
            else:
                self.stdscr.addstr(6, 4, "Note: <empty>")

            # Display field selection menu
            self.stdscr.addstr(8, 2, "Select field to edit:")
            self.draw_menu(self.fields, self.selected_index, start_y=9)
            
            # Show password generation hint if password is selected
            if self.selected_index == 2:  # Password field index ("Password")
                self.draw_footer(["SELECT", "GENERATE", "BACK_CANCEL"])
            elif self.selected_index == 3: # Note field index
                 self.draw_footer(["SELECT", "SHOW_HIDE", "BACK_CANCEL"]) # Assuming 'V' for note visibility too
            else: # Service name, Username, Save, Cancel
                self.draw_footer(["SELECT", "BACK_CANCEL"])
            
            # Input handling
            key = self.stdscr.getch()
            
            if key == KEYBINDINGS["NAVIGATE_UP"] and self.selected_index > 0:
                self.selected_index -= 1
            elif key == KEYBINDINGS["NAVIGATE_DOWN"] and self.selected_index < len(self.fields) - 1:
                self.selected_index += 1
            elif key in KEYBINDINGS["BACK_CANCEL"]:
                return None # Cancel editing
            elif key in KEYBINDINGS["SELECT"]:
                if self.fields[self.selected_index] == "Save":
                    return self.entry
                elif self.fields[self.selected_index] == "Cancel":
                    return None
                else:
                    # This will call edit_field for "Service name", "Username", "Password", "Note"
                    self.edit_field(self.selected_index) 
            elif key == KEYBINDINGS["GENERATE"] and self.fields[self.selected_index] == "Password":
                self.entry['password'] = self.password_generator.generate_password()
                # No need to call edit_field, password is set directly. Refresh will show it.
            
            self.refresh()
    
    def edit_field(self, field_index): # field_index refers to ["Service name", "Username", "Password", "Note"]
        """Edit selected field"""
        field_name = self.fields[field_index] # "Service name", "Username", "Password", "Note"
        field_map = {
            "Service name": "service_name",
            "Username": "username",
            "Password": "password",
            "Note": "note"
        }
        
        current_value = self.entry[field_map[field_name]]
        
        # Clear input area
        for i in range(12, 15):
            self.stdscr.move(i, 2)
            self.stdscr.clrtoeol()

        if field_name == "Password":
            # Special handling for password
            show_password = False
            input_value = ""
            cursor_pos = 0
            
            while True:
                self.stdscr.move(12, 2)
                self.stdscr.clrtoeol()
                prompt = f"Current password: "
                self.stdscr.addstr(12, 2, prompt)
                
                # Display current password (hidden or visible)
                if show_password:
                    self.stdscr.addstr(current_value)
                else:
                    self.stdscr.addstr('*' * len(current_value))
                
                # Display input area
                self.stdscr.move(13, 2)
                self.stdscr.clrtoeol()
                input_prompt = "New password: "
                self.stdscr.addstr(13, 2, input_prompt)
                
                # Display entered password
                display_value = input_value if show_password else '*' * len(input_value)
                self.stdscr.addstr(13, 2 + len(input_prompt), display_value)
                
                # Position cursor
                self.stdscr.move(13, 2 + len(input_prompt) + cursor_pos)
                
                # Footer for password editing
                self.draw_footer([
                    "NAVIGATE_LEFT", "NAVIGATE_RIGHT", "HOME", "END", 
                    "SHOW_HIDE", "GENERATE", "SAVE", "BACK_CANCEL",
                    "BACKSPACE", "DELETE_CHAR" # Implicitly handled by loop but good for user
                ])
                
                key = self.stdscr.getch() # Consider get_wch for unicode if issues
                
                if key == KEYBINDINGS["SHOW_HIDE"]:
                    show_password = not show_password
                elif key == KEYBINDINGS["GENERATE"]:
                    input_value = self.password_generator.generate_password()
                    cursor_pos = len(input_value)
                elif key in KEYBINDINGS["BACK_CANCEL"]:
                    return # Cancel editing this field
                elif key in KEYBINDINGS["SELECT"]: # Using SELECT for save, consistent with get_string_input
                    if input_value: # Only save if not empty, or allow empty? Current: must not be empty.
                        self.entry[field_map[field_name]] = input_value
                    return # Finish editing this field
                elif key in KEYBINDINGS["BACKSPACE"]:
                    if cursor_pos > 0:
                        input_value = input_value[:cursor_pos-1] + input_value[cursor_pos:]
                        cursor_pos -= 1
                elif key == KEYBINDINGS["DELETE_CHAR"]:
                    if cursor_pos < len(input_value):
                        input_value = input_value[:cursor_pos] + input_value[cursor_pos+1:]
                elif key == KEYBINDINGS["NAVIGATE_LEFT"] and cursor_pos > 0:
                    cursor_pos -= 1
                elif key == KEYBINDINGS["NAVIGATE_RIGHT"] and cursor_pos < len(input_value):
                    cursor_pos += 1
                elif key == KEYBINDINGS["HOME"]:
                    cursor_pos = 0
                elif key == KEYBINDINGS["END"]:
                    cursor_pos = len(input_value)
                elif 32 <= key <= 126 and len(input_value) < 256:  # Printable characters, increased limit
                    input_value = input_value[:cursor_pos] + chr(key) + input_value[cursor_pos:]
                    cursor_pos += 1
                
                self.refresh()
        elif field_name == "Note":
            show_note = False
            value = current_value
            cursor_pos = len(value)
            while True:
                self.stdscr.move(12, 2)
                self.stdscr.clrtoeol()
                prompt = "Current note: "
                display_note = value if show_note else '*' * min(len(value), 30)
                self.stdscr.addstr(12, 2, prompt + display_note[:self.width-20])
                self.stdscr.move(13, 2)
                self.stdscr.clrtoeol()
                input_prompt = "New note (up to 50 words): "
                self.stdscr.addstr(13, 2, input_prompt) # No, input_prompt is "New note..."
                # Display the actual editable value
                self.stdscr.addstr(13, 2 + len(input_prompt), value) # Display full value for editing
                self.stdscr.move(13, 2 + len(input_prompt) + cursor_pos) # Move cursor correctly

                # Footer for note editing
                self.draw_footer([
                    "NAVIGATE_LEFT", "NAVIGATE_RIGHT", "HOME", "END",
                    "SHOW_HIDE", "SAVE", "BACK_CANCEL",
                    "BACKSPACE", "DELETE_CHAR"
                ])
                key = self.stdscr.getch() # Consider get_wch

                if key == KEYBINDINGS["SHOW_HIDE"]:
                    show_note = not show_note # This toggles the "Current note" display, not input
                elif key in KEYBINDINGS["BACK_CANCEL"]:
                    return # Cancel editing this field
                elif key in KEYBINDINGS["SELECT"]: # Save
                    words = re.findall(r'\S+', value)
                    if len(words) > 50: # Word limit
                        value = ' '.join(words[:50])
                    self.entry[field_map[field_name]] = value
                    return # Finish editing
                elif key in KEYBINDINGS["BACKSPACE"]:
                    if cursor_pos > 0:
                        value = value[:cursor_pos-1] + value[cursor_pos:]
                        cursor_pos -= 1
                elif key == KEYBINDINGS["DELETE_CHAR"]:
                    if cursor_pos < len(value):
                        value = value[:cursor_pos] + value[cursor_pos+1:]
                elif key == KEYBINDINGS["NAVIGATE_LEFT"] and cursor_pos > 0:
                    cursor_pos -= 1
                elif key == KEYBINDINGS["NAVIGATE_RIGHT"] and cursor_pos < len(value):
                    cursor_pos += 1
                elif key == KEYBINDINGS["HOME"]:
                    cursor_pos = 0
                elif key == KEYBINDINGS["END"]:
                    cursor_pos = len(value)
                # Allow any printable char, including spaces. Max length for notes is implicitly handled by screen width or later by get_string_input if used.
                # Max words check is only on save.
                elif 32 <= key <= 126: # Printable ASCII. Max length for notes can be large.
                     # Assuming max_length for notes around 1000 as used in AddEntryWindow's get_string_input
                    if len(value) < 1000:
                        value = value[:cursor_pos] + chr(key) + value[cursor_pos:]
                        cursor_pos += 1
                self.refresh()
        else:
            # For other fields, show current value and allow editing
            self.stdscr.addstr(12, 2, f"Current value: {current_value}")
            max_length = 200 if field_name == "Note" else 50
            value = self.get_string_input(f"New value: ", 13, 2, max_length=max_length)
            
            if value:
                self.entry[field_map[field_name]] = value 