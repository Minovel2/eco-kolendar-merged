from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import User, Favorite, Holiday
from app.external_apis import email_service
import json
import asyncio

def send_holiday_notifications(db: Session):  # Принимаем db как параметр
    """Проверяет избранные праздники и отправляет уведомления"""
    today = datetime.now().date()
    
    print(f"🔍 Начало проверки уведомлений. Дата: {today}")
    
    try:
        # Получаем все избранные праздники
        favorites = db.query(Favorite).all()
        print(f"📊 Найдено избранных записей: {len(favorites)}")
        
        if not favorites:
            print("❌ Нет избранных праздников")
            return 0
        
        notifications_sent = 0
        
        for fav in favorites:
            user = db.query(User).filter(User.id == fav.user_id).first()
            holiday = db.query(Holiday).filter(Holiday.id == fav.holiday_id).first()
            
            if not user:
                print(f"⚠️ Пользователь не найден для fav.id={fav.id}")
                continue
            if not holiday:
                print(f"⚠️ Праздник не найден для fav.id={fav.id}")
                continue
            
            print(f"\n📌 Проверка: {user.email} -> {holiday.name}")
            print(f"   День: {holiday.day}, Месяц: {holiday.month}")
            
            # Текущий год
            current_year = today.year
            
            # Создаём дату праздника в текущем году
            # ВНИМАНИЕ: month в БД 0-11, а datetime month 1-12
            holiday_date = datetime(current_year, holiday.month + 1, holiday.day).date()
            
            days_until = (holiday_date - today).days
            
            print(f"   Сегодня: {today}")
            print(f"   Праздник: {holiday_date}")
            print(f"   Дней до/после: {days_until}")
            
            if days_until == 0:
                print(f"✅ СЕГОДНЯ праздник! Отправка уведомления...")
                subject = f"🌿 Сегодня праздник: {holiday.name}!"
                success = send_notification(user, holiday, subject, "сегодня")
                if success:
                    notifications_sent += 1
                    print(f"   ✅ Уведомление отправлено")
                else:
                    print(f"   ❌ Ошибка отправки")
                    
            elif days_until == 1:
                print(f"✅ ЗАВТРА праздник! Отправка уведомления...")
                subject = f"⭐ Завтра праздник: {holiday.name}!"
                success = send_notification(user, holiday, subject, "завтра")
                if success:
                    notifications_sent += 1
                    print(f"   ✅ Уведомление отправлено")
                else:
                    print(f"   ❌ Ошибка отправки")
            else:
                print(f"   ⏭️ Не подходит (дней: {days_until})")
        
        print(f"\n📊 ИТОГО отправлено уведомлений: {notifications_sent}")
        return notifications_sent
        
    except Exception as e:
        print(f"❌ Ошибка рассылки: {e}")
        import traceback
        traceback.print_exc()
        return 0

def send_notification(user, holiday, subject, when):
    """Отправляет одно уведомление пользователю"""
    print(f"   📧 Подготовка письма для {user.email}")
    
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
            <div style="background: linear-gradient(135deg, #4caf50, #2e7d32); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">🌿 Эко-календарь</h1>
            </div>
            <div style="padding: 30px;">
                <h2 style="color: #5A5A40; margin-bottom: 15px;">Здравствуйте, {user_name}!</h2>
                <p style="color: #333; font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
                    Напоминаем, что <strong>{when}</strong> отмечается праздник:
                </p>
                <div style="background: #f5f5f0; padding: 20px; border-radius: 15px; border-left: 5px solid #4caf50; margin-bottom: 20px;">
                    <h2 style="color: #5A5A40; margin: 0 0 10px 0; font-size: 22px;">{holiday.name}</h2>
                    <p style="color: #666; margin: 0 0 10px 0; font-size: 14px;">
                        📅 {holiday.day}.{holiday.month + 1}
                    </p>
                    <p style="color: #666; margin: 0; font-size: 14px; line-height: 1.6;">
                        {holiday.description[:300]}{'...' if len(holiday.description) > 300 else ''}
                    </p>
                </div>
                <div style="text-align: center; margin-top: 30px;">
                    <a href="http://127.0.0.1:8000" 
                       style="background: linear-gradient(135deg, #4caf50, #2e7d32); color: white; padding: 15px 35px; text-decoration: none; border-radius: 12px; font-weight: bold; display: inline-block; font-size: 16px;">
                        🌍 Перейти в Эко-календарь
                    </a>
                </div>
            </div>
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
        # Создаём MIME сообщение
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"Эко-календарь <{email_service.from_email}>"
        msg['To'] = user.email
        
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Отправляем синхронно (не асинхронно для простоты)
        import smtplib
        if email_service.smtp_port == 465:
            server = smtplib.SMTP_SSL(email_service.smtp_server, email_service.smtp_port, timeout=30)
        else:
            server = smtplib.SMTP(email_service.smtp_server, email_service.smtp_port, timeout=30)
            server.starttls()
        
        server.login(email_service.email_user, email_service.email_password)
        server.send_message(msg)
        server.quit()
        
        print(f"   ✅ Письмо успешно отправлено на {user.email}")
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка отправки письма на {user.email}: {e}")
        import traceback
        traceback.print_exc()
        return False