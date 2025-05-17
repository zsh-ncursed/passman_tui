#!/usr/bin/env python3
"""
Запуск менеджера паролей
"""

# Гарантируем, что наш модуль будет найден
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем приложение
try:
    from passman.app import main
    main()
except Exception as e:
    print(f"Ошибка: {e}")
    import traceback
    traceback.print_exc() 