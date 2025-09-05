# QRailway - Railway Management System

A comprehensive Django-based railway management system that facilitates requirement management, vendor bidding, and equipment tracking through QR codes.

## Features

### User Types
- **Railway Authority**: Create and manage requirements, assign vendors, track progress
- **Vendor**: Browse requirements, submit bids, manage assigned projects
- **Railway Worker**: Inspect equipment, perform installations, update status
- **Software Staff**: System administration, monitoring, and support

### Core Functionality
- **Requirement Management**: Create, track, and manage railway equipment requirements
- **Vendor Bidding System**: Vendors can submit proposals for requirements
- **QR Code Integration**: Generate and scan QR codes for equipment tracking
- **Status Tracking**: Track requirements through multiple stages (Inactive → Shipped → Received → Active)
- **Notification System**: Real-time alerts and reminders for deadlines and status changes
- **Inspection Management**: Record inspections at different stages
- **Location-based Access**: Zone and division-based access control

### Technical Features
- **Modern UI**: Bootstrap 5 responsive design
- **Real-time Notifications**: Email, SMS, and in-app notifications
- **API Endpoints**: RESTful APIs for mobile integration and QR scanning
- **Background Tasks**: Celery for scheduled notifications and alerts
- **Security**: Role-based access control and audit logging
- **Scalability**: Production-ready with Redis caching and PostgreSQL

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis 6+
- Node.js (for frontend assets)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd QRailway/QRAILWAY
   ```

2. **Create virtual environment**
   ```bash
   python -m venv ../venv
   source ../venv/bin/activate  # On Windows: ..\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp env.example .env
   # Edit .env with your database and Redis credentials
   ```

5. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py create_initial_data
   ```

6. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

7. **Start Services**
   ```bash
   # Start Django development server
   python manage.py runserver
   
   # Start Celery worker (in another terminal)
   celery -A qrail worker -l info
   
   # Start Celery beat (in another terminal)
   celery -A qrail beat -l info
   
   # Start Redis (if not running)
   redis-server
   ```

## Configuration

### Environment Variables
```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=qrailway
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@qrail.com
```

### User Types and Permissions

#### Railway Authority
- Create and manage requirements
- Assign vendors to requirements
- Approve/reject vendor requests
- Update requirement status
- View all requirements in their zone/division

#### Vendor
- Browse available requirements
- Submit bids for requirements
- View assigned requirements
- Update status of assigned requirements
- Access to vendor-specific dashboard

#### Railway Worker
- View requirements in their zone/division
- Conduct inspections
- Update installation status
- Upload inspection photos and reports

#### Software Staff
- Full system access
- User management
- System monitoring
- Database administration

## API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/user/` - Get current user info

### Requirements
- `GET /api/requirements/` - List requirements
- `POST /api/requirements/` - Create requirement
- `GET /api/requirements/{id}/` - Get requirement details
- `PUT /api/requirements/{id}/` - Update requirement
- `DELETE /api/requirements/{id}/` - Delete requirement

### QR Code Scanning
- `GET /api/scan/{uuid}/` - Scan QR code and get requirement info

### Notifications
- `GET /api/notifications/` - List user notifications
- `POST /api/notifications/{id}/read/` - Mark notification as read

## QR Code System

### QR Code Generation
- Each requirement gets a unique UUID
- QR codes contain requirement information and API endpoint
- Generated automatically when requirement is created
- Stored as images in the media directory

### QR Code Scanning
- Mobile-friendly API endpoint for scanning
- Returns requirement details and current status
- Logs scan events for analytics
- Supports both authenticated and anonymous scanning

## Notification System

### Types of Notifications
- **New Requirement**: Notify vendors about new requirements
- **Requirement Assigned**: Notify vendor when assigned
- **Deadline Reminders**: Alert about approaching deadlines
- **Status Changes**: Notify about requirement status updates
- **Inspection Due**: Remind about pending inspections

### Delivery Methods
- **In-app**: Real-time notifications in the web interface
- **Email**: Configurable frequency (immediate, daily, weekly)
- **SMS**: Optional SMS notifications (requires SMS service)
- **Push**: Browser push notifications

### Scheduling
- Daily deadline reminders (7, 3, 1 days before deadline)
- Overdue notifications
- Daily and weekly digest emails
- System health monitoring

## Database Schema

### Core Models
- **User**: Custom user model with role-based access
- **RailwayZone**: Railway zones (SR, ER, WR, etc.)
- **RailwayDivision**: Divisions within zones
- **Requirement**: Equipment requirements with status tracking
- **VendorRequest**: Vendor bids for requirements
- **RequirementInspection**: Inspection records
- **Notification**: System notifications

### Key Relationships
- Users belong to zones/divisions
- Requirements are created by Railway Authority
- Vendors can submit requests for requirements
- Requirements have multiple inspection records
- All actions generate notifications

## Deployment

### Production Setup
1. **Web Server**: Use Gunicorn with Nginx
2. **Database**: PostgreSQL with connection pooling
3. **Cache**: Redis for sessions and caching
4. **Background Tasks**: Celery with Redis broker
5. **Static Files**: Serve via CDN or Nginx
6. **SSL**: Use Let's Encrypt for HTTPS

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Create initial data
docker-compose exec web python manage.py create_initial_data
```

### Environment Variables for Production
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=your-production-secret-key

# Database
DB_NAME=qrailway_prod
DB_USER=qrailway_user
DB_PASSWORD=secure-password
DB_HOST=db-host
DB_PORT=5432

# Redis
REDIS_URL=redis://redis-host:6379/0

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=email-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

## Monitoring and Maintenance

### Health Checks
- `/health/` - Basic health check
- `/health/ready/` - Readiness probe
- `/health/live/` - Liveness probe

### Logging
- Application logs in `logs/django.log`
- Celery task logs
- Access logs via web server
- Error tracking (integrate with Sentry)

### Backup Strategy
- Database backups (daily)
- Media files backup
- Configuration backup
- Log rotation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## Roadmap

### Phase 1 (Current)
- ✅ Basic requirement management
- ✅ Vendor bidding system
- ✅ QR code integration
- ✅ Notification system
- ✅ User dashboards

### Phase 2 (Planned)
- 📱 Mobile application
- 📊 Advanced analytics
- 🔄 Workflow automation
- 📈 Performance monitoring
- 🌐 Multi-language support

### Phase 3 (Future)
- 🤖 AI-powered insights
- 🔗 Third-party integrations
- ☁️ Cloud deployment
- 🔒 Advanced security features
- 📱 IoT device integration