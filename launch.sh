#!/bin/bash

# Получаем абсолютный путь к директории скрипта
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# Переходим в директорию проекта
cd "$SCRIPT_DIR" || { echo "Не удалось перейти в директорию: $SCRIPT_DIR"; exit 1; }

# Проверяем наличие файла run.py
if [ ! -f "run.py" ]; then
  echo "Файл run.py не найден в директории: $SCRIPT_DIR"
  exit 1
fi

# Определяем интерпретатор Python
PYTHON_CMD=""
if command -v python3 &>/dev/null; then
  PYTHON_CMD="python3"  # Приоритет Python 3, если доступен
elif command -v python &>/dev/null; then
  PYTHON_CMD="python"   # Резервный вариант (например, Arch Linux)
else
  echo "Python не установлен. Установите Python и попробуйте снова."
  exit 1
fi

# Запускаем Python-скрипт
"$PYTHON_CMD" run.py