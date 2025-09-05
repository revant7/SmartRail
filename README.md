# QRAIL - Railway Parts Tracking System

A comprehensive Django-based web application for tracking railway parts using QR codes. This system enables railway employees to scan QR codes engraved on parts to access detailed information about each component.

## Features

### 🔐 User Authentication & Authorization
- **Multi-role system**: Railway employees, authorities, vendors, admins, inspectors, and managers
- **Role-based access control**: Different permissions for different user types
- **Secure authentication**: Session management with security features
- **User profile management**: Extended profiles with role-specific information

### 📦 Parts Management
- **Comprehensive part database**: Track all railway components with detailed specifications
- **QR code integration**: Automatic QR code generation for each part
- **Category management**: Organize parts by categories and subcategories
- **Document management**: Attach manuals, certificates, and other documents
- **Image gallery**: Store and manage part images
- **Maintenance tracking**: Record maintenance activities and schedules

### 🛒 Order Management
- **Project-based organization**: Group orders by railway projects
- **Vendor management**: Maintain vendor information and performance metrics
- **Purchase order workflow**: Complete order lifecycle from creation to delivery
- **Line item tracking**: Detailed tracking of individual items in orders
- **Status management**: Track order progress through various stages
- **Document management**: Store order-related documents

### 📍 Tracking & Monitoring
- **Real-time tracking**: Track part locations and status changes
- **Inspection records**: Comprehensive inspection management
- **Quality checks**: Quality assurance and compliance tracking
- **Alert system**: Automated alerts for maintenance, inspections, and issues
- **Audit logging**: Complete audit trail of all system activities

### 📱 QR Code Scanner
- **Web-based scanner**: Built-in QR code scanner using device camera
- **Mobile-friendly**: Responsive design for mobile devices
- **Instant lookup**: Real-time part information retrieval
- **Scan history**: Track recent scans for quick access

### 🎨 Modern UI/UX
- **Responsive design**: Works on desktop, tablet, and mobile devices
- **Bootstrap 5**: Modern, clean interface
- **Interactive dashboard**: Real-time statistics and recent activities
- **Intuitive navigation**: Easy-to-use interface for all user types

## Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **QR Code**: html5-qrcode library
- **Deployment**: Docker, Nginx, Gunicorn

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 12+
- Redis 6+
- Docker (optional)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd qrail
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=qrail_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@qrail.com

# AWS S3 Configuration (for production)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

## Usage

### User Roles

1. **System Administrator**: Full system access, user management
2. **Railway Authority**: Oversight, approval workflows, user management
3. **Railway Employee**: Part management, order creation, scanning
4. **Vendor**: Order management, delivery tracking
5. **Quality Inspector**: Inspection management, quality checks
6. **Project Manager**: Project oversight, order management

### Key Workflows

#### Part Management
1. Create parts with detailed specifications
2. Generate QR codes automatically
3. Track maintenance and inspections
4. Update location and status information

#### Order Management
1. Create projects for organizing orders
2. Add vendors and manage vendor information
3. Create purchase orders with line items
4. Track order status through approval and delivery

#### QR Code Scanning
1. Use the built-in scanner or mobile app
2. Scan QR codes to instantly access part information
3. View maintenance history and upcoming inspections
4. Update part status and location

## API Documentation

The system provides a comprehensive REST API for mobile applications and integrations:

- **Authentication**: Token-based authentication
- **Parts API**: CRUD operations for parts management
- **Orders API**: Order management and tracking
- **QR Code API**: Part lookup by QR code
- **Tracking API**: Real-time tracking and monitoring

## Security Features

- **HTTPS enforcement**: SSL/TLS encryption
- **CSRF protection**: Cross-site request forgery protection
- **XSS protection**: Cross-site scripting prevention
- **Rate limiting**: API and login rate limiting
- **Session security**: Secure session management
- **Input validation**: Comprehensive input sanitization
- **Audit logging**: Complete activity tracking

## Performance Optimizations

- **Database indexing**: Optimized database queries
- **Caching**: Redis-based caching for improved performance
- **Static file optimization**: CDN-ready static file serving
- **Image optimization**: Automatic image compression
- **Database connection pooling**: Efficient database connections

## Deployment

### Production Deployment

1. **Configure production settings**
   ```bash
   export DJANGO_SETTINGS_MODULE=qrail.settings_production
   ```

2. **Set up SSL certificates**
   ```bash
   # Place SSL certificates in ssl/ directory
   cp your-cert.pem ssl/cert.pem
   cp your-key.pem ssl/key.pem
   ```

3. **Deploy with Docker**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

### Environment-specific Configuration

- **Development**: `qrail.settings`
- **Production**: `qrail.settings_production`

## Monitoring and Logging

- **Application logs**: Comprehensive logging for debugging
- **Error tracking**: Sentry integration for error monitoring
- **Performance monitoring**: Database and application metrics
- **Health checks**: Automated health monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation wiki

## Roadmap

- [ ] Mobile application (React Native)
- [ ] Advanced analytics dashboard
- [ ] Integration with external systems
- [ ] Machine learning for predictive maintenance
- [ ] IoT device integration
- [ ] Multi-language support
- [ ] Advanced reporting features
