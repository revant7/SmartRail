"""
User models for the QRAIL system.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    """
    USER_TYPE_CHOICES = [
        ('RAILWAY_AUTHORITY', 'Railway Authority'),
        ('VENDOR', 'Vendor'),
        ('RAILWAY_WORKER', 'Railway Worker'),
        ('SOFTWARE_STAFF', 'Software Staff/Moderator'),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='VENDOR',
        help_text="Type of user in the system"
    )
    
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9]+$',
            message='Employee ID must contain only uppercase letters and numbers'
        )],
        help_text="Unique employee identification number"
    )
    
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.'
        )],
        help_text="Contact phone number"
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text="Department or division within the organization"
    )
    
    designation = models.CharField(
        max_length=100,
        blank=True,
        help_text="Job title or designation"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether the user account has been verified"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip() or self.username
    
    def is_railway_authority(self):
        return self.user_type == 'RAILWAY_AUTHORITY'
    
    def is_railway_worker(self):
        return self.user_type == 'RAILWAY_WORKER'
    
    def is_vendor(self):
        return self.user_type == 'VENDOR'
    
    def is_software_staff(self):
        return self.user_type == 'SOFTWARE_STAFF' or self.is_superuser


class UserProfile(models.Model):
    """
    Extended profile information for users.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    profile_picture = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True,
        help_text="User profile picture"
    )
    
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief description about the user"
    )
    
    address = models.TextField(
        blank=True,
        help_text="Physical address"
    )
    
    emergency_contact = models.CharField(
        max_length=15,
        blank=True,
        help_text="Emergency contact phone number"
    )
    
    # Railway Authority specific fields
    authority_level = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('ZONAL', 'Zonal Authority'),
            ('DIVISIONAL', 'Divisional Authority'),
            ('REGIONAL', 'Regional Authority'),
            ('NATIONAL', 'National Authority'),
        ],
        help_text="Authority level for railway authorities"
    )
    
    jurisdiction = models.CharField(
        max_length=200,
        blank=True,
        help_text="Geographical jurisdiction or area of responsibility"
    )
    
    # Vendor specific fields
    company_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Company name for vendors"
    )
    
    company_registration = models.CharField(
        max_length=50,
        blank=True,
        help_text="Company registration number"
    )
    
    vendor_category = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ('TRACK_COMPONENTS', 'Track Components'),
            ('SIGNALING', 'Signaling Equipment'),
            ('ELECTRICAL', 'Electrical Equipment'),
            ('MECHANICAL', 'Mechanical Equipment'),
            ('SAFETY', 'Safety Equipment'),
            ('GENERAL', 'General Supplies'),
        ],
        help_text="Category of vendor business"
    )
    
    # Employee specific fields
    railway_zone = models.CharField(
        max_length=100,
        blank=True,
        help_text="Railway zone for employees"
    )
    
    railway_division = models.CharField(
        max_length=100,
        blank=True,
        help_text="Railway division for employees"
    )
    
    work_location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Current work location"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Profile"


class UserSession(models.Model):
    """
    Track user sessions for security and analytics.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_time = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
