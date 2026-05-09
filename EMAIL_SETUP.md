# 📧 Руководство по настройке email для Эко-Календаря

## 📋 Обзор

Эко-Календарь может отправлять email уведомления пользователям. Для этого требуется настройка SMTP сервера.

---

## 🔧 Поддерживаемые провайдеры

### 🌟 Gmail (рекомендуется)
- **Надежность**: ★★★★★
- **Скорость**: ★★★★★
- **Настройка**: Средняя

### 🇷🇺 Yandex
- **Надежность**: ★★★★☆
- **Скорость**: ★★★★☆
- **Настройка**: Легкая

### 🇷🇺 Mail.ru
- **Надежность**: ★★★☆☆
- **Скорость**: ★★★☆☆
- **Настройка**: Легкая

### 🌍 Outlook
- **Надежность**: ★★★★☆
- **Скорость**: ★★★★☆
- **Настройка**: Средняя

---

## 📧 Настройка Gmail

### Шаг 1: Включите 2FA
1. Перейдите в [Google Account](https://myaccount.google.com/)
2. Включите **двухфакторную аутентификацию**
3. Это обязательно для создания пароля приложения

### Шаг 2: Создайте пароль приложения
1. Перейдите в [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Выберите:
   - **Приложение**: Другое (custom name)
   - **Имя**: Eco-Kolendar
3. Нажмите **Создать**
4. Скопируйте сгенерированный пароль (16 символов)

### Шаг 3: Настройте переменные окружения
```env
# В файле backend/.env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_16_character_app_password
FROM_EMAIL=your_email@gmail.com
```

### Шаг 4: Проверка
```python
# Тестовый скрипт
import smtplib
from email.mime.text import MIMEText

def test_email():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your_email@gmail.com', 'your_app_password')
    
    msg = MIMEText('Тестовое сообщение')
    msg['Subject'] = 'Тест Эко-Календарь'
    msg['From'] = 'your_email@gmail.com'
    msg['To'] = 'test@example.com'
    
    server.send_message(msg)
    server.quit()
    print("Email отправлен успешно!")
```

---

## 🇷🇺 Настройка Yandex

### Шаг 1: Включите IMAP
1. Перейдите в [Yandex Mail](https://mail.yandex.ru/)
2. **Настройки** → **Все настройки**
3. **Почтовые программы** → **IMAP**
4. Включите IMAP

### Шаг 2: Настройте переменные окружения
```env
SMTP_SERVER=smtp.yandex.ru
SMTP_PORT=587
EMAIL_USER=your_email@yandex.ru
EMAIL_PASSWORD=your_yandex_password
FROM_EMAIL=your_email@yandex.ru
```

### Шаг 3: Проверка
```python
import smtplib

def test_yandex_email():
    server = smtplib.SMTP('smtp.yandex.ru', 587)
    server.starttls()
    server.login('your_email@yandex.ru', 'your_password')
    # ... отправка email
    server.quit()
```

---

## 🇷🇺 Настройка Mail.ru

### Шаг 1: Настройте переменные окружения
```env
SMTP_SERVER=smtp.mail.ru
SMTP_PORT=587
EMAIL_USER=your_email@mail.ru
EMAIL_PASSWORD=your_mail_password
FROM_EMAIL=your_email@mail.ru
```

### Шаг 2: Проверка
```python
import smtplib

def test_mailru_email():
    server = smtplib.SMTP('smtp.mail.ru', 587)
    server.starttls()
    server.login('your_email@mail.ru', 'your_password')
    # ... отправка email
    server.quit()
```

---

## 🌍 Настройка Outlook

### Шаг 1: Настройте переменные окружения
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
EMAIL_USER=your_email@outlook.com
EMAIL_PASSWORD=your_outlook_password
FROM_EMAIL=your_email@outlook.com
```

### Шаг 2: Проверка
```python
import smtplib

def test_outlook_email():
    server = smtplib.SMTP('smtp-mail.outlook.com', 587)
    server.starttls()
    server.login('your_email@outlook.com', 'your_password')
    # ... отправка email
    server.quit()
```

---

## 🛠️ Конфигурация в коде

### EmailService класс
```python
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.email_user)
    
    def send_email(self, to_email, subject, body, html_body=None):
        """Отправить email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Текстовая версия
            text_part = MIMEText(body, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # HTML версия (если есть)
            if html_body:
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Отправка
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Ошибка отправки email: {e}")
            return False
```

---

## 📨 Типы email уведомлений

### 1. Регистрация пользователя
```python
def send_welcome_email(user_email, user_name):
    subject = "Добро пожаловать в Эко-Календарь!"
    body = f"""
    Здравствуйте, {user_name}!
    
    Спасибо за регистрацию в Эко-Календаре.
    
    Вы теперь можете:
    - Просматривать экологические праздники
    - Использовать интерактивную карту
    - Получать погодную информацию
    
    С уважением,
    Команда Эко-Календаря
    """
    
    email_service.send_email(user_email, subject, body)
```

### 2. Напоминание о празднике
```python
def send_holiday_reminder(user_email, holiday_name, holiday_date):
    subject = f"Напоминание: {holiday_name}"
    body = f"""
    Здравствуйте!
    
    Напоминаем, что завтра ({holiday_date}) отмечается {holiday_name}.
    
    Не забудьте об экологических мероприятиях!
    
    С уважением,
    Эко-Календарь
    """
    
    email_service.send_email(user_email, subject, body)
```

### 3. Уведомление о новом празднике
```python
def send_new_holiday_notification(user_email, holiday_name, holiday_date):
    subject = f"Новый праздник: {holiday_name}"
    body = f"""
    Здравствуйте!
    
    В календаре добавлен новый праздник:
    
    {holiday_name} - {holiday_date}
    
    Посмотреть детали можно на сайте Эко-Календаря.
    
    С уважением,
    Эко-Календарь
    """
    
    email_service.send_email(user_email, subject, body)
```

---

## 🚨 Распространенные проблемы

### Gmail: "Пароль неверен"
**Причина**: Используется обычный пароль вместо пароля приложения  
**Решение**: Создайте пароль приложения в настройках Google

### Yandex: "Ошибка аутентификации"
**Причина**: Не включен IMAP  
**Решение**: Включите IMAP в настройках Yandex Mail

### Mail.ru: "Соединение отклонено"
**Причина**: Неправильный порт или сервер  
**Решение**: Используйте smtp.mail.ru:587

### Общие проблемы
- **Брандмауэр**: блокирует порт 587
- **Антивирус**: блокирует SMTP соединения
- **Провайдер**: блокирует SMTP трафик

---

## 🔒 Безопасность

### Хранение паролей
- ✅ Используйте переменные окружения
- ✅ Не храните пароли в коде
- ✅ Используйте пароли приложений (Gmail)
- ✅ Регулярно меняйте пароли

### Шифрование
- ✅ Используйте TLS/SSL (port 587)
- ✅ Проверяйте сертификаты сервера
- ✅ Не передавайте пароли в открытом виде

### Ограничения
- 📊 Gmail: 500 email/день для обычных аккаунтов
- 📊 Yandex: ~100 email/день
- 📊 Mail.ru: ~50 email/день
- 📊 Outlook: ~300 email/день

---

## 🧪 Тестирование

### Тестовый скрипт
```python
# test_email.py
import os
from backend.app.external_apis import EmailService

def test_email_service():
    email_service = EmailService()
    
    # Проверка конфигурации
    if not email_service.email_user:
        print("❌ EMAIL_USER не настроен")
        return
    
    if not email_service.email_password:
        print("❌ EMAIL_PASSWORD не настроен")
        return
    
    # Тестовая отправка
    test_email = "test@example.com"
    subject = "Тест Эко-Календарь"
    body = "Это тестовое сообщение от Эко-Календаря"
    
    success = email_service.send_email(test_email, subject, body)
    
    if success:
        print("✅ Email отправлен успешно")
    else:
        print("❌ Ошибка отправки email")

if __name__ == "__main__":
    test_email_service()
```

### Запуск теста
```bash
cd backend
python test_email.py
```

---

## 📊 Мониторинг

### Логирование
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email_with_logging(user_email, subject, body):
    try:
        success = email_service.send_email(user_email, subject, body)
        if success:
            logger.info(f"Email отправлен на {user_email}")
        else:
            logger.error(f"Ошибка отправки на {user_email}")
    except Exception as e:
        logger.error(f"Исключение при отправке email: {e}")
```

### Статистика
```python
# Отслеживание отправленных email
email_stats = {
    'sent': 0,
    'failed': 0,
    'last_sent': None
}

def update_stats(success):
    if success:
        email_stats['sent'] += 1
        email_stats['last_sent'] = datetime.now()
    else:
        email_stats['failed'] += 1
```

---

## 🔄 Альтернативные сервисы

### SendGrid
- **Бесплатно**: 100 email/день
- **Надежность**: ★★★★★
- **API**: REST API

### Mailgun
- **Бесплатно**: 1000 email/месяц
- **Надежность**: ★★★★★
- **API**: REST API

### AWS SES
- **Бесплатно**: 62000 email/месяц
- **Надежность**: ★★★★★
- **API**: AWS SDK

---

## 📞 Поддержка

### Документация провайдеров
- [Gmail Help](https://support.google.com/mail/)
- [Yandex Help](https://yandex.ru/support/mail/)
- [Mail.ru Help](https://help.mail.ru/)
- [Outlook Help](https://support.microsoft.com/ru-ru/outlook/)

### Сообщество
- [Stack Overflow](https://stackoverflow.com/)
- [GitHub Issues](https://github.com/issues)
- [Python SMTP](https://docs.python.org/3/library/smtplib.html)

---

**📧 Правильная настройка email - важная часть Эко-Календаря!**
