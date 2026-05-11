# import httpx  # Disabled for Python 3.14 compatibility
import json
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
from . import models, schemas, crud
from .database import engine, get_db
from .seed import seed_database
from .models import User, WorkDay
from .schemas import UserRegister, UserLogin, UserResponse, HolidayUpdate
from .external_apis import WeatherAPI, weather_api, news_api, geocoding_api, email_service
import secrets
import string
from datetime import datetime
from .notifications import send_holiday_notifications
from prometheus_fastapi_instrumentator import Instrumentator

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Эко-календарь API",
    description="API для экологического и национального календаря праздников",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

Instrumentator().instrument(app).expose(app)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    seed_database()
    models.Base.metadata.create_all(bind=engine)  # Создаёт все таблицы
    seed_database()

@app.get("/")
async def root():
    return {"message": "Эко-календарь API работает!"}

@app.get("/api/import/holidays")
async def import_holidays(db: Session = Depends(get_db)):
    """Импорт праздников из 3 внешних API"""
    from .holiday_importers import HolidayImporter
    
    print("📥 Запуск импорта праздников из внешних API...")
    
    importer = HolidayImporter(db)
    results = importer.import_all()
    
    return {
        "message": f"Импорт завершён. Всего добавлено: {results.get('total', 0)} праздников",
        "total_imported": results.get("total", 0),
        "sources": results
    }

