#!/bin/bash

# QRAIL Deployment Script
# This script handles the deployment of the QRAIL application

set -e  # Exit on any error

echo "🚀 Starting QRAIL deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from env.example..."
    cp env.example .env
    print_warning "Please edit .env file with your configuration before continuing."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles
mkdir -p ssl

# Set proper permissions
chmod 755 logs media staticfiles ssl

# Build and start services
print_status "Building and starting services..."
docker-compose down --remove-orphans
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check if services are running
print_status "Checking service health..."
if ! docker-compose ps | grep -q "Up"; then
    print_error "Some services failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Run database migrations
print_status "Running database migrations..."
docker-compose exec -T web python manage.py migrate

# Create superuser if it doesn't exist
print_status "Creating superuser (if not exists)..."
docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@qrail.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Collect static files
print_status "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Load initial data (if exists)
if [ -f "fixtures/initial_data.json" ]; then
    print_status "Loading initial data..."
    docker-compose exec -T web python manage.py loaddata fixtures/initial_data.json
fi

# Set up SSL certificates (if provided)
if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
    print_status "SSL certificates found. HTTPS will be enabled."
else
    print_warning "SSL certificates not found. Please add cert.pem and key.pem to ssl/ directory for HTTPS."
fi

# Final health check
print_status "Performing final health check..."
sleep 10

if curl -f http://localhost/health/ > /dev/null 2>&1; then
    print_status "✅ Application is healthy and running!"
    echo ""
    echo "🌐 Application URLs:"
    echo "   - Web Interface: http://localhost"
    echo "   - Admin Panel: http://localhost/admin/"
    echo "   - API Documentation: http://localhost/api/"
    echo ""
    echo "👤 Default Admin Credentials:"
    echo "   - Username: admin"
    echo "   - Password: admin123"
    echo ""
    echo "📊 Monitoring:"
    echo "   - Health Check: http://localhost/health/"
    echo "   - Logs: docker-compose logs -f"
    echo ""
    print_status "🎉 Deployment completed successfully!"
else
    print_error "Health check failed. Please check the logs: docker-compose logs"
    exit 1
fi
