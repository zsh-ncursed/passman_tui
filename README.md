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

- Use arrow keys `↑↓` to navigate menus
- `Enter` to select menu item
- `Esc` to go back
- `c` to copy information to clipboard

## Security

- All data is stored encrypted in the `~/.passman/` directory
- Modern encryption algorithms are used (AES-256 by default)
- Passwords and settings are never stored in plain text
- The `secrets` module is used for cryptographically secure password generation

## License

MIT 

## Changelog

### 1.0.1
- Поле note теперь до 50 слов, ограничение по словам
- Note скрыт по умолчанию, отображается по V
- В details можно копировать note (меню и хоткей N)
- В EditEntryWindow при редактировании note — отображение/скрытие по V
- В app.py добавлено копирование note в буфер 