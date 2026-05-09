# 🗄️ Руководство по базе данных SQLite

## 📋 Обзор

Эко-Календарь использует **SQLite** в качестве базы данных. SQLite - это легковесная файловая база данных, которая не требует отдельного сервера.

---

## 📁 Файл базы данных

```
backend/holidays.db
```

Этот файл содержит все данные приложения:
- Праздники
- Рабочие дни
- Пользователей

---

## 🔧 Работа с базой данных

### Через Python (рекомендуется)

#### Подключение к БД
```python
import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('backend/holidays.db')
cursor = conn.cursor()
```

#### Просмотр таблиц
```python
# Получить список всех таблиц
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(tables)
```

#### Просмотр данных
```python
# Все праздники
cursor.execute("SELECT * FROM holidays;")
holidays = cursor.fetchall()

# Все пользователи
cursor.execute("SELECT id, email, name, role FROM users;")
users = cursor.fetchall()

# Рабочие дни
cursor.execute("SELECT * FROM work_days;")
work_days = cursor.fetchall()
```

#### Закрытие соединения
```python
conn.close()
```

---

### Через командную строку

#### Установка SQLite
```bash
# Windows (обычно уже установлен)
sqlite3 --version

# Linux
sudo apt-get install sqlite3

# macOS
brew install sqlite
```

#### Работа с БД
```bash
# Перейти в папку backend
cd backend

# Открыть базу данных
sqlite3 holidays.db

# Основные команды
.tables                    # Показать таблицы
.schema                    # Показать структуру
.dump                      # Экспорт всей БД
.quit                      # Выход
```

#### SQL запросы
```sql
-- Посмотреть все праздники
SELECT * FROM holidays;

-- Посмотреть пользователей
SELECT id, email, name, role FROM users;

-- Посмотреть рабочие дни
SELECT * FROM work_days;

-- Найти праздники в определенную дату
SELECT * FROM holidays WHERE date = '2024-06-05';

-- Посмотреть праздники по типу
SELECT * FROM holidays WHERE type = 'national';
```

---

## 📊 Структура таблиц

### `holidays`
```sql
CREATE TABLE holidays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT,
    type TEXT DEFAULT 'national',
    region TEXT DEFAULT 'international',
    image_url TEXT
);
```

### `work_days`
```sql
CREATE TABLE work_days (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    work_days_count INTEGER NOT NULL
);
```

### `users`
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role INTEGER DEFAULT 0
);
```

---

## 🔍 Полезные запросы

### Анализ данных
```sql
-- Количество праздников по типам
SELECT type, COUNT(*) as count FROM holidays GROUP BY type;

-- Праздники в текущем месяце
SELECT * FROM holidays 
WHERE strftime('%m', date) = strftime('%m', 'now');

-- Пользователи по ролям
SELECT role, COUNT(*) as count FROM users GROUP BY role;
```

### Поиск данных
```sql
-- Поиск праздников по названию
SELECT * FROM holidays WHERE name LIKE '%экология%';

-- Праздники в диапазоне дат
SELECT * FROM holidays 
WHERE date BETWEEN '2024-06-01' AND '2024-06-30';
```

---

## 🛠️ Управление данными

### Добавление данных
```sql
-- Новый праздник
INSERT INTO holidays (name, date, description, type, region)
VALUES ('Новый праздник', '2024-12-25', 'Описание', 'national', 'international');

-- Новый пользователь
INSERT INTO users (email, name, password_hash, role)
VALUES ('user@example.com', 'Иван Иванов', 'hashed_password', 0);
```

### Обновление данных
```sql
-- Обновить описание праздника
UPDATE holidays 
SET description = 'Новое описание' 
WHERE id = 1;

-- Обновить роль пользователя
UPDATE users 
SET role = 1 
WHERE email = 'admin@example.com';
```

### Удаление данных
```sql
-- Удалить праздник
DELETE FROM holidays WHERE id = 1;

-- Удалить пользователя
DELETE FROM users WHERE email = 'user@example.com';
```

---

## 📱 Графические инструменты

### DB Browser for SQLite
- **Скачать**: https://sqlitebrowser.org/
- **Платформы**: Windows, macOS, Linux
- **Функции**: Просмотр, редактирование, запросы

### VS Code расширения
- **SQLite Viewer** - просмотр БД прямо в VS Code
- **SQLTools** - выполнение SQL запросов

### Онлайн инструменты
- **SQLite Online Viewer** - веб-интерфейс
- **DB Fiddle** - тестирование SQL

---

## 🔧 Резервное копирование

### Создание резервной копии
```bash
# Копия файла БД
cp backend/holidays.db backend/holidays_backup.db

# Через SQLite
sqlite3 backend/holidays.db ".backup backup.db"
```

### Восстановление из копии
```bash
# Восстановление из копии
cp backend/holidays_backup.db backend/holidays.db
```

### Экспорт данных
```bash
# Экспорт в SQL файл
sqlite3 backend/holidays.db ".dump" > backup.sql

# Экспорт только таблицы
sqlite3 backend/holidays.db ".dump holidays" > holidays.sql
```

### Импорт данных
```bash
# Импорт из SQL файла
sqlite3 new_holidays.db < backup.sql
```

---

## 🚨 Важные замечания

### Безопасность
- 🔒 Файл БД должен быть защищен от записи
- 👥 Не храните пароли в открытом виде
- 📋 Регулярно делайте резервные копии

### Производительность
- ⚡ SQLite оптимизирован для небольших БД
- 📊 Добавляйте индексы для частых запросов
- 🧹 Периодически очищайте БД (VACUUM)

### Ограничения
- 👥 Одновременная запись ограничена
- 📏 Размер файла до 140TB
- 🔗 Нет сложных связей между таблицами

---

## 🔄 Обслуживание БД

### Оптимизация
```sql
-- Очистка БД
VACUUM;

-- Анализ статистики
ANALYZE;

-- Проверка целостности
PRAGMA integrity_check;
```

### Просмотр статистики
```sql
-- Размер БД
SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();

-- Количество записей в таблицах
SELECT 'holidays' as table_name, COUNT(*) as count FROM holidays
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'work_days', COUNT(*) FROM work_days;
```

---

## 📞 Поддержка

### Частые проблемы
- **"database is locked"** - закройте все соединения с БД
- **"no such table"** - проверьте путь к файлу БД
- **"file is encrypted"** - файл поврежден, восстановите из копии

### Диагностика
```python
# Проверка соединения
try:
    conn = sqlite3.connect('backend/holidays.db')
    print("База данных доступна")
    conn.close()
except sqlite3.Error as e:
    print(f"Ошибка: {e}")
```

---

**🗄️ SQLite - простая и надежная база данных для Эко-Календаря!**
