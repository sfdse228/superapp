"""
currency_widget.py - Виджет для отслеживания курсов валют
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QMessageBox, QDateEdit, QGroupBox
)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PyQt5.QtGui import QPainter, QColor, QFont

from src.utils.currency_api import CurrencyAPI
from src.utils.logger_setup import logger


class CurrencyWidget(QWidget):
    """Виджет для отображения курсов валют"""
    
    def __init__(self):
        super().__init__()
        self.api = CurrencyAPI()
        self.current_rates = {}
        self.history_data = {}
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("📈 Курсы валют ЦБ РФ")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)
        
        # Вкладки
        tabs = QTabWidget()
        
        # Вкладка 1: Текущие курсы
        current_tab = self.create_current_tab()
        tabs.addTab(current_tab, "Текущие курсы")
        
        # Вкладка 2: История
        history_tab = self.create_history_tab()
        tabs.addTab(history_tab, "История курсов")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def create_current_tab(self) -> QWidget:
        """Создаёт вкладку с текущими курсами"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Кнопка обновления
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("🔄 Обновить курсы")
        refresh_btn.clicked.connect(self.load_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Таблица с курсами
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Код", "Валюта", "Курс к RUB", "Дата"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        widget.setLayout(layout)
        return widget
    
    def create_history_tab(self) -> QWidget:
        """Создаёт вкладку с историей курсов"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Панель управления
        control_layout = QHBoxLayout()
        
        # Выбор валюты
        control_layout.addWidget(QLabel("Валюта:"))
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(sorted(CurrencyAPI.CURRENCIES.keys()))
        self.currency_combo.currentTextChanged.connect(self.update_history_chart)
        control_layout.addWidget(self.currency_combo)
        
        # Кнопка загрузки истории
        load_btn = QPushButton("📊 Показать историю")
        load_btn.clicked.connect(self.load_history)
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        control_layout.addWidget(load_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # График
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(400)
        layout.addWidget(self.chart_view)
        
        # Информация
        self.info_label = QLabel("Выберите валюту и нажмите 'Показать историю'")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("padding: 10px; color: #666;")
        layout.addWidget(self.info_label)
        
        widget.setLayout(layout)
        return widget
    
    def load_data(self):
        """Загружает и отображает текущие курсы"""
        try:
            self.current_rates = self.api.get_daily_rates()
            self.display_rates()
            logger.info("Курсы валют обновлены")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить курсы:\n{str(e)}")
            logger.error(f"Ошибка загрузки курсов: {e}")
    
    def display_rates(self):
        """Отображает курсы в таблице"""
        self.table.setRowCount(len(self.current_rates) - 1)  # -1 для RUB
        
        row = 0
        date_str = datetime.now().strftime("%d.%m.%Y")
        
        for code, rate in sorted(self.current_rates.items()):
            if code == "RUB":
                continue
            
            name = self.api.get_currency_name(code)
            
            self.table.setItem(row, 0, QTableWidgetItem(code))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(f"{rate:.4f}"))
            self.table.setItem(row, 3, QTableWidgetItem(date_str))
            
            # Выделяем популярные валюты
            if code in ["USD", "EUR", "GBP", "CNY"]:
                for col in range(4):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor(230, 240, 255))
            
            row += 1
        
        self.table.resizeColumnsToContents()
    
    def load_history(self):
        """Загружает историю курсов для выбранной валюты"""
        currency = self.currency_combo.currentText()
        if not currency:
            return
        
        try:
            self.history_data = self.api.get_historical_rates(30)
            self.update_history_chart()
            logger.info(f"Загружена история для {currency}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить историю:\n{str(e)}")
            logger.error(f"Ошибка загрузки истории: {e}")
    
    def update_history_chart(self):
        """Обновляет график истории курсов"""
        currency = self.currency_combo.currentText()
        
        if currency not in self.history_data or not self.history_data[currency]:
            self.show_empty_chart("Нет данных для отображения")
            return
        
        data = self.history_data[currency]
        data.sort(key=lambda x: x['date'])
        
        # Создаём серию
        series = QLineSeries()
        series.setName(f"{currency} / RUB")
        
        # Находим минимальное и максимальное значение для оси Y
        rates = [d['rate'] for d in data]
        min_rate = min(rates)
        max_rate = max(rates)
        
        for point in data:
            # Используем QDateTime для оси X
            dt = QDateTime.fromString(point['date'], "dd/MM/yyyy")
            timestamp = dt.toMSecsSinceEpoch()
            
            series.append(timestamp, point['rate'])
        
        # Создаём график
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"Курс {currency} к RUB")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Настройка оси X (даты)
        axis_x = QDateTimeAxis()
        axis_x.setFormat("dd.MM")
        axis_x.setTitleText("Дата")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Настройка оси Y (курс)
        axis_y = QValueAxis()
        axis_y.setTitleText("Курс")
        axis_y.setLabelFormat("%.4f")
        
        # Добавляем отступы для лучшего отображения
        margin = (max_rate - min_rate) * 0.1
        axis_y.setRange(min_rate - margin, max_rate + margin)
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        # Стилизация графика
        chart.setTheme(QChart.ChartThemeDark)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        self.chart_view.setChart(chart)
        
        # Обновляем информацию
        latest = data[-1]
        first = data[0]
        change = latest['rate'] - first['rate']
        change_percent = (change / first['rate']) * 100 if first['rate'] > 0 else 0
        
        self.info_label.setText(
            f"📊 {currency} {self.api.get_currency_name(currency)} | "
            f"Текущий курс: {latest['rate']:.4f} | "
            f"Изменение за период: {'+' if change > 0 else ''}{change:.4f} ({'+' if change_percent > 0 else ''}{change_percent:.2f}%)"
        )
    
    def show_empty_chart(self, message: str):
        """Показывает пустой график с сообщением"""
        chart = QChart()
        chart.setTitle(message)
        self.chart_view.setChart(chart)
        self.info_label.setText("")
