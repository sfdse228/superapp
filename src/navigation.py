"""
navigation.py - Навигация между утилитами
"""

from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import pyqtSignal


class NavigationWidget(QListWidget):
    """Виджет навигации с переключением между утилитами"""
    
    item_selected = pyqtSignal(str)  # Сигнал при выборе утилиты
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setMaximumWidth(200)
        self.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                border: none;
                padding: 10px 0;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px 20px;
                margin: 2px 10px;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background-color: #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #4a6fa5;
                color: white;
            }
        """)
        
        # Добавляем пункты меню
        items = [
            ("💱", "Курсы валют", "currency"),
            ("🌤️", "Погода", "weather"),
            ("📝", "Заметки", "notes"),
            ("🧮", "Калькулятор", "calculator"),
            ("✅", "Список дел", "todo"),
        ]
        
        for icon, name, widget_id in items:
            item = QListWidgetItem(f"{icon}  {name}")
            item.setData(Qt.UserRole, widget_id)
            item.setToolTip(f"Перейти к утилите: {name}")
            self.addItem(item)
        
        # Выбираем первый пункт по умолчанию
        if self.count() > 0:
            self.setCurrentRow(0)
            self.itemClicked.emit(self.item(0))
        
        self.itemClicked.connect(self.on_item_clicked)
    
    def on_item_clicked(self, item):
        """Обработка клика по пункту меню"""
        widget_id = item.data(Qt.UserRole)
        self.item_selected.emit(widget_id)
    
    def select_item_by_id(self, widget_id: str):
        """Выбирает пункт меню по ID"""
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.UserRole) == widget_id:
                self.setCurrentRow(i)
                break
