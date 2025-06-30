import curses
from .base import BaseWindow
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
        self.draw_footer(["[Enter] - Save", "[G] - Generate password", "[Esc] - Cancel"])
        
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
            if key == ord('g') or key == ord('G'):
                password = self.password_generator.generate_password()
                continue
            elif key in [10, 13]:  # Enter
                if password:
                    break
            elif key == 27:  # Escape
                return None
            elif key == curses.KEY_BACKSPACE or key == 127:
                password = password[:-1]
            elif 32 <= key <= 126:  # Printable characters
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
        """Display view records window (optimized redraw)"""
        prev_selected = -1
        prev_offset = -1
        prev_size = (self.height, self.width)
        dirty = True
        while True:
            if dirty or self.selected_index != prev_selected or self.offset != prev_offset or (self.height, self.width) != prev_size:
                self.clear()
                self.draw_header("Records list")
                self.draw_footer(["[↑↓] - Navigation", "[Enter] - Select", "[Esc] - Back"])
                if not self.entries:
                    self.draw_message("Records list is empty", self.height // 2, None, 5)
                    self.refresh()
                    key = self.wait_for_key([10, 13, 27])  # Enter or Escape
                    return None
                display_items = [f"{entry['service_name']} ({entry['username']})" for entry in self.entries]
                visible_items = display_items[self.offset:self.offset+self.items_per_page]
                self.draw_menu(visible_items, self.selected_index - self.offset)
                self.refresh()
                prev_selected = self.selected_index
                prev_offset = self.offset
                prev_size = (self.height, self.width)
                dirty = False
            key = self.stdscr.getch()
            if key == curses.KEY_UP:
                if self.selected_index > 0:
                    self.selected_index -= 1
                    if self.selected_index < self.offset:
                        self.offset = self.selected_index
            elif key == curses.KEY_DOWN:
                if self.selected_index < len(self.entries) - 1:
                    self.selected_index += 1
                    if self.selected_index >= self.offset + self.items_per_page:
                        self.offset += 1
            elif key == 10 or key == 13:  # Enter
                return self.selected_index
            elif key == 27:  # Escape
                return None
            elif key == curses.KEY_RESIZE:
                self.resize()
                self.items_per_page = self.height - 4
                dirty = True
            if self.selected_index != prev_selected or self.offset != prev_offset or dirty:
                continue


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
        """Display record details window (optimized redraw)"""
        prev_selected = -1
        prev_show_hidden = None
        prev_size = (self.height, self.width)
        dirty = True
        while True:
            if dirty or self.selected_index != prev_selected or self.show_hidden != prev_show_hidden or (self.height, self.width) != prev_size:
                self.clear()
                self.draw_header(f"Details: {self.entry['service_name']}")
                self.draw_footer(["[V] - Show/hide"])
                self.stdscr.addstr(2, 2, f"Service: {self.entry['service_name']}")
                self.stdscr.addstr(3, 2, f"Username: {self.entry['username']}")
                if self.show_hidden:
                    self.stdscr.addstr(4, 2, f"Password: {self.entry['password']}")
                else:
                    self.stdscr.addstr(4, 2, f"Password: {'*' * len(self.entry['password'])}")
                if self.entry.get('note'):
                    self.stdscr.addstr(5, 2, "Note:")
                    note_display = self.entry['note'] if self.show_hidden else '*' * min(len(self.entry['note']), 30)
                    note_lines = note_display.split('\n')
                    for i, line in enumerate(note_lines[:3]):
                        self.stdscr.addstr(6 + i, 4, line[:self.width-6])
                menu_start_y = 10 if self.entry.get('note') else 6
                self.draw_menu(self.menu_items, self.selected_index, start_y=menu_start_y)
                self.refresh()
                prev_selected = self.selected_index
                prev_show_hidden = self.show_hidden
                prev_size = (self.height, self.width)
                dirty = False
            key = self.stdscr.getch()
            if key == curses.KEY_UP and self.selected_index > 0:
                self.selected_index -= 1
            elif key == curses.KEY_DOWN and self.selected_index < len(self.menu_items) - 1:
                self.selected_index += 1
            elif key == 10 or key == 13:  # Enter
                return self.selected_index
            elif key == 27:  # Escape
                return len(self.menu_items) - 1  # Return selected item index
            elif key in [ord('l'), ord('L')]:
                return 0
            elif key in [ord('p'), ord('P')]:
                return 1
            elif key in [ord('n'), ord('N')]:
                return 2
            elif key in [ord('v'), ord('V')]:
                self.show_hidden = not self.show_hidden
            elif key == curses.KEY_RESIZE:
                self.resize()
                dirty = True
            if self.selected_index != prev_selected or self.show_hidden != prev_show_hidden or dirty:
                continue


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
        """Display edit record window (optimized redraw)"""
        prev_selected = -1
        prev_size = (self.height, self.width)
        dirty = True
        while True:
            if dirty or self.selected_index != prev_selected or (self.height, self.width) != prev_size:
                self.clear()
                self.draw_header("Edit record")
                self.stdscr.addstr(2, 2, "Current values:")
                self.stdscr.addstr(3, 4, f"Service: {self.entry['service_name']}")
                self.stdscr.addstr(4, 4, f"Username: {self.entry['username']}")
                self.stdscr.addstr(5, 4, f"Password: {'*' * len(self.entry['password'])}")
                if self.entry.get('note'):
                    note_preview = self.entry['note'][:30] + '...' if len(self.entry['note']) > 30 else self.entry['note']
                    self.stdscr.addstr(6, 4, f"Note: {note_preview}")
                else:
                    self.stdscr.addstr(6, 4, "Note: <empty>")
                self.stdscr.addstr(8, 2, "Select field to edit:")
                self.draw_menu(self.fields, self.selected_index, start_y=9)
                if self.selected_index == 2:  # Password field index
                    self.draw_footer(["[Enter] - Edit", "[G] - Generate", "[Esc] - Cancel"])
                else:
                    self.draw_footer(["[Enter] - Edit", "[Esc] - Cancel"])
                self.refresh()
                prev_selected = self.selected_index
                prev_size = (self.height, self.width)
                dirty = False
            key = self.stdscr.getch()
            if key == curses.KEY_UP and self.selected_index > 0:
                self.selected_index -= 1
            elif key == curses.KEY_DOWN and self.selected_index < len(self.fields) - 1:
                self.selected_index += 1
            elif key == 27:  # Escape
                return None
            elif key == 10 or key == 13:  # Enter
                if self.selected_index == 4:  # Save
                    return self.entry
                elif self.selected_index == 5:  # Cancel
                    return None
                else:
                    self.edit_field(self.selected_index)
                    dirty = True
            elif (key in [ord('g'), ord('G')]) and self.selected_index == 2:  # Password generation
                self.entry['password'] = self.password_generator.generate_password()
                dirty = True
            elif key == curses.KEY_RESIZE:
                self.resize()
                dirty = True
            if self.selected_index != prev_selected or (self.height, self.width) != prev_size or dirty:
                continue

    def edit_field(self, field_index):
        """Edit selected field"""
        field_name = self.fields[field_index]
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
                
                self.draw_footer([
                    "[←→] - Move cursor",
                    "[V] - Show/hide",
                    "[G] - Generate",
                    "[Enter] - Save",
                    "[Esc] - Cancel"
                ])
                
                key = self.stdscr.getch()
                
                if key in [ord('v'), ord('V')]:
                    show_password = not show_password
                elif key in [ord('g'), ord('G')]:
                    input_value = self.password_generator.generate_password()
                    cursor_pos = len(input_value)
                elif key == 27:  # Escape
                    return
                elif key in [10, 13]:  # Enter
                    if input_value:
                        self.entry[field_map[field_name]] = input_value
                    return
                elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                    if cursor_pos > 0:
                        input_value = input_value[:cursor_pos-1] + input_value[cursor_pos:]
                        cursor_pos -= 1
                elif key == curses.KEY_DC:  # Delete
                    if cursor_pos < len(input_value):
                        input_value = input_value[:cursor_pos] + input_value[cursor_pos+1:]
                elif key == curses.KEY_LEFT and cursor_pos > 0:
                    cursor_pos -= 1
                elif key == curses.KEY_RIGHT and cursor_pos < len(input_value):
                    cursor_pos += 1
                elif key == curses.KEY_HOME:
                    cursor_pos = 0
                elif key == curses.KEY_END:
                    cursor_pos = len(input_value)
                elif 32 <= key <= 126 and len(input_value) < 50:  # Printable characters
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
                self.stdscr.addstr(13, 2, input_prompt)
                self.stdscr.addstr(13, 2 + len(input_prompt), value[:self.width-20])
                self.stdscr.move(13, 2 + len(input_prompt) + cursor_pos)
                self.draw_footer(["[V] - Show/hide", "[Enter] - Save", "[Esc] - Cancel"])
                key = self.stdscr.getch()
                if key in [ord('v'), ord('V')]:
                    show_note = not show_note
                elif key == 27:
                    return
                elif key in [10, 13]:
                    # Ограничение по словам
                    words = re.findall(r'\S+', value)
                    if len(words) > 50:
                        value = ' '.join(words[:50])
                    self.entry[field_map[field_name]] = value
                    return
                elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                    if cursor_pos > 0:
                        value = value[:cursor_pos-1] + value[cursor_pos:]
                        cursor_pos -= 1
                elif key == curses.KEY_DC:
                    if cursor_pos < len(value):
                        value = value[:cursor_pos] + value[cursor_pos+1:]
                elif key == curses.KEY_LEFT and cursor_pos > 0:
                    cursor_pos -= 1
                elif key == curses.KEY_RIGHT and cursor_pos < len(value):
                    cursor_pos += 1
                elif key == curses.KEY_HOME:
                    cursor_pos = 0
                elif key == curses.KEY_END:
                    cursor_pos = len(value)
                elif 32 <= key <= 126 and len(re.findall(r'\S+', value)) < 50:
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