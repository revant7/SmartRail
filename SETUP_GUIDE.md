# QRAIL Setup Guide

## 🚀 Quick Start

Your QRAIL Railway Parts Tracking System is now ready! Here's how to get started:

### ✅ What's Already Done

1. **Virtual Environment**: Created and activated (`venv`)
2. **Dependencies**: All packages installed from `requirements.txt`
3. **Database**: SQLite database created with all tables
4. **Admin User**: Superuser account created
5. **Development Server**: Running on http://127.0.0.1:8000

### 🌐 Access Your Application

- **Main Application**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **API Endpoints**: http://127.0.0.1:8000/api/

### 👤 Default Admin Credentials

- **Username**: `admin`
- **Password**: `admin` (or whatever you set during creation)

## 🛠 Development Commands

### Start the Server
```bash
# Windows
run_local.bat

# Linux/Mac
./run_local.sh

# Or manually
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
python manage.py runserver --settings=qrail.settings_local
```

### Database Operations
```bash
# Create new migrations
python manage.py makemigrations --settings=qrail.settings_local

# Apply migrations
python manage.py migrate --settings=qrail.settings_local

# Create superuser
python manage.py createsuperuser --settings=qrail.settings_local
```

### Django Shell
```bash
python manage.py shell --settings=qrail.settings_local
```

## 📱 Features Available

### 1. User Management
- **6 User Types**: Admin, Railway Authority, Railway Employee, Vendor, Inspector, Manager
- **Role-based Access**: Different permissions for each user type
- **User Profiles**: Extended profiles with role-specific information

### 2. Parts Management
- **Part Database**: Comprehensive parts with specifications
- **QR Code Generation**: Automatic QR codes for each part
- **Categories**: Hierarchical part categorization
- **Documents & Images**: File attachments for parts
- **Maintenance Tracking**: Schedule and history

### 3. Order Management
- **Projects**: Organize orders by railway projects
- **Vendors**: Vendor management with performance tracking
- **Purchase Orders**: Complete order workflow
- **Line Items**: Detailed item tracking
- **Status Management**: Order progress tracking

### 4. QR Code Scanner
- **Web Scanner**: Built-in camera-based scanner
- **Mobile Friendly**: Responsive design
- **Instant Lookup**: Real-time part information
- **Scan History**: Recent scans tracking

### 5. Tracking & Monitoring
- **Real-time Tracking**: Part location and status
- **Inspections**: Comprehensive inspection records
- **Quality Checks**: Quality assurance tracking
- **Alerts**: Automated notifications
- **Audit Logs**: Complete activity tracking

## 🔧 Configuration

### Local Development Settings
The application is configured to use:
- **Database**: SQLite (`db.sqlite3`)
- **Cache**: Dummy cache (no Redis required)
- **Celery**: Eager execution (no background tasks)
- **Debug**: Enabled for development

### Environment Variables
For production, create a `.env` file with:
```env
SECRET_KEY=your-secret-key
DEBUG=False
DB_NAME=qrail_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

## 📊 Sample Data

### Create Sample Parts
1. Go to Admin Panel: http://127.0.0.1:8000/admin/
2. Login with admin credentials
3. Navigate to "Parts" → "Part categories"
4. Create categories like "Track Components", "Signaling", etc.
5. Navigate to "Parts" → "Parts"
6. Create sample parts with QR codes

### Create Sample Orders
1. Go to Admin Panel
2. Navigate to "Orders" → "Projects"
3. Create railway projects
4. Navigate to "Orders" → "Vendors"
5. Create vendor companies
6. Navigate to "Orders" → "Purchase orders"
7. Create sample orders

## 🧪 Testing

### Run Tests
```bash
python manage.py test --settings=qrail.settings_local
```

### Test QR Scanner
1. Create a part in the admin panel
2. Go to http://127.0.0.1:8000/qr-scanner/
3. Use the QR code from the part
4. Test the scanning functionality

## 🚀 Production Deployment

### Using Docker
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or use the deployment script
./deploy.sh  # Linux/Mac
deploy.bat   # Windows
```

### Manual Production Setup
1. Set `DEBUG=False` in settings
2. Configure PostgreSQL database
3. Set up Redis for caching
4. Configure Celery for background tasks
5. Set up Nginx reverse proxy
6. Configure SSL certificates

## 📚 API Documentation

### Authentication
- **Session Authentication**: For web interface
- **Token Authentication**: For API access

### Key Endpoints
- `GET /api/parts/` - List all parts
- `GET /api/parts/{id}/` - Get part details
- `GET /api/parts/qr/{qr_data}/` - Get part by QR code
- `GET /api/orders/` - List all orders
- `POST /api/scan-qr/` - Scan QR code

### Example API Usage
```bash
# Get all parts
curl http://127.0.0.1:8000/api/parts/

# Get part by QR code
curl http://127.0.0.1:8000/api/parts/qr/QRAIL_PART_12345_abc123/
```

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Solution: Use local settings with SQLite
   - Command: `python manage.py runserver --settings=qrail.settings_local`

2. **Missing Dependencies**
   - Solution: Activate virtual environment and install requirements
   - Commands:
     ```bash
     venv\Scripts\activate  # Windows
     pip install -r requirements.txt
     ```

3. **Migration Errors**
   - Solution: Delete database and recreate
   - Commands:
     ```bash
     del db.sqlite3  # Windows
     python manage.py makemigrations --settings=qrail.settings_local
     python manage.py migrate --settings=qrail.settings_local
     ```

4. **Static Files Not Loading**
   - Solution: Collect static files
   - Command: `python manage.py collectstatic --settings=qrail.settings_local`

### Getting Help
- Check Django logs in the console
- Use Django shell for debugging
- Check admin panel for data integrity
- Review the README.md for detailed documentation

## 🎉 You're All Set!

Your QRAIL Railway Parts Tracking System is now running successfully! 

**Next Steps:**
1. Explore the admin panel to create sample data
2. Test the QR scanner functionality
3. Create different user types and test permissions
4. Customize the system for your specific railway needs

**Happy Tracking! 🚂**
