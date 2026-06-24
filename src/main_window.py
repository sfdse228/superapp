"""
main_window.py - Главное окно SuperApp
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QStackedWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.navigation import NavigationWidget
from src.widgets.currency_widget import CurrencyWidget
from src.utils.logger_setup import logger


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SuperApp v1.0")
        self.setGeometry(100, 100, 1200, 700)
        self.init_ui()
        
        logger.info("SuperApp запущен")
    
    def init_ui(self):
        """Инициализация интерфейса"""
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Боковая панель с навигацией
        self.navigation = NavigationWidget()
        self.navigation.item_selected.connect(self.switch_widget)
        main_layout.addWidget(self.navigation)
        
        # Правая часть: заголовок + содержимое
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        main_layout.addWidget(right_panel, 1)
        
        # Заголовок
        self.title_label = QLabel("Добро пожаловать в SuperApp!")
        self.title_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.title_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 8px;")
        right_layout.addWidget(self.title_label)
        
        # Стек виджетов
        self.stack = QStackedWidget()
        right_layout.addWidget(self.stack, 1)
        
        # Регистрируем утилиты
        self.widgets = {}
        self.register_widgets()
        
        # Показываем первую утилиту
        self.navigation.setCurrentRow(0)
        self.switch_widget("currency")
    
    def register_widgets(self):
        """Регистрация всех утилит"""
        
        # Утилита 1: Курсы валют (реализована)
        currency_widget = CurrencyWidget()
        self.stack.addWidget(currency_widget)
        self.widgets["currency"] = (currency_widget, "💱 Курсы валют")
        
        # Утилита 2: Погода (заглушка)
        weather_widget = self.create_placeholder_widget(
            "🌤️ Прогноз погоды",
            "Функция будет добавлена в следующей версии\n\n"
            "Планируется:\n"
            "• Отображение текущей погоды\n"
            "• Прогноз на неделю\n"
            "• Интерактивные карты"
        )
        self.stack.addWidget(weather_widget)
        self.widgets["weather"] = (weather_widget, "🌤️ Погода")
        
        # Утилита 3: Заметки (заглушка)
        notes_widget = self.create_placeholder_widget(
            "📝 Заметки",
            "Функция будет добавлена в следующей версии\n\n"
            "Планируется:\n"
            "• Создание заметок\n"
            "• Категории и теги\n"
            "• Поиск по заметкам"
        )
        self.stack.addWidget(notes_widget)
        self.widgets["notes"] = (notes_widget, "📝 Заметки")
        
        # Утилита 4: Калькулятор (заглушка)
        calculator_widget = self.create_placeholder_widget(
            "🧮 Калькулятор",
            "Функция будет добавлена в следующей версии\n\n"
            "Планируется:\n"
            "• Обычный калькулятор\n"
            "• Инженерный режим\n"
            "• История вычислений"
        )
        self.stack.addWidget(calculator_widget)
        self.widgets["calculator"] = (calculator_widget, "🧮 Калькулятор")
        
        # Утилита 5: Список дел (заглушка)
        todo_widget = self.create_placeholder_widget(
            "✅ Список дел",
            "Функция будет добавлена в следующей версии\n\n"
            "Планируется:\n"
            "• Добавление задач\n"
            "• Приоритеты и сроки\n"
            "• Статус выполнения"
        )
        self.stack.addWidget(todo_widget)
        self.widgets["todo"] = (todo_widget, "✅ Список дел")
    
    def create_placeholder_widget(self, title: str, message: str) -> QWidget:
        """Создаёт виджет-заглушку для будущих утилит"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Заголовок
        label_title = QLabel(title)
        label_title.setFont(QFont("Arial", 24, QFont.Bold))
        label_title.setAlignment(Qt.AlignCenter)
        label_title.setStyleSheet("color: #4a6fa5; padding: 20px;")
        layout.addWidget(label_title)
        
        # Сообщение
        label_msg = QLabel(message)
        label_msg.setAlignment(Qt.AlignCenter)
        label_msg.setStyleSheet("font-size: 14px; color: #666; padding: 20px; background-color: #f9f9f9; border-radius: 10px;")
        label_msg.setWordWrap(True)
        layout.addWidget(label_msg)
        
        # Индикатор "В разработке"
        status = QLabel("🚧 В разработке")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("font-size: 18px; color: #ff9800; font-weight: bold; padding: 10px;")
        layout.addWidget(status)
        
        widget.setLayout(layout)
        return widget
    
    def switch_widget(self, widget_id: str):
        """Переключение между утилитами"""
        if widget_id in self.widgets:
            widget, title = self.widgets[widget_id]
            self.stack.setCurrentWidget(widget)
            self.title_label.setText(f"📱 {title}")
            
            # Обновляем выделение в навигации
            self.navigation.select_item_by_id(widget_id)
            
            logger.info(f"Переключено на утилиту: {title}")
    
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        reply = QMessageBox.question(
            self,
            "Выход",
            "Вы уверены, что хотите выйти из SuperApp?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("SuperApp закрыт")
            event.accept()
        else:
            event.ignore()
