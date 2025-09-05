# Online Inspection System for Railway Manufacturing

## Overview

The Online Inspection System is a comprehensive Django-based application designed to manage inspections at every stage of railway manufacturing, supply, receiving, and fitting processes. The system enables vendors, receivers, railway authorities, and workers to conduct online inspections with photo uploads, document management, and AI-ready data collection.

## Features

### 🏗️ **Multi-Stage Inspection Support**
- **Manufacturing Stage**: Quality control during production
- **Supply Stage**: Pre-delivery inspection and packaging verification
- **Receiving Stage**: Post-delivery inspection at railway facilities
- **Fitting/Track Installation Stage**: Installation and assembly verification
- **Final Inspection Stage**: Comprehensive final quality assessment

### 📸 **Photo Management**
- Multiple photo upload (bulk and individual)
- Photo categorization (overview, detail, issue, completion, document)
- GPS coordinate capture for photos
- AI analysis integration ready
- Photo gallery with management capabilities

### 📋 **Configurable Checklist System**
- Stage-specific checklist items
- Required/optional item designation
- Interactive response system
- Photo attachments for checklist items
- Progress tracking and validation

### 👥 **Role-Based Access Control**
- **Vendors**: Can create and manage inspections for their products
- **Receivers**: Can conduct receiving inspections
- **Railway Authority**: Can oversee all inspections and manage stages
- **Workers**: Can perform fitting and installation inspections

### 🤖 **AI Integration Ready**
- Structured data collection for AI model training
- Photo analysis data storage
- Quality metrics and defect pattern tracking
- AI summary generation framework
- Confidence scoring system

## System Architecture

### Models

1. **InspectionStage**: Defines different inspection stages and their requirements
2. **OnlineInspection**: Main inspection record with status, results, and participants
3. **InspectionPhoto**: Photo management with AI analysis support
4. **InspectionDocument**: Document upload and categorization
5. **InspectionChecklist**: Configurable checklist items per stage
6. **InspectionChecklistResponse**: User responses to checklist items
7. **AITrainingData**: Structured data for AI model training
8. **InspectionSummary**: AI-generated summaries and recommendations

### Key Features

- **Multi-participant Support**: Each stage can require specific participants
- **Quality Assessment**: 0-10 quality rating and 0-100 overall scoring
- **Location Tracking**: GPS coordinates and railway location data
- **Document Management**: Multiple document types with metadata
- **Progress Tracking**: Real-time status updates and completion validation
- **Data Export**: AI-ready data collection for machine learning

## Installation & Setup

### Prerequisites
- Django 4.2+
- Python 3.8+
- PostgreSQL (recommended) or SQLite
- Virtual environment

### Installation Steps

1. **Activate Virtual Environment**
   ```bash
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations**
   ```bash
   python manage.py makemigrations inspections
   python manage.py migrate
   ```

4. **Create Default Inspection Stages**
   ```bash
   python manage.py create_inspection_stages
   ```

5. **Create Sample Checklist Items**
   ```bash
   python manage.py create_sample_checklist
   ```

6. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

## Usage Guide

### For Vendors

1. **Access Inspections**: Navigate to "Online Inspections" in the sidebar
2. **Create Inspection**: Click "Create Inspection" and select "Manufacturing Stage"
3. **Upload Photos**: Add photos of the manufacturing process and quality checks
4. **Complete Checklist**: Respond to all required checklist items
5. **Submit for Review**: Complete the inspection for railway authority review

### For Railway Authority

1. **Manage Stages**: Access "Inspection Stages" to configure requirements
2. **Oversee Inspections**: View all inspections across all stages
3. **Review Results**: Analyze inspection data and quality metrics
4. **Generate Reports**: Export inspection data for analysis

### For Workers

1. **Installation Inspections**: Create inspections for "Fitting/Track Installation Stage"
2. **Photo Documentation**: Upload photos of installation process
3. **Quality Verification**: Complete checklist items for installation quality
4. **Final Inspection**: Conduct final comprehensive inspection

## API Endpoints

### Inspection Management
- `GET /inspections/` - Dashboard view
- `GET /inspections/list/` - List all inspections
- `POST /inspections/create/` - Create new inspection
- `GET /inspections/{id}/` - View inspection details
- `POST /inspections/{id}/edit/` - Update inspection
- `POST /inspections/{id}/complete/` - Complete inspection

### Photo & Document Upload
- `POST /inspections/{id}/photos/` - Upload multiple photos
- `POST /inspections/{id}/documents/` - Upload documents
- `POST /inspections/api/{id}/upload-photo/` - AJAX single photo upload
- `DELETE /inspections/api/photo/{id}/delete/` - Delete photo

### Checklist Management
- `POST /inspections/{id}/checklist/{item_id}/` - Respond to checklist item
- `GET /inspections/stages/` - Manage inspection stages

## Data Collection for AI Training

The system collects comprehensive data for AI model training:

### Structured Data
- Inspection results and quality metrics
- Stage-specific process information
- Participant information and roles
- Location and environmental data

### Visual Data
- Categorized photos with metadata
- GPS coordinates for location context
- Photo analysis tags and descriptions

### Process Data
- Checklist responses and notes
- Quality ratings and scores
- Defect patterns and issues found
- Recommendations and corrective actions

## AI Integration

### Current Capabilities
- Structured data collection
- Photo metadata and categorization
- Quality metrics tracking
- Defect pattern identification

### Future AI Features
- Automated photo analysis
- Defect detection from images
- Predictive quality assessment
- Automated summary generation
- Risk assessment and recommendations

## Configuration

### Inspection Stages
Configure stages in Django Admin or via the web interface:
- Set required participants for each stage
- Define stage-specific checklist items
- Configure quality requirements

### User Permissions
- Vendors: Can create and manage their own inspections
- Railway Authority: Full access to all inspections
- Workers: Can perform assigned inspections
- Software Staff: Administrative access

## Troubleshooting

### Common Issues

1. **Template Not Found**: Ensure all template files are in the correct directory
2. **Permission Denied**: Check user roles and permissions
3. **Photo Upload Fails**: Verify file size limits and formats
4. **Database Errors**: Run migrations and check database connectivity

### Debug Mode
Enable debug mode in settings for detailed error information:
```python
DEBUG = True
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is part of the QRAIL Railway Management System.

## Support

For technical support or questions about the inspection system, please contact the development team or create an issue in the project repository.

---

**Note**: This system is designed to be AI-ready and will collect data that can be used for training machine learning models to provide automated analysis, defect detection, and quality assessment in future versions.