@app.get("/api/holidays", response_model=List[schemas.HolidayResponse])
async def get_holidays(
    type: Optional[str] = None,
    region: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получить список всех праздников с возможностью фильтрации"""
    holidays = crud.filter_holidays(db, type=type, region=region, search=search)
    return holidays

@app.get("/api/work-days")
async def get_work_days(
    year: int = Query(...),
    month: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Получить список рабочих/выходных дней"""
    query = db.query(WorkDay).filter(WorkDay.year == year)
    if month is not None:
        query = query.filter(WorkDay.month == month)
    return query.all()

# Внешние API эндпоинты
@app.get("/api/external/weather")
async def get_weather_for_holiday(
    lat: float = Query(..., description="Широта"),
    lon: float = Query(..., description="Долгота"),
    days: int = Query(5, description="Количество дней прогноза"),
    date: str = Query(None, description="Конкретная дата в формате YYYY-MM-DD")
):
    """Получить прогноз погоды для праздника"""
    if date:
        weather_data = await weather_api.get_weather_for_date(lat, lon, date)
    else:
        weather_data = await weather_api.get_weather_forecast(lat, lon, days)
    
    if not weather_data:
        raise HTTPException(status_code=404, detail="Не удалось получить данные о погоде")
    
    # Добавляем информацию о местоположении
    location_name = await get_location_name(lat, lon)
    if location_name:
        weather_data["location_name"] = location_name
    
    return weather_data

async def get_location_name(lat: float, lon: float) -> str:
    """Получить название местоположения по координатам"""
    try:
        # Используем Nominatim (OpenStreetMap) для обратного геокодирования
        import urllib.request, json
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=ru"
        req = urllib.request.Request(url, headers={'User-Agent': 'EcoKolendar/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            address = data.get('address', {})
            # Пробуем получить город, деревню, посёлок или район
            location = (
                address.get('city') or 
                address.get('town') or 
                address.get('village') or 
                address.get('municipality') or
                address.get('county') or
                address.get('state') or
                data.get('display_name', '').split(',')[0]
            )
            if location:
                # Добавляем страну для контекста
                country = address.get('country', '')
                if country and country != location:
                    return f"{location}, {country}"
                return location
    except Exception as e:
        print(f"Ошибка получения названия местоположения: {e}")
    return None

@app.get("/api/external/news/{holiday_id}")
async def get_news_for_holiday(
    holiday_id: int,
    db: Session = Depends(get_db)
):
    """Получить новости, связанные с праздником"""
    holiday = db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Праздник не найден")
    
    # Ищем новости по названию праздника
    news_data = await news_api.search_holiday_news(holiday.name)
    
    if not news_data:
        # Если новостей по празднику нет, ищем общие экологические новости
        news_data = await news_api.get_eco_news()
    
    if not news_data:
        return {"articles": [], "message": "Новости не найдены"}
    
    return {
        "holiday": holiday.name,
        "articles": news_data.get("articles", [])[:5],  # Ограничиваем количество статей
        "source": "NewsAPI"
    }

@app.get("/api/external/locations/search")
async def search_locations(
    query: str = Query(..., description="Поисковый запрос"),
    limit: int = Query(5, description="Количество результатов")
):
    """Поиск местоположений для проведения мероприятий"""
    locations_data = await geocoding_api.search_location(query, limit)
    
    if not locations_data:
        return {"locations": [], "message": "Местоположения не найдены"}
    
    return {
        "query": query,
        "locations": locations_data,
        "source": "2ГИС"
    }

@app.get("/api/external/locations/nearby")
async def get_nearby_locations(
    lat: float = Query(..., description="Широта"),
    lon: float = Query(..., description="Долгота"),
    radius: int = Query(10000, description="Радиус поиска в метрах")
):
    """Найти ближайшие парки и заповедники"""
    locations_data = await geocoding_api.find_nearby_parks(lat, lon, radius)
    
    if not locations_data:
        return {"locations": [], "message": "Места не найдены"}
    
    return {
        "center": {"lat": lat, "lon": lon},
        "radius": radius,
        "locations": locations_data,
        "source": "2ГИС"
    }



@app.get("/api/external/eco-news")
async def get_ecological_news():
    """Получить последние экологические новости"""
    news_data = await news_api.get_eco_news()
    
    if not news_data:
        return {"articles": [], "message": "Новости не найдены"}
    
    return {
        "articles": news_data.get("articles", [])[:5],
        "source": "NewsAPI"
    }

@app.get("/api/holidays/{holiday_id}", response_model=schemas.HolidayResponse)
async def get_holiday(
    holiday_id: int,
    db: Session = Depends(get_db)
):
    """Получить праздник по ID"""
    holiday = crud.get_holiday(db, holiday_id=holiday_id)
    if holiday is None:
        raise HTTPException(status_code=404, detail="Праздник не найден")
    try:
        events = json.loads(holiday.events) if holiday.events else []
    except:
        events = []
    return {
        "id": holiday.id,
        "name": holiday.name,
        "day": holiday.day,
        "month": holiday.month,
        "type": holiday.type,
        "region": holiday.region,
        "description": holiday.description,
        "events": events,
        "wikipedia_url": holiday.wikipedia_url or ""
    }

@app.delete("/api/holidays/{holiday_id}")
async def delete_holiday(
    holiday_id: int,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """Удалить праздник"""
    # Временно без проверки админа
    success = crud.delete_holiday(db, holiday_id)
    if not success:
        raise HTTPException(status_code=404, detail="Праздник не найден")
    return {"message": "Праздник удалён"}

@app.post("/api/holidays", response_model=schemas.HolidayResponse)
async def create_holiday(
    holiday: schemas.HolidayCreate,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """Добавить новый праздник"""
    # Временно без проверки админа (добавим позже)
    db_holiday = crud.create_holiday(db=db, holiday=holiday)
    try:
        events = json.loads(db_holiday.events) if db_holiday.events else []
    except:
        events = []
    return {
        "id": db_holiday.id,
        "name": db_holiday.name,
        "day": db_holiday.day,
        "month": db_holiday.month,
        "type": db_holiday.type,
        "region": db_holiday.region,
        "description": db_holiday.description,
        "events": events,
        "wikipedia_url": db_holiday.wikipedia_url or ""
    }

@app.post("/api/register", response_model=UserResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Регистрация пользователя с отправкой приветственного письма"""
    user = crud.create_user(db, user_data)
    if not user:
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    
    # Отправляем приветственное письмо
    try:
        user_name = f"{user.first_name} {user.last_name}"
        email_sent = await email_service.send_welcome_email(user.email, user_name)
        if email_sent:
            print(f"Приветственное письмо отправлено на {user.email}")
        else:
            print(f"Ошибка отправки письма на {user.email}")
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")
    
    return user

@app.post("/api/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Вход в систему"""
    user = crud.login_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "name": f"{user.last_name} {user.first_name}"
    }

@app.put("/api/holidays/{holiday_id}")
async def update_holiday(
    holiday_id: int,
    holiday_data: HolidayUpdate,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """Обновить праздник"""
    # Временно без проверки админа
    updated = crud.update_holiday(db, holiday_id, holiday_data.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Праздник не найден")
    return {"message": "Праздник обновлён"}

# Управление пользователями
@app.get("/api/admin/users")
async def get_all_users(db: Session = Depends(get_db)):
    """Получить список всех пользователей (только для админа)"""
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "patronymic": user.patronymic,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        for user in users
    ]

@app.put("/api/admin/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role_data: dict,
    db: Session = Depends(get_db)
):
    """Обновить роль пользователя (только для админа)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    new_role = role_data.get("role")
    if new_role not in [0, 1]:
        raise HTTPException(status_code=400, detail="Неверная роль. Допустимые значения: 0 (пользователь), 1 (администратор)")
    
    user.role = new_role
    db.commit()
    
    return {"message": f"Роль пользователя {user.email} обновлена на {'администратор' if new_role == 1 else 'пользователь'}"}

@app.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Удалить пользователя (только для админа)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    db.delete(user)
    db.commit()
    
    return {"message": f"Пользователь {user.email} удалён"}

@app.post("/api/admin/users/import")
async def import_users(users_data: dict, db: Session = Depends(get_db)):
    """Импорт пользователей из JSON с генерацией случайных паролей"""
    users = users_data.get("users", [])
    imported = 0
    skipped = 0
    errors = 0
    new_users_passwords = []  # Для вывода админу
    
    for user_data in users:
        if not user_data.get("email") or not user_data.get("last_name") or not user_data.get("first_name"):
            errors += 1
            continue
        
        # Проверяем дубликат по email
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if existing:
            skipped += 1
            continue
        
        try:
            # Генерируем случайный пароль
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for _ in range(12))
            hashed = crud.hash_password(password)
            
            user = User(
                last_name=user_data["last_name"],
                first_name=user_data["first_name"],
                patronymic=user_data.get("patronymic"),
                email=user_data["email"],
                password=hashed,
                role=user_data.get("role", 0),
                created_at=datetime.now()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Отправляем пароль на почту
            user_name = f"{user.first_name} {user.last_name}"
            try:
                await email_service.send_welcome_email(
                    user_email=user.email, 
                    user_name=user_name,
                    custom_message=f"Ваш временный пароль: {password}\n\nРекомендуем сменить его при первом входе."
                )
            except Exception as e:
                print(f"Ошибка отправки письма: {e}")
            
            new_users_passwords.append({"email": user.email, "password": password})
            imported += 1
            
        except Exception as e:
            print(f"Ошибка импорта пользователя {user_data.get('email')}: {e}")
            errors += 1
    
    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors,
        "passwords": new_users_passwords,
        "message": f"Импортировано: {imported}, пропущено: {skipped}, ошибок: {errors}"
    }
    
@app.get("/api/favorites")
async def get_favorites(user_id: int = Query(...), db: Session = Depends(get_db)):
    """Получить избранные праздники пользователя"""
    favorites = db.query(models.Favorite).filter(models.Favorite.user_id == user_id).all()
    return [{"holiday_id": f.holiday_id} for f in favorites]

@app.post("/api/favorites/{holiday_id}")
async def add_favorite(holiday_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Добавить праздник в избранное"""
    existing = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.holiday_id == holiday_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Уже в избранном")
    
    favorite = models.Favorite(user_id=user_id, holiday_id=holiday_id)
    db.add(favorite)
    db.commit()
    return {"message": "Добавлено в избранное"}

@app.delete("/api/favorites/{holiday_id}")
async def remove_favorite(holiday_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    """Удалить праздник из избранного"""
    favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.holiday_id == holiday_id
    ).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Не найдено в избранном")
    
    db.delete(favorite)
    db.commit()
    return {"message": "Удалено из избранного"}

@app.post("/api/admin/send-notifications")
async def trigger_notifications():
    """Запустить рассылку уведомлений о праздниках (для теста)"""
    from .notifications import send_holiday_notifications
    sent = send_holiday_notifications()
    return {"message": f"Рассылка завершена", "sent": sent}

@app.post("/api/admin/reset-database")
async def reset_database_endpoint():
    """Сбросить БД к исходному состоянию (только для админа)"""
    from .reset_db import reset_database
    success = reset_database()
    return {"message": "База данных восстановлена" if success else "Ошибка восстановления"}