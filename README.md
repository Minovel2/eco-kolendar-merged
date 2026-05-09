# 🌿 Eco-Kolendar (Эко-Календарь)

Экологический и национальный календарь праздников с панелью администратора.

## 📋 Технологии

- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI
- **База данных**: PostgreSQL
- **Документация API**: Swagger

## 🚀 Быстрый старт

### Что нужно установить заранее:
1. **Python** (версия 3.10+) - https://www.python.org/downloads/
2. **Node.js** (версия 18+) - https://nodejs.org/
3. **PostgreSQL** - https://www.postgresql.org/download/

### 1. Клонируем репозиторий
```bash
git clone https://github.com/Minovel2/eco-kolendar.git
cd eco-kolendar
```

### 2. Устанавливаем Frontend
```bash
npm install
```

### 3. Настраиваем Backend

#### Создаем базу данных в PostgreSQL:
Открываем PGAdmin4:
1. Подключаемся к серверу PostgreSQL
2. Правый клик на "Databases" → "Create" → "Database"
3. Название: `eco_kolendar`
4. Нажимаем "Save"

#### Устанавливаем Python зависимости:
```bash
cd backend
pip install -r requirements.txt
```

#### Настраиваем подключение к БД:
Создаем файл `backend/.env` и записываем в него:
```
DATABASE_URL=postgresql://postgres:ВАШ_ПАРОЛЬ@localhost:5432/eco_kolendar
```
> Замените `ВАШ_ПАРОЛЬ` на пароль от PostgreSQL

#### Заполняем базу данных:
```bash
python fill_db.py
```

### 4. Запускаем проект

**Терминал 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Терминал 2 - Frontend (открыть новый терминал):**
```bash
npm run dev
```

### 5. Открываем в браузере:
- 🌐 **Сайт**: http://localhost:3000
- 📚 **Swagger документация**: http://localhost:8000/docs
- 🔌 **API**: http://localhost:8000/api/holidays

### 6. Простая версия (если React не работает):
Открыть файл `frontend.html` в браузере (двойной клик)

## 📁 Структура проекта
```
eco-kolendar/
├── src/                    # React компоненты
├── backend/               # Python FastAPI
│   ├── app/
│   │   ├── main.py        # Основной файл API
│   │   ├── models.py      # Модели базы данных
│   │   ├── database.py    # Подключение к БД
│   │   ├── schemas.py     # Схемы данных
│   │   └── crud.py        # Операции с БД
│   ├── fill_db.py         # Заполнение БД тестовыми данными
│   └── requirements.txt   # Python зависимости
├── frontend.html          # Простая HTML версия (без React)
├── package.json           # Node.js зависимости
└── vite.config.ts         # Конфигурация Vite
```

## 📝 API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/holidays` | Получить все праздники |
| POST | `/api/holidays` | Добавить новый праздник |
| GET | `/api/holidays/{id}` | Получить праздник по ID |
| DELETE | `/api/holidays/{id}` | Удалить праздник по ID |

## 🎯 Фильтры API

```
/api/holidays?type=eco        # Только экологические
/api/holidays?type=national   # Только национальные
/api/holidays?region=russia   # Только Россия
/api/holidays?search=день     # Поиск по названию
```

## 🛠️ Команды

| Команда | Где выполнять | Описание |
|---------|--------------|----------|
| `npm install` | Корень проекта | Установка JS зависимостей |
| `npm run dev` | Корень проекта | Запуск Frontend |
| `pip install -r requirements.txt` | Папка backend | Установка Python зависимостей |
| `python -m uvicorn app.main:app --reload --port 8000` | Папка backend | Запуск Backend |
| `python fill_db.py` | Папка backend | Заполнение БД |

## ❗ Частые проблемы

**Ошибка подключения к БД:**
- Проверьте, запущен ли PostgreSQL
- Проверьте пароль в файле `.env`
- Убедитесь, что база данных `eco_kolendar` создана

**Frontend не запускается:**
- Попробуйте `npm cache clean --force`
- Или откройте `frontend.html` в браузере

**Backend не запускается:**
- Проверьте, установлены ли Python зависимости
- Убедитесь, что порт 8000 не занят
