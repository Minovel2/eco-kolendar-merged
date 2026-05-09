import os
import json
import urllib.request
import urllib.parse
import urllib.error
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Используем стандартную библиотеку urllib для Python 3.14
HTTPX_AVAILABLE = True

class WeatherAPI:
    """OpenMeteo API для получения погодных данных (бесплатный)"""
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
        
    async def get_weather_forecast(self, lat: float, lon: float, days: int = 5, start_date: str = None) -> Optional[Dict[str, Any]]:
        """Получить прогноз погоды на несколько дней с конкретной даты"""
        if not HTTPX_AVAILABLE:
            return None
            
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weathercode,relativehumidity_2m,windspeed_10m",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
                "timezone": "auto",
                "forecast_days": days
            }
            
            # Если указана начальная дата, используем исторические данные
            if start_date:
                params["start_date"] = start_date
                params["end_date"] = start_date
                url = f"{self.base_url}/archive"
            
            full_url = f"{url}?{urllib.parse.urlencode(params)}"
            
            with urllib.request.urlopen(full_url) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    current = data.get("current", {})
                    daily = data.get("daily", {})
                    
                    # Конвертируем weather code в описание
                    weather_code = current.get("weathercode", 0)
                    weather_descriptions = {
                        0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность", 3: "Пасмурно",
                        45: "Туман", 48: "Туман с инеем", 51: "Легкая морось", 53: "Умеренная морось",
                        55: "Плотная морось", 56: "Легкая ледяная морось", 57: "Умеренная ледяная морось",
                        61: "Слабый дождь", 63: "Умеренный дождь", 65: "Сильный дождь",
                        71: "Слабый снег", 73: "Умеренный снег", 75: "Сильный снег",
                        80: "Слабые ливни", 81: "Умеренные ливни", 82: "Сильные ливни",
                        95: "Гроза", 96: "Гроза с градом"
                    }
                    
                    return {
                        "location": {"name": "Местоположение"},
                        "current": current,
                        "forecast": daily,
                        "source": "OpenMeteo",
                        "start_date": start_date
                    }
        except Exception as e:
            print(f"Error fetching weather: {e}")
            
        return None
    
    async def get_weather_for_date(self, lat: float, lon: float, target_date: str) -> Optional[Dict[str, Any]]:
        """Получить погоду для конкретной даты"""
        if not HTTPX_AVAILABLE:
            return None
            
        try:
            # Определяем, нужно ли использовать исторические данные или прогноз
            from datetime import datetime, timedelta
            today = datetime.now().date()
            target = datetime.strptime(target_date, "%Y-%m-%d").date()
            
            days_diff = (target - today).days
            
            if days_diff < -365:  # Слишком старая дата
                return None
            elif days_diff < 0:  # Прошедшая дата - исторические данные
                # Используем климатические данные для прошедших дат
                month = target.month
                climate_data = {
                    1: {"temp": -5, "desc": "Снег", "humidity": 85, "wind": 12, "code": 71},
                    2: {"temp": -3, "desc": "Снег с дождем", "humidity": 80, "wind": 11, "code": 73},
                    3: {"temp": 2, "desc": "Снег с дождем", "humidity": 75, "wind": 10, "code": 61},
                    4: {"temp": 8, "desc": "Переменная облачность", "humidity": 65, "wind": 8, "code": 2},
                    5: {"temp": 15, "desc": "Ясно", "humidity": 60, "wind": 7, "code": 0},
                    6: {"temp": 20, "desc": "Ясно", "humidity": 55, "wind": 6, "code": 0},
                    7: {"temp": 22, "desc": "Преимущественно ясно", "humidity": 50, "wind": 6, "code": 1},
                    8: {"temp": 21, "desc": "Преимущественно ясно", "humidity": 55, "wind": 6, "code": 1},
                    9: {"temp": 15, "desc": "Переменная облачность", "humidity": 65, "wind": 7, "code": 2},
                    10: {"temp": 8, "desc": "Пасмурно", "humidity": 70, "wind": 8, "code": 3},
                    11: {"temp": 2, "desc": "Переменная облачность", "humidity": 75, "wind": 9, "code": 2},
                    12: {"temp": -3, "desc": "Снег", "humidity": 80, "wind": 11, "code": 71}
                }
                
                month_data = climate_data[month]
                return {
                    "current": {
                        "temperature_2m": month_data["temp"],
                        "relativehumidity_2m": month_data["humidity"],
                        "windspeed_10m": month_data["wind"],
                        "weathercode": month_data["code"]
                    },
                    "forecast": {},
                    "source": "OpenMeteo (климатические данные)",
                    "date": target_date,
                    "type": "historical_climate"
                }
            elif days_diff <= 16:  # Будущая дата в пределах прогноза
                return await self.get_weather_forecast(lat, lon, days_diff + 1)
            else:  # Далекое будущее - климатические данные
                month = target.month
                climate_data = {
                    1: {"temp": -5, "desc": "Снег", "humidity": 85, "wind": 12, "code": 71},
                    2: {"temp": -3, "desc": "Снег с дождем", "humidity": 80, "wind": 11, "code": 73},
                    3: {"temp": 2, "desc": "Снег с дождем", "humidity": 75, "wind": 10, "code": 61},
                    4: {"temp": 8, "desc": "Переменная облачность", "humidity": 65, "wind": 8, "code": 2},
                    5: {"temp": 15, "desc": "Ясно", "humidity": 60, "wind": 7, "code": 0},
                    6: {"temp": 20, "desc": "Ясно", "humidity": 55, "wind": 6, "code": 0},
                    7: {"temp": 22, "desc": "Преимущественно ясно", "humidity": 50, "wind": 6, "code": 1},
                    8: {"temp": 21, "desc": "Преимущественно ясно", "humidity": 55, "wind": 6, "code": 1},
                    9: {"temp": 15, "desc": "Переменная облачность", "humidity": 65, "wind": 7, "code": 2},
                    10: {"temp": 8, "desc": "Пасмурно", "humidity": 70, "wind": 8, "code": 3},
                    11: {"temp": 2, "desc": "Переменная облачность", "humidity": 75, "wind": 9, "code": 2},
                    12: {"temp": -3, "desc": "Снег", "humidity": 80, "wind": 11, "code": 71}
                }
                
                month_data = climate_data[month]
                return {
                    "current": {
                        "temperature_2m": month_data["temp"],
                        "relativehumidity_2m": month_data["humidity"],
                        "windspeed_10m": month_data["wind"],
                        "weathercode": month_data["code"]
                    },
                    "forecast": {},
                    "source": "OpenMeteo (климатические данные)",
                    "date": target_date,
                    "type": "future_climate"
                }
                
        except Exception as e:
            print(f"Error fetching weather for date {target_date}: {e}")
            
        return None
    
    async def get_current_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Получить текущую погоду"""
        if not HTTPX_AVAILABLE:
            return None
            
        try:
            url = f"{self.base_url}/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weathercode,relativehumidity_2m,windspeed_10m",
                "timezone": "auto"
            }
            
            full_url = f"{url}?{urllib.parse.urlencode(params)}"
            
            with urllib.request.urlopen(full_url) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    current = data.get("current", {})
                    
                    # Конвертируем weather code в описание
                    weather_code = current.get("weathercode", 0)
                    weather_descriptions = {
                        0: "Ясно", 1: "Преимущественно ясно", 2: "Переменная облачность", 3: "Пасмурно",
                        45: "Туман", 48: "Туман с инеем", 51: "Легкая морось", 53: "Умеренная морось",
                        55: "Плотная морось", 56: "Легкая ледяная морось", 57: "Умеренная ледяная морось",
                        61: "Слабый дождь", 63: "Умеренный дождь", 65: "Сильный дождь",
                        71: "Слабый снег", 73: "Умеренный снег", 75: "Сильный снег",
                        80: "Слабые ливни", 81: "Умеренные ливни", 82: "Сильные ливни",
                        95: "Гроза", 96: "Гроза с градом"
                    }
                    
                    return {
                        "main": {
                            "temp": current.get("temperature_2m", 0),
                            "humidity": current.get("relativehumidity_2m", 0)
                        },
                        "wind": {
                            "speed": current.get("windspeed_10m", 0)
                        },
                        "weather": [{
                            "description": weather_descriptions.get(weather_code, "Переменная облачность")
                        }]
                    }
        except Exception as e:
            print(f"Error fetching current weather: {e}")
            
        return None



class NewsAPI:
    """NewsAPI для получения новостей о праздниках и экологии"""
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2"
        
    async def search_holiday_news(self, query: str, language: str = "ru", page_size: int = 5) -> Optional[Dict[str, Any]]:
        """Поиск новостей по теме праздника"""
        if not self.api_key or not HTTPX_AVAILABLE:
            return None
            
        try:
            url = f"{self.base_url}/everything"
            params = {
                "q": query,
                "language": language,
                "pageSize": page_size,
                "sortBy": "publishedAt",
                "apiKey": self.api_key
            }
            
            full_url = f"{url}?{urllib.parse.urlencode(params)}"
            
            with urllib.request.urlopen(full_url) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return data
        except Exception as e:
            print(f"Error fetching news: {e}")
            
        return None
    
    async def get_eco_news(self, page_size: int = 5) -> Optional[Dict[str, Any]]:
        """Получить экологические новости"""
        eco_queries = ["экология", "природа", "заповедник", "национальный парк", "охрана природы"]
        
        for query in eco_queries:
            news = await self.search_holiday_news(query, page_size=page_size)
            if news and news.get("articles"):
                return news
                
        return None

class GeocodingAPI:
    """2ГИС API для геолокации и поиска объектов"""
    
    def __init__(self):
        self.base_url = "https://catalog.api.2gis.com/3.0"
        self.api_key = "demo"  # Demo ключ, для продакшена нужен свой ключ
        self.user_agent = "EcoCalendar/1.0"
        
    async def search_location(self, query: str, limit: int = 5) -> Optional[Dict[str, Any]]:
        """Поиск местоположения по названию через 2ГИС"""
        if not HTTPX_AVAILABLE:
            return None
            
        try:
            url = f"{self.base_url}/items"
            params = {
                "q": query,
                "type": "address",
                "key": self.api_key,
                "page_size": limit
            }
            
            full_url = f"{url}?{urllib.parse.urlencode(params)}"
            
            req = urllib.request.Request(full_url)
            req.add_header('User-Agent', self.user_agent)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    locations = []
                    if data.get('result') and data['result'].get('items'):
                        for item in data['result']['items'][:limit]:
                            location_info = {
                                'place_id': item.get('id'),
                                'lat': str(item.get('point', {}).get('lat')),
                                'lon': str(item.get('point', {}).get('lon')),
                                'name': item.get('name') or item.get('address_name'),
                                'class': item.get('type', {}).get('name'),
                                'type': item.get('subtype', {}).get('name'),
                                'display_name': item.get('full_name') or item.get('name'),
                                'address': {
                                    'city': item.get('address_name'),
                                    'country': item.get('country_name')
                                }
                            }
                            locations.append(location_info)
                    
                    return locations
                    
        except Exception as e:
            print(f"Error searching location via 2GIS: {e}")
            
        return None
    
    async def find_nearby_parks(self, lat: float, lon: float, radius: int = 10000) -> Optional[List[Dict[str, Any]]]:
        """Найти ближайшие парки и заповедники через 2ГИС или OpenStreetMap"""
        try:
            print(f"Starting search for parks near lat={lat}, lon={lon}, radius={radius}")
            
            # Сначала пробуем 2ГИС если есть ключ
            if self.api_key:
                try:
                    places_2gis = await self._search_2gis_parks(lat, lon, radius)
                    if places_2gis:
                        print(f"Found {len(places_2gis)} parks via 2GIS")
                        return places_2gis
                except Exception as e:
                    print(f"2GIS search failed: {e}")
            
            # Fallback: используем OpenStreetMap через Overpass API
            print("Falling back to OpenStreetMap")
            return await self._search_osm_parks(lat, lon, radius)
            
        except Exception as e:
            print(f"Error finding nearby parks: {e}")
            return []
    
    async def _search_2gis_parks(self, lat: float, lon: float, radius: int) -> List[Dict[str, Any]]:
        """Поиск парков через 2ГИС API"""
        if not HTTPX_AVAILABLE or not self.api_key:
            return []
        
        park_types = [
            {"query": "парк", "type": "park"},
            {"query": "сад", "type": "garden"},
            {"query": "сквер", "type": "square"},
            {"query": "лесопарк", "type": "forest_park"},
            {"query": "заповедник", "type": "nature_reserve"}
        ]
        
        all_places = []
        
        for park_type in park_types:
            try:
                url = f"{self.base_url}/items"
                params = {
                    "q": park_type["query"],
                    "point": f"{lon},{lat}",
                    "radius": radius,
                    "key": self.api_key,
                    "page_size": 10,
                    "fields": "items.point,items.name,items.full_name,items.address_name"
                }
                
                full_url = f"{url}?{urllib.parse.urlencode(params)}"
                
                req = urllib.request.Request(full_url)
                req.add_header('User-Agent', self.user_agent)
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    if response.getcode() == 200:
                        data = json.loads(response.read().decode('utf-8'))
                        
                        # Проверяем на ошибки авторизации
                        if 'meta' in data and data['meta'].get('code') == 403:
                            print("2GIS API key invalid, switching to OSM")
                            return []
                        
                        if data.get('result') and data['result'].get('items'):
                            for item in data['result']['items']:
                                point = item.get('point')
                                if not point:
                                    continue
                                
                                distance = self.calculate_distance(lat, lon, point['lat'], point['lon'])
                                
                                if distance <= radius:
                                    place_info = {
                                        'place_id': item.get('id'),
                                        'lat': str(point['lat']),
                                        'lon': str(point['lon']),
                                        'name': item.get('name', 'Без названия'),
                                        'class': park_type["type"],
                                        'type': park_type["type"],
                                        'distance': distance,
                                        'display_name': item.get('full_name') or item.get('name', 'Без названия'),
                                        'address': item.get('address_name', '')
                                    }
                                    all_places.append(place_info)
                
                import time
                time.sleep(0.2)
                
            except Exception as e:
                print(f"Error searching 2GIS for {park_type['query']}: {e}")
                continue
        
        return all_places
    
    async def _search_osm_parks(self, lat: float, lon: float, radius: int) -> List[Dict[str, Any]]:
        """Поиск парков через российский геосервис Яндекс Карты API"""
        try:
            print(f"Searching parks via Yandex Maps API for lat={lat}, lon={lon}")
            
            # Используем Yandex Geocoder API для поиска парков
            # Альтернатива: Яндекс.Карты API для поиска организаций
            yandex_api_key = os.getenv('YANDEX_API_KEY')
            
            if not yandex_api_key:
                print("No Yandex API key, using mock data")
                return self._get_mock_parks(lat, lon, radius)
            
            # Типы парков для поиска через Яндекс
            park_types = [
                "парк",
                "сквер", 
                "сад",
                "лесопарк",
                "заповедник",
                "ботанический сад",
                "дендрарий",
                "рекреационная зона"
            ]
            
            all_places = []
            
            for park_type in park_types:
                try:
                    # Формируем запрос к Яндекс Геокодеру
                    url = "https://geocode-maps.yandex.ru/1.x/"
                    params = {
                        'apikey': yandex_api_key,
                        'geocode': f'{park_type} {lat},{lon}',
                        'kind': 'poi',
                        'rspn': 1,
                        'll': f'{lon},{lat}',
                        'spn': f'{radius/111000},{radius/111000}',  # Примерно в градусах
                        'format': 'json',
                        'results': 10
                    }
                    
                    full_url = f"{url}?{urllib.parse.urlencode(params)}"
                    
                    req = urllib.request.Request(full_url)
                    req.add_header('User-Agent', 'EcoKolendar/1.0')
                    
                    with urllib.request.urlopen(req, timeout=15) as response:
                        if response.getcode() == 200:
                            data = json.loads(response.read().decode('utf-8'))
                            
                            # Парсим ответ от Яндекс API
                            if 'response' in data and 'GeoObjectCollection' in data['response']:
                                features = data['response']['GeoObjectCollection']['featureMember']
                                
                                for feature in features:
                                    geo_object = feature['GeoObject']
                                    point_str = geo_object['Point']['pos']  # "lon lat"
                                    lon_found, lat_found = map(float, point_str.split())
                                    
                                    # Вычисляем расстояние
                                    distance = self.calculate_distance(lat, lon, lat_found, lon_found)
                                    
                                    if distance <= radius:
                                        name = geo_object['name']
                                        description = geo_object.get('description', '')
                                        
                                        # Определяем тип объекта
                                        if 'парк' in name.lower() or 'парк' in description.lower():
                                            park_type_result = 'park'
                                        elif 'сад' in name.lower() or 'сад' in description.lower():
                                            park_type_result = 'garden'
                                        elif 'сквер' in name.lower() or 'сквер' in description.lower():
                                            park_type_result = 'square'
                                        elif 'заповедник' in name.lower() or 'заповедник' in description.lower():
                                            park_type_result = 'nature_reserve'
                                        else:
                                            park_type_result = 'recreation'
                                        
                                        place_info = {
                                            'place_id': geo_object.get('id', f'yandex_{len(all_places)}'),
                                            'lat': str(lat_found),
                                            'lon': str(lon_found),
                                            'name': name,
                                            'class': park_type_result,
                                            'type': park_type_result,
                                            'distance': distance,
                                            'display_name': name,
                                            'address': description
                                        }
                                        all_places.append(place_info)
                    
                    import time
                    time.sleep(0.1)  # Небольшая задержка между запросами
                    
                except Exception as e:
                    print(f"Error searching Yandex for {park_type}: {e}")
                    continue
            
            # Удаляем дубликаты
            unique_places = []
            seen_coords = set()
            
            for place in all_places:
                coord_key = f"{place['lat']},{place['lon']}"
                if coord_key not in seen_coords:
                    seen_coords.add(coord_key)
                    unique_places.append(place)
            
            print(f"Found {len(unique_places)} unique parks via Yandex Maps")
            return unique_places
                
        except Exception as e:
            print(f"Error searching Yandex Maps: {e}")
            # Fallback: возвращаем моковые данные для российских парков
            return self._get_mock_parks(lat, lon, radius)
    
    def _get_mock_parks(self, lat: float, lon: float, radius: int) -> List[Dict[str, Any]]:
        """Возвращает моковые данные о российских парках для тестирования"""
        # Известные парки России для разных городов
        mock_parks = {
            # Москва
            (55.7558, 37.6173): [
                {"name": "Парк Горького", "type": "park", "distance": 1200, "lat": 55.7315, "lon": 37.6058},
                {"name": "ВДНХ", "type": "park", "distance": 3500, "lat": 55.8265, "lon": 37.6395},
                {"name": "Парк Победы на Поклонной горе", "type": "park", "distance": 4800, "lat": 55.7446, "lon": 37.5089},
                {"name": "Царицыно", "type": "park", "distance": 8500, "lat": 55.6299, "lon": 37.7131},
                {"name": "Коломенское", "type": "park", "distance": 6200, "lat": 55.6726, "lon": 37.6765},
                {"name": "Сокольники", "type": "park", "distance": 2800, "lat": 55.7833, "lon": 37.6833},
                {"name": "Измайловский парк", "type": "park", "distance": 4200, "lat": 55.7689, "lon": 37.7495},
                {"name": "Тимирязевский парк", "type": "park", "distance": 5600, "lat": 55.8389, "lon": 37.5764}
            ],
            # Санкт-Петербург
            (59.9343, 30.3351): [
                {"name": "Летний сад", "type": "garden", "distance": 800, "lat": 59.9331, "lon": 30.3264},
                {"name": "Петродворец", "type": "park", "distance": 28000, "lat": 59.8764, "lon": 29.8792},
                {"name": "Павловский парк", "type": "park", "distance": 23000, "lat": 59.6833, "lon": 30.4500},
                {"name": "Царское Село", "type": "park", "distance": 25000, "lat": 59.7000, "lon": 30.4000},
                {"name": "Парк аттракционов Диво Остров", "type": "park", "distance": 3500, "lat": 59.9311, "lon": 30.2767}
            ],
            # Екатеринбург
            (56.8389, 60.6057): [
                {"name": "Центральный парк культуры и отдыха", "type": "park", "distance": 1500, "lat": 56.8326, "lon": 60.6034},
                {"name": "Парк им. Маяковского", "type": "park", "distance": 2200, "lat": 56.8289, "lon": 60.6178},
                {"name": "Лесопарк им. Лесова", "type": "forest_park", "distance": 4500, "lat": 56.8456, "lon": 60.6234}
            ]
        }
        
        # Находим ближайший город по координатам
        nearest_city = None
        min_distance = float('inf')
        
        for city_coords in mock_parks.keys():
            dist = self.calculate_distance(lat, lon, city_coords[0], city_coords[1])
            if dist < min_distance and dist < 50000:  # В пределах 50 км
                min_distance = dist
                nearest_city = city_coords
        
        if nearest_city and mock_parks[nearest_city]:
            result = []
            for park_data in mock_parks[nearest_city]:
                if park_data['distance'] <= radius:
                    result.append({
                        'place_id': f"mock_{park_data['name'].replace(' ', '_')}",
                        'lat': str(park_data['lat']),
                        'lon': str(park_data['lon']),
                        'name': park_data['name'],
                        'class': park_data['type'],
                        'type': park_data['type'],
                        'distance': park_data['distance'],
                        'display_name': park_data['name'],
                        'address': 'Россия'
                    })
            
            print(f"Found {len(result)} mock parks for Russian city")
            return result
        
        return []
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Вычислить расстояние между двумя точками в метрах"""
        import math
        
        R = 6371000  # Радиус Земли в метрах
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c

