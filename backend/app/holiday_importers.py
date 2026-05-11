import json
import urllib.request
import urllib.parse
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Holiday
from app.database import SessionLocal

class HolidayImporter:
    """Импортёр праздников из внешних API"""
    
    def __init__(self, db: Session):
        self.db = db
        self.results = {}
    
    def import_all(self):
        """Запускает импорт из всех источников"""
        print("📥 Начинаем импорт праздников...")
        
        self.results = {
            "nager_date": self.import_from_nager_date(),
            "abstract_api": self.import_from_abstract_api(),
            "calendarific": self.import_from_calendarific()
        }
        
        # Считаем общее количество
        total = sum(r["imported"] for r in self.results.values())
        self.results["total"] = total
        
        print(f"✅ Импорт завершён. Всего добавлено: {total} праздников")
        return self.results
    
    def _is_duplicate(self, name: str, month: int, day: int) -> bool:
        """Проверяет, существует ли уже такой праздник (по названию И дате)"""
        # Проверяем точное совпадение названия и даты
        existing = self.db.query(Holiday).filter(
            Holiday.name == name,
            Holiday.month == month,
            Holiday.day == day
        ).first()
    
        if existing:
            return True
    
        # Проверяем похожие названия (например, "Victory Day" и "День Победы" в одну дату)
        from sqlalchemy import func
        similar = self.db.query(Holiday).filter(
            func.lower(Holiday.name) == func.lower(name),
            Holiday.month == month,
            Holiday.day == day
        ).first()
    
        return similar is not None
    
    def _add_holiday(self, name: str, day: int, month: int, holiday_type: str, 
                     region: str, description: str, events: list = None,
                     wikipedia_url: str = "") -> bool:
        """Добавляет праздник в БД. Возвращает True если добавлен"""
        if self._is_duplicate(name, month, day):
            return False
        
        holiday = Holiday(
            name=name,
            day=day,
            month=month,
            type=holiday_type,
            region=region,
            description=description,
            events=json.dumps(events if events else []),
            wikipedia_url=wikipedia_url
        )
        self.db.add(holiday)
        return True
    
    def import_from_nager_date(self):
        """
        Импорт из Nager.Date API (бесплатный, без ключа)
        Источник: https://date.nager.at
        """
        print("📅 Импорт из Nager.Date API...")
        
        result = {
            "source": "Nager.Date API",
            "url": "https://date.nager.at",
            "checked": 0,
            "imported": 0,
            "skipped": 0,
            "errors": 0,
            "holiday_types": {}
        }
        
        try:
            # Получаем праздники для России и мира на 2026 год
            countries = ["RU", "UA", "BY", "KZ"]  # Россия, Украина, Беларусь, Казахстан
            year = 2026
            
            for country_code in countries:
                try:
                    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"
                    
                    req = urllib.request.Request(url, headers={'User-Agent': 'EcoKolendar/1.0'})
                    
                    with urllib.request.urlopen(req, timeout=10) as response:
                        if response.getcode() == 200:
                            data = json.loads(response.read().decode('utf-8'))
                            
                            for h in data:
                                result["checked"] += 1
                                
                                try:
                                    name = h.get('localName') or h.get('name')
                                    date_parts = h['date'].split('-')
                                    month = int(date_parts[1]) - 1  # 0-индексация
                                    day = int(date_parts[2])
                                    
                                    holiday_type = "national" if country_code == "RU" else "world"
                                    region = "russia" if country_code == "RU" else "world"
                                    
                                    types = h.get('types', [])
                                    description = f"Официальный праздник: {h.get('name', '')}. "
                                    description += f"Тип: {', '.join(types) if types else 'Публичный'}. "
                                    description += f"Страна: {h.get('countryCode', '')}"
                                    
                                    if self._add_holiday(name, day, month, holiday_type, region, description):
                                        result["imported"] += 1
                                        
                                        # Считаем типы
                                        for t in types:
                                            result["holiday_types"][t] = result["holiday_types"].get(t, 0) + 1
                                    else:
                                        result["skipped"] += 1
                                        
                                except Exception as e:
                                    result["errors"] += 1
                                    print(f"Ошибка обработки праздника: {e}")
                
                except Exception as e:
                    print(f"Ошибка для страны {country_code}: {e}")
        
        except Exception as e:
            print(f"Ошибка импорта из Nager.Date: {e}")
            result["errors"] += 1
        
        self.db.commit()
        return result
    
    def import_from_abstract_api(self):
        """Импорт из Abstract API (бесплатно 1000 запросов/мес)"""
        print("🎄 Импорт из Abstract API...")
    
        result = {
            "source": "Abstract Holidays API",
            "url": "https://www.abstractapi.com/holidays-api",
            "checked": 0,
            "imported": 0,
            "skipped": 0,
            "errors": 0,
            "holiday_types": {}
        }
    
        try:
            import os
            api_key = os.getenv("ABSTRACT_API_KEY", "")
        
            if not api_key or api_key == "your_abstract_api_key_here":
                result["errors"] = 0
                result["message"] = "API ключ не настроен. Получите ключ на https://www.abstractapi.com/holidays-api"
                return result
        
            # Страны и год
            countries = ["RU", "US", "GB", "FR", "DE"]
            year = 2026
        
            for country in countries:
                try:
                    url = "https://holidays.abstractapi.com/v1/"
                    params = {
                        "api_key": api_key,
                        "country": country,
                        "year": year,
                        "language": "ru"
                    }
                
                    full_url = f"{url}?{urllib.parse.urlencode(params)}"
                    print(f"Запрос к Abstract API: страна={country}, год={year}")
                
                    req = urllib.request.Request(full_url, headers={'User-Agent': 'EcoKolendar/1.0'})
                
                    with urllib.request.urlopen(req, timeout=15) as response:
                        if response.getcode() == 200:
                            raw_data = response.read().decode('utf-8')
                            print(f"Ответ Abstract API ({country}): {raw_data[:200]}...")
                        
                            data = json.loads(raw_data)
                        
                            # Abstract API может вернуть список или объект с полем holidays
                            holidays = data if isinstance(data, list) else data.get('holidays', [])
                        
                            for h in holidays:
                                result["checked"] += 1
                            
                                try:
                                    name = h.get('name', '')
                                    if not name:
                                        continue
                                
                                    # Пробуем разные форматы даты
                                    date_str = h.get('date') or h.get('date_time', '')
                                    if not date_str:
                                        continue
                                
                                    try:
                                        date_obj = datetime.strptime(date_str[:10], '%Y-%m-%d')
                                    except:
                                        date_obj = datetime.strptime(date_str[:10], '%m/%d/%Y')
                                
                                    month = date_obj.month - 1  # 0-индексация
                                    day = date_obj.day
                                
                                    holiday_type = "world"
                                    region = "russia" if country == "RU" else "world"
                                
                                    h_type = h.get('type', 'National')
                                    location = h.get('location', country)
                                    description = f"Международный праздник: {name}. "
                                    description += f"Тип: {h_type}. "
                                    description += f"Страна: {location}"
                                
                                    if self._add_holiday(name, day, month, holiday_type, region, description):
                                        result["imported"] += 1
                                        result["holiday_types"][h_type] = result["holiday_types"].get(h_type, 0) + 1
                                    else:
                                        result["skipped"] += 1
                            
                                except Exception as e:
                                    result["errors"] += 1
                                    print(f"Ошибка обработки праздника из Abstract API: {e}")
            
                except urllib.error.HTTPError as e:
                    print(f"HTTP ошибка для Abstract API ({country}): {e.code} - {e.reason}")
                    if e.code == 401:
                        result["message"] = "Неверный API ключ Abstract"
                    elif e.code == 429:
                        result["message"] = "Превышен лимит запросов Abstract API"
                except Exception as e:
                    print(f"Ошибка для страны {country} в Abstract API: {e}")
    
        except Exception as e:
            print(f"Общая ошибка Abstract API: {e}")
            result["errors"] += 1
    
        self.db.commit()
        return result
    
    def import_from_calendarific(self):
        """
        Импорт из Calendarific API
        Документация: https://calendarific.com/api-documentation
        Бесплатно: 1000 запросов/мес
        """
        print("🗓️ Импорт из Calendarific API...")
        
        result = {
            "source": "Calendarific API",
            "url": "https://calendarific.com",
            "checked": 0,
            "imported": 0,
            "skipped": 0,
            "errors": 0,
            "holiday_types": {}
        }
        
        try:
            import os
            api_key = os.getenv("CALENDARIFIC_API_KEY", "")
            
            if not api_key:
                result["errors"] = 1
                result["message"] = "API ключ не настроен (CALENDARIFIC_API_KEY в .env)"
                return result
            
            # Страны и год
            countries = ["ru", "ua", "by", "kz", "us", "gb", "fr", "de"]
            year = 2026
            
            for country in countries:
                try:
                    url = f"https://calendarific.com/api/v2/holidays"
                    params = {
                        "api_key": api_key,
                        "country": country,
                        "year": year,
                        "language": "ru"
                    }
                    
                    full_url = f"{url}?{urllib.parse.urlencode(params)}"
                    
                    req = urllib.request.Request(full_url, headers={'User-Agent': 'EcoKolendar/1.0'})
                    
                    with urllib.request.urlopen(req, timeout=10) as response:
                        if response.getcode() == 200:
                            data = json.loads(response.read().decode('utf-8'))
                            
                            holidays = data.get('response', {}).get('holidays', [])
                            
                            for h in holidays:
                                result["checked"] += 1
                                
                                try:
                                    name = h.get('name', '')
                                    date_obj = datetime.strptime(h.get('date', {}).get('iso', ''), '%Y-%m-%d')
                                    month = date_obj.month - 1
                                    day = date_obj.day
                                    
                                    holiday_type = "world"
                                    region = "russia" if country == "ru" else "world"
                                    
                                    h_types = h.get('type', [])
                                    description = h.get('description', '') or f"Праздник: {name}. "
                                    description += f"Тип: {', '.join(h_types)}. "
                                    description += f"Страна: {h.get('country', {}).get('name', country)}"
                                    
                                    if self._add_holiday(name, day, month, holiday_type, region, description):
                                        result["imported"] += 1
                                        
                                        for t in h_types:
                                            result["holiday_types"][t] = result["holiday_types"].get(t, 0) + 1
                                    else:
                                        result["skipped"] += 1
                                
                                except Exception as e:
                                    result["errors"] += 1
                
                except Exception as e:
                    print(f"Ошибка для страны {country}: {e}")
        
        except Exception as e:
            print(f"Ошибка импорта из Calendarific: {e}")
            result["errors"] += 1
        
        self.db.commit()
        return result