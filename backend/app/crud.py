from sqlalchemy.orm import Session
from app import models, schemas
import hashlib
from app.models import User
import json

def get_holidays(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Holiday).offset(skip).limit(limit).all()

def get_holiday(db: Session, holiday_id: int):
    return db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()

def create_holiday(db: Session, holiday: schemas.HolidayCreate):
    db_holiday = models.Holiday(
        **holiday.model_dump(exclude={'events'}),
        events=json.dumps(holiday.events if holiday.events else [])
    )
    db.add(db_holiday)
    db.commit()
    db.refresh(db_holiday)
    return db_holiday

def filter_holidays(
    db: Session, 
    type: str = None, 
    region: str = None, 
    search: str = None
):
    query = db.query(models.Holiday)
    
    if type and type != "all":
        query = query.filter(models.Holiday.type == type)
    if region and region != "all":
        query = query.filter(models.Holiday.region == region)
    if search:
        query = query.filter(
            models.Holiday.name.ilike(f"%{search}%") | 
            models.Holiday.description.ilike(f"%{search}%")
        )
    
    return query.all()

def delete_holiday(db: Session, holiday_id: int):
    holiday = db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()
    if holiday:
        db.delete(holiday)
        db.commit()
        return True
    return False

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(db: Session, user_data):
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        return None
    user = User(
        last_name=user_data.last_name,
        first_name=user_data.first_name,
        patronymic=user_data.patronymic,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=0
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def login_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if user and user.password == hash_password(password):
        return user
    return None

def is_admin(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    return user and user.role == 1

def update_holiday(db: Session, holiday_id: int, data: dict):
    holiday = db.query(models.Holiday).filter(models.Holiday.id == holiday_id).first()
    if not holiday:
        return None
    for key, value in data.items():
        if value is not None:
            if key == 'events':
                setattr(holiday, key, json.dumps(value))
            else:
                setattr(holiday, key, value)
    db.commit()
    db.refresh(holiday)
    return holiday