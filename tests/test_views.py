"""
Tests for views.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User
from parts.models import Part, PartCategory
from orders.models import Project, Vendor, PurchaseOrder

User = get_user_model()


class AuthenticationViewTest(TestCase):
    """Test authentication views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='RAILWAY_EMPLOYEE'
        )
    
    def test_login_view_get(self):
        """Test login view GET request."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_login_view_post_valid(self):
        """Test login view POST with valid credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('dashboard'))
    
    def test_login_view_post_invalid(self):
        """Test login view POST with invalid credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')
    
    def test_logout_view(self):
        """Test logout view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
    
    def test_register_view_get(self):
        """Test register view GET request."""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
    
    def test_register_view_post_valid(self):
        """Test register view POST with valid data."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '+1234567890',
            'user_type': 'RAILWAY_EMPLOYEE',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())


class DashboardViewTest(TestCase):
    """Test dashboard view."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='RAILWAY_EMPLOYEE'
        )
    
    def test_dashboard_authenticated(self):
        """Test dashboard view for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
    
    def test_dashboard_unauthenticated(self):
        """Test dashboard view for unauthenticated user."""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")


class PartViewTest(TestCase):
    """Test part views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='RAILWAY_EMPLOYEE'
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
    
    def test_part_list_authenticated(self):
        """Test part list view for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('part_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Part')
    
    def test_part_detail_authenticated(self):
        """Test part detail view for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('part_detail', args=[self.part.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Part')
    
    def test_part_create_authenticated(self):
        """Test part create view for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('part_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Part')
    
    def test_part_create_post(self):
        """Test part creation via POST."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('part_create'), {
            'part_number': 'PART002',
            'name': 'New Test Part',
            'description': 'New test part description',
            'category': self.category.id,
            'manufacturer': 'New Test Manufacturer'
        })
        self.assertRedirects(response, reverse('part_detail', args=[2]))
        self.assertTrue(Part.objects.filter(part_number='PART002').exists())


class OrderViewTest(TestCase):
    """Test order views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='RAILWAY_EMPLOYEE'
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
    
    def test_order_list_authenticated(self):
        """Test order list view for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Orders')
    
    def test_order_detail_authenticated(self):
        """Test order detail view for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('order_detail', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.order_number)
    
    def test_order_create_authenticated(self):
        """Test order create view for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('order_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Order')


class QRScannerViewTest(TestCase):
    """Test QR scanner views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='RAILWAY_EMPLOYEE'
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
    
    def test_qr_scanner_authenticated(self):
        """Test QR scanner view for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('qr_scanner'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'QR Code Scanner')
    
    def test_scan_qr_code_valid(self):
        """Test QR code scanning with valid data."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('scan_qr_code'), {
            'qr_data': self.part.qr_code_data
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['part']['part_number'], 'PART001')
    
    def test_scan_qr_code_invalid(self):
        """Test QR code scanning with invalid data."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('scan_qr_code'), {
            'qr_data': 'invalid_qr_data'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertFalse(data['success'])


class APITest(TestCase):
    """Test API endpoints."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='RAILWAY_EMPLOYEE'
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
    
    def test_api_part_list_authenticated(self):
        """Test API part list for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('api_part_list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)
    
    def test_api_part_detail_authenticated(self):
        """Test API part detail for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('api_part_detail', args=[self.part.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['part_number'], 'PART001')
    
    def test_api_part_by_qr_authenticated(self):
        """Test API part by QR code for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('api_part_by_qr', args=[self.part.qr_code_data]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['part_number'], 'PART001')
    
    def test_api_dashboard_stats_authenticated(self):
        """Test API dashboard stats for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('api_dashboard_stats'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('total_parts', data)
        self.assertEqual(data['total_parts'], 1)