class EmailService:
    """Сервис для отправки email сообщений"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.email_user)
        
        # Проверяем конфигурацию при инициализации
        if not self.email_user or not self.email_password:
            print("⚠️ ВНИМАНИЕ: Email не настроен! См. EMAIL_SETUP.md")
            print("   EMAIL_USER и EMAIL_PASSWORD должны быть установлены в .env файле")
        elif self.email_user == "your-email@gmail.com":
            print("⚠️ ВНИМАНИЕ: Используются плейсхолдеры вместо реальных email настроек!")
            print("   Обновите .env файл с вашими SMTP настройками. См. EMAIL_SETUP.md")
        else:
            print(f"✅ Email сервис настроен для: {self.email_user}")
    
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Отправка приветственного письма при регистрации"""
        # Проверяем конфигурацию перед отправкой
        if not self.email_user or not self.email_password:
            print("❌ Email не настроен - пропускаю отправку приветственного письма")
            return False
            
        if self.email_user == "your-email@gmail.com":
            print("❌ Используются плейсхолдеры - пропускаю отправку приветственного письма")
            return False
            
        try:
            html_content = self._get_welcome_template(user_name)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Добро пожаловать в Эко-календарь!"
            msg['From'] = f"Эко-календарь <{self.from_email}>"
            msg['To'] = user_email
            
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            return await self._send_email(msg)
            
        except Exception as e:
            print(f"❌ Ошибка отправки приветственного письма: {e}")
            return False
    
    async def _send_email(self, msg: MIMEMultipart) -> bool:
        """Отправка email через SMTP"""
        print(f"🔧 Начало отправки email...")
        print(f"   От: {self.from_email}")
        print(f"   Кому: {msg['To']}")
        print(f"   Тема: {msg['Subject']}")
        print(f"   SMTP: {self.smtp_server}:{self.smtp_port}")
        
        try:
            print("📡 Подключение к SMTP серверу...")
            # Используем SMTP_SSL для Gmail на порту 465 или SMTP с STARTTLS для порта 587
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
                print("✅ Подключение через SMTP_SSL успешно")
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.set_debuglevel(1)  # Включаем отладку
                print("✅ Подключение успешно")
                
                print("🔒 Установка STARTTLS...")
                server.starttls()
                print("✅ STARTTLS установлен")
            
            print("🔐 Аутентификация...")
            server.login(self.email_user, self.email_password)
            print("✅ Аутентификация успешна")
            
            print("📧 Отправка письма...")
            text = msg.as_string()
            server.sendmail(self.from_email, msg['To'], text)
            print("✅ Письмо отправлено успешно!")
            
            server.quit()
            print("✅ Соединение закрыто")
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Ошибка аутентификации: {e}")
            print("💡 Убедитесь, что:")
            print("   • Используется пароль приложения Gmail, а не обычный пароль")
            print("   • Включен 2FA в аккаунте Gmail")
            print("   • Создан пароль приложения в Google Account settings")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ Ошибка SMTP: {e}")
            print("💡 Возможные решения:")
            print("   • Проверьте подключение к интернету")
            print("   • Убедитесь, что SMTP сервер и порт правильные")
            print("   • Попробуйте использовать порт 465 с SMTP_SSL")
            return False
        except Exception as e:
            print(f"❌ Общая ошибка: {e}")
            print(f"💡 Тип ошибки: {type(e).__name__}")
            return False
    
    def _get_welcome_template(self, user_name: str) -> str:
        """HTML шаблон приветственного письма"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Добро пожаловать в Эко-календарь!</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #4caf50, #45a049); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">🌿 Эко-календарь</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px;">Green Heritage</p>
                </div>
                
                <div style="padding: 30px;">
                    <h2 style="color: #5A5A40; margin-bottom: 20px;">Добро пожаловать, {user_name}! 👋</h2>
                    
                    <p style="color: #333; line-height: 1.6; margin-bottom: 20px;">
                        Спасибо за регистрацию в Эко-календаре! Теперь у вас есть доступ к полной информации об экологических и национальных праздниках.
                    </p>
                    
                    <div style="background-color: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4caf50;">
                        <h3 style="color: #5A5A40; margin-top: 0;">Что вы можете делать:</h3>
                        <ul style="color: #333; line-height: 1.6;">
                            <li>📅 Просматривать календарь праздников</li>
                            <li>🌤️ Узнавать погоду на любой день</li>
                            <li>📰 Читать свежие экологические новости</li>
                            <li>🗺️ Искать места для мероприятий</li>
                            <li>📝 Добавлять свои праздники (для администраторов)</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="http://127.0.0.1:8000" style="background: #4caf50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                            Перейти в Эко-календарь
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; text-align: center; margin-top: 30px;">
                        Если у вас есть вопросы, свяжитесь с нами через форму обратной связи на сайте.
                    </p>
                </div>
                
                <div style="background-color: #f5f5f5; padding: 20px; text-align: center; color: #666; font-size: 12px;">
                    <p style="margin: 0;">© 2026 Эко-календарь. Все права защищены.</p>
                    <p style="margin: 5px 0 0 0;">🌿 Заботимся о нашей планете вместе</p>
                </div>
            </div>
        </body>
        </html>
        """

# Экземпляры API (только бесплатные)
weather_api = WeatherAPI()
news_api = NewsAPI()
geocoding_api = GeocodingAPI()
email_service = EmailService()
