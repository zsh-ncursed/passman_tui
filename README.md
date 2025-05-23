# Password Manager with TUI Interface

A secure and convenient application for password management with a text user interface (TUI), supporting data encryption, password generation, clipboard copy, and intuitive navigation.

## Version

Current version: 1.0.0

## Features

- Add, view, edit, and delete password entries
- Data encryption using AES-256, ChaCha20, or Camellia algorithms
- Secure password generation with customizable parameters
- Copy passwords to clipboard with auto-clear
- Intuitive TUI interface with arrow key navigation and hotkeys
- **Export/import**: encrypted archive of all data and settings (menu: Settings → Export/Import)
- Unicode support in all fields
- All data stored in `~/.passman/`
- **Note field**: up to 50 words, hidden by default, can be shown/hidden (V), copy to clipboard (N)

## Requirements

- Python 3.10 or higher
- Linux (main support)
- macOS (limited compatibility)
- Windows (via WSL)

## Project Structure

```
passman/
├── run.py              # Main entry point
├── launch.sh           # Launch script for different terminals
├── passman/           # Main package
│   ├── app.py         # Main application module
│   ├── crypto.py      # Encryption
│   ├── password_generator.py  # Password generation
│   ├── clipboard.py   # Clipboard operations
│   └── ui/           # UI components
│       ├── base.py    # Base window class
│       ├── main_menu.py  # Main menu
│       ├── password_entry.py  # Entry management
│       └── settings.py  # Settings
├── requirements.txt    # Project dependencies
├── setup.py           # Installation settings
└── README.md          # Documentation
```

## Installation

1. Clone the repository:
```
git clone https://github.com/zsh-ncursed/passman_tui.git
cd passman
```

2. Install dependencies:
```
pip install -r requirements.txt
```

## Usage

Start the application in one of the following ways:

```bash
# Automatic terminal selection
./launch.sh

# Or directly via Python
python run.py
```

On first launch, you will be prompted to create a master password, which will be used to encrypt your data.

### Navigation

The Text User Interface (TUI) provides context-specific keybindings that are dynamically displayed in the footer of each screen. This ensures that you always have the relevant commands visible for the current view or task.

Common global keys that are generally available:
- Arrow keys (`↑`, `↓`, `←`, `→`): Used for navigating through menus, lists, and sometimes for adjusting values in settings.
- `Enter`: Used for selecting menu items, confirming actions, or proceeding to the next step.
- `Esc`: Used for backing out of menus, canceling current operations, or closing dialogs.

Common actions like Copy, Generate, Settings, Save, Edit, Delete, etc., will have their respective hotkeys (e.g., `[c]`, `[g]`, `[S]`, `[s]`) displayed in the footer when they are available in the current context. Always refer to the footer for the most up-to-date keybindings for your current screen.

## Security

- All data is stored encrypted in the `~/.passman/` directory
- Modern encryption algorithms are used (AES-256 by default)
- Passwords and settings are never stored in plain text
- The `secrets` module is used for cryptographically secure password generation

## License

MIT 

## Changelog

### 1.0.1
- Note field now supports up to 50 words (word limit)
- Note is hidden by default, shown by pressing V
- In details, note can be copied (menu and hotkey N)
- In EditEntryWindow, note can be shown/hidden by pressing V
- In app.py, added copying note to clipboard 