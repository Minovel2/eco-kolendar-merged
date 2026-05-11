from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Favorite, Holiday
from app.external_apis import email_service
import json

def send_holiday_notifications():
    """Проверяет избранные праздники и отправляет уведомления"""
    db = SessionLocal()
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    try:
        # Получаем все избранные праздники
        favorites = db.query(Favorite).all()
        
        notifications_sent = 0
        
        for fav in favorites:
            user = db.query(User).filter(User.id == fav.user_id).first()
            holiday = db.query(Holiday).filter(Holiday.id == fav.holiday_id).first()
            
            if not user or not holiday:
                continue
            
            # Текущий год
            current_year = today.year
            
            # Создаём дату праздника в текущем году
            holiday_date = datetime(current_year, holiday.month + 1, holiday.day).date()
            
            # Проверяем: сегодня праздник или завтра?
            days_until = (holiday_date - today).days
            
            if days_until == 0:
                # Отправляем уведомление в день праздника
                subject = f"🌿 Сегодня праздник: {holiday.name}!"
                send_notification(user, holiday, subject, "сегодня")
                notifications_sent += 1
                
            elif days_until == 1:
                # Отправляем уведомление за день до праздника
                subject = f"⭐ Завтра праздник: {holiday.name}!"
                send_notification(user, holiday, subject, "завтра")
                notifications_sent += 1
        
        print(f"✅ Отправлено уведомлений: {notifications_sent}")
        return notifications_sent
        
    except Exception as e:
        print(f"❌ Ошибка рассылки: {e}")
        return 0
    finally:
        db.close()

def send_notification(user, holiday, subject, when):
    """Отправляет одно уведомление пользователю"""
    user_name = f"{user.first_name} {user.last_name}"
    
    events = []
    try:
        events = json.loads(holiday.events) if holiday.events else []
    except:
        pass
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f0;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            
            <!-- Шапка -->
            <div style="background: linear-gradient(135deg, #4caf50, #2e7d32); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">🌿 Эко-календарь</h1>
            </div>
            
            <!-- Содержание -->
            <div style="padding: 30px;">
                <h2 style="color: #5A5A40; margin-bottom: 15px;">Здравствуйте, {user_name}!</h2>
                
                <p style="color: #333; font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
                    Напоминаем, что <strong>{when}</strong> отмечается праздник:
                </p>
                
                <div style="background: #f5f5f0; padding: 20px; border-radius: 15px; border-left: 5px solid #4caf50; margin-bottom: 20px;">
                    <h2 style="color: #5A5A40; margin: 0 0 10px 0; font-size: 22px;">{holiday.name}</h2>
                    <p style="color: #666; margin: 0 0 10px 0; font-size: 14px;">
                        📅 {holiday.day} {get_month_name(holiday.month)}
                    </p>
                    <p style="color: #666; margin: 0; font-size: 14px; line-height: 1.6;">
                        {holiday.description[:300]}{'...' if len(holiday.description) > 300 else ''}
                    </p>
                </div>
                
                {f'''
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #5A5A40; font-size: 16px;">📋 Запланированные мероприятия:</h3>
                    <ul style="list-style: none; padding: 0;">
                        {''.join(f'<li style="padding: 10px; background: #f5f5f0; border-radius: 10px; margin-bottom: 8px;">✅ {e}</li>' for e in events)}
                    </ul>
                </div>
                ''' if events else ''}
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="http://127.0.0.1:8000" 
                       style="background: linear-gradient(135deg, #4caf50, #2e7d32); color: white; padding: 15px 35px; text-decoration: none; border-radius: 12px; font-weight: bold; display: inline-block; font-size: 16px;">
                        🌍 Перейти в Эко-календарь
                    </a>
                </div>
            </div>
            
            <!-- Подвал -->
            <div style="background: #f5f5f0; padding: 20px; text-align: center; border-top: 1px solid #e0e0d0;">
                <p style="margin: 0; color: #999; font-size: 12px;">
                    Вы получили это письмо, потому что добавили праздник в избранное.<br>
                    © 2026 Эко-календарь. Все права защищены.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        # Используем существующий email_service
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Создаём MIME сообщение
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"Эко-календарь <{email_service.from_email}>"
        msg['To'] = user.email
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Отправляем
        success = loop.run_until_complete(email_service._send_email(msg))
        loop.close()
        
        return success
    except Exception as e:
        print(f"Ошибка отправки уведомления для {user.email}: {e}")
        return False

def get_month_name(month_index):
    """Возвращает название месяца по индексу (0-11)"""
    months = [
        'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
        'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
    ]
    return months[month_index] if 0 <= month_index <= 11 else ''

# Для ручного запуска из командной строки
if __name__ == "__main__":
    print("📧 Запуск рассылки уведомлений о праздниках...")
    sent = send_holiday_notifications()
    print(f"Готово! Отправлено уведомлений: {sent}")