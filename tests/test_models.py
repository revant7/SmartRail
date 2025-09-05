"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from accounts.models import User, UserProfile
from parts.models import Part, PartCategory
from orders.models import Project, Vendor, PurchaseOrder
from tracking.models import TrackingEvent, Alert

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='RAILWAY_EMPLOYEE',
            employee_id='EMP001',
            phone_number='+1234567890'
        )
    
    def test_user_creation(self):
        """Test user creation."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.user_type, 'RAILWAY_EMPLOYEE')
        self.assertEqual(self.user.employee_id, 'EMP001')
    
    def test_user_full_name(self):
        """Test user full name method."""
        self.assertEqual(self.user.get_full_name(), 'Test User')
    
    def test_user_type_methods(self):
        """Test user type checking methods."""
        self.assertTrue(self.user.is_railway_employee())
        self.assertFalse(self.user.is_admin())
        self.assertFalse(self.user.is_vendor())


class PartModelTest(TestCase):
    """Test Part model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = PartCategory.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        self.part = Part.objects.create(
            part_number='PART001',
            name='Test Part',
            description='Test part description',
            category=self.category,
            manufacturer='Test Manufacturer',
            created_by=self.user
        )
    
    def test_part_creation(self):
        """Test part creation."""
        self.assertEqual(self.part.part_number, 'PART001')
        self.assertEqual(self.part.name, 'Test Part')
        self.assertEqual(self.part.manufacturer, 'Test Manufacturer')
        self.assertTrue(self.part.qr_code_data)
    
    def test_part_str_representation(self):
        """Test part string representation."""
        expected = f"{self.part.part_number} - {self.part.name}"
        self.assertEqual(str(self.part), expected)
    
    def test_qr_code_generation(self):
        """Test QR code generation."""
        # QR code should be generated automatically
        self.assertTrue(self.part.qr_code_data)
        self.assertIn('QRAIL_PART_', self.part.qr_code_data)


class ProjectModelTest(TestCase):
    """Test Project model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            project_code='PROJ001',
            name='Test Project',
            description='Test project description',
            project_type='NEW_CONSTRUCTION',
            railway_zone='Test Zone',
            railway_division='Test Division',
            location='Test Location',
            start_date='2024-01-01',
            project_manager=self.user,
            created_by=self.user
        )
    
    def test_project_creation(self):
        """Test project creation."""
        self.assertEqual(self.project.project_code, 'PROJ001')
        self.assertEqual(self.project.name, 'Test Project')
        self.assertEqual(self.project.project_type, 'NEW_CONSTRUCTION')
    
    def test_project_str_representation(self):
        """Test project string representation."""
        expected = f"{self.project.project_code} - {self.project.name}"
        self.assertEqual(str(self.project), expected)


class PurchaseOrderModelTest(TestCase):
    """Test PurchaseOrder model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.project = Project.objects.create(
            project_code='PROJ001',
            name='Test Project',
            description='Test project description',
            project_type='NEW_CONSTRUCTION',
            railway_zone='Test Zone',
            railway_division='Test Division',
            location='Test Location',
            start_date='2024-01-01',
            project_manager=self.user,
            created_by=self.user
        )
        
        self.vendor = Vendor.objects.create(
            vendor_code='VENDOR001',
            company_name='Test Vendor',
            contact_person='Test Contact',
            email='vendor@example.com',
            phone='+1234567890',
            address='Test Address',
            created_by=self.user
        )
        
        self.order = PurchaseOrder.objects.create(
            project=self.project,
            vendor=self.vendor,
            delivery_address='Test Delivery Address',
            created_by=self.user
        )
    
    def test_order_creation(self):
        """Test purchase order creation."""
        self.assertEqual(self.order.project, self.project)
        self.assertEqual(self.order.vendor, self.vendor)
        self.assertTrue(self.order.order_number)
        self.assertEqual(self.order.status, 'DRAFT')
    
    def test_order_number_generation(self):
        """Test automatic order number generation."""
        self.assertTrue(self.order.order_number)
        self.assertIn('PO-', self.order.order_number)


class TrackingEventModelTest(TestCase):
    """Test TrackingEvent model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = PartCategory.objects.create(
            name='Test Category',
            description='Test category description'
        )
        
        self.part = Part.objects.create(
            part_number='PART001',
            name='Test Part',
            description='Test part description',
            category=self.category,
            manufacturer='Test Manufacturer',
            created_by=self.user
        )
        
        self.event = TrackingEvent.objects.create(
            part=self.part,
            event_type='INSTALLED',
            description='Part installed at location',
            location='Test Location',
            recorded_by=self.user
        )
    
    def test_tracking_event_creation(self):
        """Test tracking event creation."""
        self.assertEqual(self.event.part, self.part)
        self.assertEqual(self.event.event_type, 'INSTALLED')
        self.assertEqual(self.event.location, 'Test Location')
    
    def test_tracking_event_str_representation(self):
        """Test tracking event string representation."""
        expected = f"{self.part.part_number} - Installed ({self.event.event_date})"
        self.assertEqual(str(self.event), expected)


class AlertModelTest(TestCase):
    """Test Alert model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.alert = Alert.objects.create(
            alert_type='MAINTENANCE_DUE',
            priority='HIGH',
            title='Test Alert',
            message='Test alert message',
            created_by=self.user
        )
    
    def test_alert_creation(self):
        """Test alert creation."""
        self.assertEqual(self.alert.alert_type, 'MAINTENANCE_DUE')
        self.assertEqual(self.alert.priority, 'HIGH')
        self.assertEqual(self.alert.status, 'ACTIVE')
    
    def test_alert_acknowledge(self):
        """Test alert acknowledgment."""
        self.alert.acknowledge(self.user)
        self.assertEqual(self.alert.status, 'ACKNOWLEDGED')
        self.assertEqual(self.alert.acknowledged_by, self.user)
    
    def test_alert_resolve(self):
        """Test alert resolution."""
        self.alert.resolve()
        self.assertEqual(self.alert.status, 'RESOLVED')
