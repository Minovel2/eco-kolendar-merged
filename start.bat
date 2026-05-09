@echo off
echo Installing Python dependencies...
cd backend
pip install --upgrade fastapi uvicorn sqlalchemy python-dotenv alembic pydantic
echo.
echo Starting Backend Server...
start cmd /k python -m uvicorn app.main:app --reload --port 8000
echo.
echo Backend started on port 8000
echo Swagger: http://localhost:8000/docs
echo API: http://localhost:8000/api/holidays
echo.
timeout /t 3
echo Opening frontend.html in browser...
cd ..
start frontend.html
