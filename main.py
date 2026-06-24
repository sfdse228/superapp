#!/usr/bin/env python3
"""
main.py - Точка входа в SuperApp
"""

import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from src.main_window import MainWindow
from src.utils.logger_setup import logger


def main():
    """Главная функция"""
    try:
        app = QApplication(sys.argv)
        
        # Стиль приложения
        app.setStyle('Fusion')
        
        # Создаём и показываем окно
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
