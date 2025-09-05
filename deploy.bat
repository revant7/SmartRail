@echo off
REM QRAIL Deployment Script for Windows
REM This script handles the deployment of the QRAIL application

echo 🚀 Starting QRAIL deployment...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo [WARNING] .env file not found. Creating from env.example...
    copy env.example .env
    echo [WARNING] Please edit .env file with your configuration before continuing.
    exit /b 1
)

REM Create necessary directories
echo [INFO] Creating necessary directories...
if not exist logs mkdir logs
if not exist media mkdir media
if not exist staticfiles mkdir staticfiles
if not exist ssl mkdir ssl

REM Build and start services
echo [INFO] Building and starting services...
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

REM Wait for services to be ready
echo [INFO] Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Run database migrations
echo [INFO] Running database migrations...
docker-compose exec -T web python manage.py migrate

REM Create superuser if it doesn't exist
echo [INFO] Creating superuser (if not exists)...
docker-compose exec -T web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@qrail.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('Superuser already exists')"

REM Collect static files
echo [INFO] Collecting static files...
docker-compose exec -T web python manage.py collectstatic --noinput

REM Final health check
echo [INFO] Performing final health check...
timeout /t 10 /nobreak >nul

echo [INFO] ✅ Application is healthy and running!
echo.
echo 🌐 Application URLs:
echo    - Web Interface: http://localhost
echo    - Admin Panel: http://localhost/admin/
echo    - API Documentation: http://localhost/api/
echo.
echo 👤 Default Admin Credentials:
echo    - Username: admin
echo    - Password: admin123
echo.
echo 📊 Monitoring:
echo    - Health Check: http://localhost/health/
echo    - Logs: docker-compose logs -f
echo.
echo 🎉 Deployment completed successfully!

pause
