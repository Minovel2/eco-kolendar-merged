@echo off
cd /d "%~dp0"
cd backend
echo Running holiday notifications...
python -c "from app.notifications import send_holiday_notifications; send_holiday_notifications()"
echo Done.