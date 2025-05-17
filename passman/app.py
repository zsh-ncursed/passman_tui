import os
import json
import curses
from pathlib import Path

from .crypto import CryptoManager
from .password_generator import PasswordGenerator
from .clipboard import ClipboardManager
from .ui.main_menu import MainMenu
from .ui.password_entry import AddEntryWindow, ViewEntriesWindow, EntryDetailsWindow, EditEntryWindow
from .ui.password_generator import PasswordGeneratorWindow
from .ui.settings import SettingsWindow


class PasswordManager:
    """Main application class - password manager"""
    
    def __init__(self):
        """Initialize password manager"""
        self.home_dir = str(Path.home())
        self.storage_dir = Path(self.home_dir) / '.passman'
        self.storage_dir.mkdir(exist_ok=True)
        self.settings_file = 'settings'  # Without extension, CryptoManager will add .gpg
        self.data_file = 'passwords'
        self.entries = []
        self.settings = {
            'encryption_algorithm': 'AES-256',
            'clipboard_clear_time': 30,
            'master_password': ''
        }
        self._settings_crypto = None
        self._settings_loaded = False
        self.load_settings()
    
    def load_settings(self):
        """Load settings from encrypted file"""
        # If master password is not set, read regular json (first run)
        json_path = self.storage_dir / 'settings.json'
        if json_path.exists() and not self._settings_loaded:
            try:
                with open(json_path, 'r') as f:
                    settings = json.load(f)
                    self.settings.update(settings)
            except Exception:
                pass
        # If master password is already set, try to decrypt
        if self.settings['master_password']:
            self._settings_crypto = CryptoManager(
                password=self.settings['master_password'],
                algorithm=self.settings.get('encryption_algorithm', 'AES-256')
            )
            try:
                data = self._settings_crypto.load_from_file(self.settings_file)
                if data:
                    self.settings.update(data)
                    self._settings_loaded = True
            except Exception:
                pass
    
    def save_settings(self):
        """Save settings to encrypted file"""
        if not self._settings_crypto and self.settings['master_password']:
            self._settings_crypto = CryptoManager(
                password=self.settings['master_password'],
                algorithm=self.settings.get('encryption_algorithm', 'AES-256')
            )
        if self._settings_crypto:
            self._settings_crypto.save_to_file(self.settings, self.settings_file)
            # Remove open json if it existed
            json_path = self.storage_dir / 'settings.json'
            if json_path.exists():
                try:
                    os.remove(json_path)
                except Exception:
                    pass
        else:
            # First run, master password is not set
            json_path = self.storage_dir / 'settings.json'
            with open(json_path, 'w') as f:
                json.dump(self.settings, f)
    
    def authenticate(self, stdscr):
        """User authentication"""
        from .ui.base import BaseWindow
        window = BaseWindow(stdscr)
        settings_gpg_path = self.storage_dir / f'{self.settings_file}.gpg'
        if not settings_gpg_path.exists():
            while True:
                window.clear()
                window.draw_header("First run - setting master password")
                window.draw_footer(["[Enter] - Save", "[Esc] - Exit"])
                password = window.get_string_input("Enter master password: ", 3, 2, mask=True)
                if not password:
                    return False
                confirm = window.get_string_input("Confirm password: ", 5, 2, mask=True)
                if not confirm:
                    return False
                if password != confirm:
                    window.draw_message("Passwords do not match", window.height // 2, None, 4)
                    window.refresh()
                    window.wait_for_key([10, 13, 27])
                    continue
                self.settings['master_password'] = password
                self.save_settings()
                return True
        else:
            while True:
                window.clear()
                window.draw_header("Login to password manager")
                window.draw_footer(["[Enter] - Login", "[Esc] - Exit"])
                password = window.get_string_input("Enter master password: ", 3, 2, mask=True)
                if not password:
                    return False
                # Try to decrypt settings with this password
                try:
                    crypto = CryptoManager(password=password, algorithm=self.settings.get('encryption_algorithm', 'AES-256'))
                    data = crypto.load_from_file(self.settings_file)
                    if data:
                        self.settings.update(data)
                        self.settings['master_password'] = password
                        return True
                except Exception:
                    pass
                window.draw_message("Invalid password", window.height // 2, None, 4)
                window.refresh()
                window.wait_for_key([10, 13, 27])
    
    def load_data(self):
        """Load data from file"""
        # Initialize encryption manager
        crypto_manager = CryptoManager(
            password=self.settings.get('master_password', ''),
            algorithm=self.settings.get('encryption_algorithm', 'AES-256')
        )
        
        # Load data
        data = crypto_manager.load_from_file(self.data_file)
        if data:
            self.entries = data
        else:
            self.entries = []
    
    def save_data(self):
        """Save data to file"""
        # Initialize encryption manager
        crypto_manager = CryptoManager(
            password=self.settings.get('master_password', ''),
            algorithm=self.settings.get('encryption_algorithm', 'AES-256')
        )
        
        # Save data
        crypto_manager.save_to_file(self.entries, self.data_file)
    
    def run(self, stdscr):
        """Application launch"""
        # Authentication
        if not self.authenticate(stdscr):
            return
        
        # Load data
        self.load_data()
        
        # Initialize managers
        password_generator = PasswordGenerator()
        clipboard_manager = ClipboardManager()
        
        # Launch main menu
        while True:
            main_menu = MainMenu(stdscr)
            menu_choice = main_menu.display()
            
            # Handle menu item selection
            if menu_choice == 0:  # Show entries
                self.view_entries(stdscr, clipboard_manager)
            elif menu_choice == 1:  # Add entry
                self.add_entry(stdscr)
            elif menu_choice == 2:  # Generate password
                self.generate_password(stdscr, password_generator, clipboard_manager)
            elif menu_choice == 3:  # Settings
                self.show_settings(stdscr)
            elif menu_choice == 4:  # Exit
                break
    
    def view_entries(self, stdscr, clipboard_manager):
        """View and manage entries"""
        while True:
            view_window = ViewEntriesWindow(stdscr, self.entries)
            selected_index = view_window.display()
            
            if selected_index is None:
                break
                
            # Display selected entry
            details_window = EntryDetailsWindow(stdscr, self.entries[selected_index])
            details_choice = details_window.display()
            
            # Handle entry selection action
            if details_choice == 0:  # Copy login
                clipboard_manager.copy_to_clipboard(
                    self.entries[selected_index]['username'],
                    clear_after=self.settings.get('clipboard_clear_time', 30)
                )
            elif details_choice == 1:  # Copy password
                clipboard_manager.copy_to_clipboard(
                    self.entries[selected_index]['password'],
                    clear_after=self.settings.get('clipboard_clear_time', 30)
                )
            elif details_choice == 2:  # Edit entry
                edit_window = EditEntryWindow(stdscr, self.entries[selected_index])
                updated_entry = edit_window.display()
                
                if updated_entry:
                    self.entries[selected_index] = updated_entry
                    self.save_data()
            elif details_choice == 3:  # Delete entry
                # Create base window for entry deletion confirmation
                from .ui.base import BaseWindow
                window = BaseWindow(stdscr)
                
                window.clear()
                window.draw_header("Delete entry")
                window.draw_footer(["[y] - Yes", "[n] - No"])
                
                window.draw_message(f"Are you sure you want to delete entry '{self.entries[selected_index]['service_name']}'?", window.height // 2, None, 5)
                window.refresh()
                
                key = window.wait_for_key([ord('y'), ord('Y'), ord('n'), ord('N'), 27])
                if key in [ord('y'), ord('Y')]:
                    del self.entries[selected_index]
                    self.save_data()
    
    def add_entry(self, stdscr):
        """Add new entry"""
        add_window = AddEntryWindow(stdscr)
        entry = add_window.display()
        
        if entry:
            self.entries.append(entry)
            self.save_data()
    
    def generate_password(self, stdscr, password_generator, clipboard_manager):
        """Generate password"""
        password_window = PasswordGeneratorWindow(stdscr, password_generator)
        password = password_window.display()
        
        if password:
            clipboard_manager.copy_to_clipboard(
                password,
                clear_after=self.settings.get('clipboard_clear_time', 30)
            )
    
    def show_settings(self, stdscr):
        """Display settings"""
        settings_window = SettingsWindow(stdscr, self.settings)
        updated_settings = settings_window.display()
        
        if updated_settings:
            # If encryption algorithm changed, reencrypt data
            if updated_settings.get('encryption_algorithm') != self.settings.get('encryption_algorithm'):
                self.settings = updated_settings
                self.save_data()
            
            self.settings = updated_settings
            self.save_settings()


def main():
    """Application entry point"""
    password_manager = PasswordManager()
    curses.wrapper(password_manager.run) 