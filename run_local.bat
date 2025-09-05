@echo off
echo Starting QRAIL with local settings...
echo.
echo Virtual environment: venv
echo Database: SQLite (db.sqlite3)
echo Settings: qrail.settings_local
echo.
echo Server will be available at: http://127.0.0.1:8000
echo Admin panel: http://127.0.0.1:8000/admin/
echo.
echo Press Ctrl+C to stop the server
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Start Django development server
python manage.py runserver --settings=qrail.settings_local

pause
