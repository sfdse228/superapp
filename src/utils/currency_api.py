"""
currency_api.py - Работа с API ЦБ РФ для получения курсов валют
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.utils.logger_setup import logger


class CurrencyAPI:
    """Класс для работы с API ЦБ РФ"""
    
    # Официальный API ЦБ РФ
    BASE_URL = "https://www.cbr-xml-daily.ru"
    
    # Доступные валюты
    CURRENCIES = {
        "USD": "Доллар США",
        "EUR": "Евро",
        "GBP": "Фунт стерлингов",
        "CNY": "Китайский юань",
        "JPY": "Японская иена",
        "CHF": "Швейцарский франк",
        "CAD": "Канадский доллар",
        "AUD": "Австралийский доллар",
        "TRY": "Турецкая лира",
        "KZT": "Казахстанский тенге",
        "UAH": "Украинская гривна",
        "BYN": "Белорусский рубль",
        "PLN": "Польский злотый",
        "SEK": "Шведская крона",
        "NOK": "Норвежская крона",
        "DKK": "Датская крона",
        "SGD": "Сингапурский доллар",
        "INR": "Индийская рупия",
        "BRL": "Бразильский реал",
        "ZAR": "Южноафриканский рэнд"
    }
    
    def __init__(self):
        self.cache_file = "data/currency_cache.json"
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Создаёт папку для кэша"""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
    
    def get_daily_rates(self) -> Dict[str, float]:
        """
        Получает курсы валют на сегодня
        
        Returns:
            Словарь {код_валюты: курс}
        """
        try:
            url = f"{self.BASE_URL}/daily_json.js"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rates = {}
            
            # Добавляем рубль (базовая валюта)
            rates["RUB"] = 1.0
            
            # Парсим курсы
            for code, info in data.get("Valute", {}).items():
                if code in self.CURRENCIES:
                    # Курс к рублю
                    nominal = info.get("Nominal", 1)
                    value = info.get("Value", 0)
                    rates[code] = value / nominal
            
            # Сохраняем в кэш
            self._save_cache(rates)
            logger.info(f"Получены курсы валют: {len(rates)} валют")
            return rates
            
        except requests.RequestException as e:
            logger.error(f"Ошибка получения курсов: {e}")
            # Пробуем загрузить из кэша
            return self._load_cache()
    
    def get_historical_rates(self, days: int = 30) -> Dict[str, List[Dict]]:
        """
        Получает исторические курсы валют
        
        Args:
            days: Количество дней истории
            
        Returns:
            Словарь с историей по каждой валюте
        """
        history = {}
        
        # Используем ежедневные архивы ЦБ
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%d/%m/%Y")
            
            try:
                url = f"{self.BASE_URL}/archive/{date.strftime('%Y')}/{date.strftime('%m')}/{date.strftime('%d')}/daily_json.js"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    for code, info in data.get("Valute", {}).items():
                        if code in self.CURRENCIES:
                            if code not in history:
                                history[code] = []
                            
                            nominal = info.get("Nominal", 1)
                            value = info.get("Value", 0)
                            rate = value / nominal
                            
                            history[code].append({
                                'date': date_str,
                                'rate': rate
                            })
                            
            except Exception as e:
                logger.warning(f"Не удалось получить данные за {date_str}: {e}")
                continue
        
        # Добавляем сегодняшние данные
        today_rates = self.get_daily_rates()
        today_str = datetime.now().strftime("%d/%m/%Y")
        for code, rate in today_rates.items():
            if code != "RUB" and code in self.CURRENCIES:
                if code not in history:
                    history[code] = []
                history[code].append({
                    'date': today_str,
                    'rate': rate
                })
        
        logger.info(f"Получена история курсов для {len(history)} валют")
        return history
    
    def _save_cache(self, rates: Dict[str, float]):
        """Сохраняет курсы в кэш"""
        try:
            cache_data = {
                'date': datetime.now().isoformat(),
                'rates': rates
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения кэша: {e}")
    
    def _load_cache(self) -> Dict[str, float]:
        """Загружает курсы из кэша"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info("Загружены курсы из кэша")
                    return data.get('rates', {})
        except Exception as e:
            logger.error(f"Ошибка загрузки кэша: {e}")
        
        return {}
    
    def get_currency_name(self, code: str) -> str:
        """Возвращает название валюты по коду"""
        return self.CURRENCIES.get(code, code)
