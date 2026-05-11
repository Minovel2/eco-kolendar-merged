from app.database import SessionLocal, engine
from app.models import Base, Holiday, WorkDay
from app.seed import seed_database

def reset_database():
    """Сбрасывает БД к исходному состоянию"""
    print("🔄 Сброс базы данных...")
    
    db = SessionLocal()
    try:
        # Удаляем все импортированные праздники
        deleted_holidays = db.query(Holiday).delete()
        deleted_workdays = db.query(WorkDay).delete()
        db.commit()
        
        print(f"✅ Удалено праздников: {deleted_holidays}")
        print(f"✅ Удалено рабочих дней: {deleted_workdays}")
        
        # Заново наполняем БД исходными данными
        print("🌱 Наполнение базы исходными данными...")
        seed_database()
        
        print("✅ База данных восстановлена!")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка сброса БД: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()