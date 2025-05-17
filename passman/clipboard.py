import pyperclip
import time
import threading

class ClipboardManager:
    """Manager for clipboard operations"""
    
    def __init__(self):
        """Initialize clipboard manager"""
        self.timer = None
    
    def copy_to_clipboard(self, text, clear_after=30):
        """
        Copies text to clipboard
        
        Args:
            text: Text to copy
            clear_after: Time in seconds to clear clipboard after (0 - never clear)
        """
        try:
            pyperclip.copy(text)
            
            # Stop previous timer if it exists
            if self.timer and self.timer.is_alive():
                self.timer.cancel()
            
            # Start timer to clear if needed
            if clear_after > 0:
                self.timer = threading.Timer(clear_after, self.clear_clipboard)
                self.timer.daemon = True
                self.timer.start()
                
            return True
        except Exception as e:
            return False
    
    def clear_clipboard(self):
        """Clears clipboard"""
        try:
            pyperclip.copy('')
            return True
        except Exception as e:
            return False 