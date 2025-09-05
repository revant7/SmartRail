"""
Models for railway parts management.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

User = get_user_model()


class PartCategory(models.Model):
    """
    Categories for railway parts.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'part_categories'
        verbose_name = 'Part Category'
        verbose_name_plural = 'Part Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PartSpecification(models.Model):
    """
    Technical specifications for parts.
    """
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=200)
    unit = models.CharField(max_length=50, blank=True)
    part = models.ForeignKey(
        'Part',
        on_delete=models.CASCADE,
        related_name='specifications'
    )
    
    class Meta:
        db_table = 'part_specifications'
        verbose_name = 'Part Specification'
        verbose_name_plural = 'Part Specifications'
        unique_together = ['part', 'name']
    
    def __str__(self):
        return f"{self.part.name} - {self.name}: {self.value} {self.unit}"


class Part(models.Model):
    """
    Railway parts model with QR code integration.
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('DISCONTINUED', 'Discontinued'),
        ('UNDER_REVIEW', 'Under Review'),
    ]
    
    # Basic Information
    part_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        PartCategory,
        on_delete=models.PROTECT,
        related_name='parts'
    )
    
    # Technical Details
    manufacturer = models.CharField(max_length=200)
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    material = models.CharField(max_length=100, blank=True)
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Weight in kilograms"
    )
    dimensions = models.CharField(max_length=200, blank=True)
    
    # Status and Lifecycle
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    installation_date = models.DateField(null=True, blank=True)
    expected_lifespan = models.IntegerField(
        null=True,
        blank=True,
        help_text="Expected lifespan in months"
    )
    last_inspection_date = models.DateField(null=True, blank=True)
    next_inspection_date = models.DateField(null=True, blank=True)
    
    # Location Information
    current_location = models.CharField(max_length=200, blank=True)
    railway_zone = models.CharField(max_length=100, blank=True)
    railway_division = models.CharField(max_length=100, blank=True)
    track_section = models.CharField(max_length=100, blank=True)
    kilometer_marker = models.CharField(max_length=50, blank=True)
    
    # QR Code and Identification
    qr_code = models.ImageField(
        upload_to='qr_codes/',
        null=True,
        blank=True
    )
    qr_code_data = models.CharField(max_length=500, unique=True)
    
    # Financial Information
    unit_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(max_length=3, default='INR')
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_parts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='updated_parts',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'parts'
        verbose_name = 'Part'
        verbose_name_plural = 'Parts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['part_number']),
            models.Index(fields=['qr_code_data']),
            models.Index(fields=['status']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.part_number} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.qr_code_data:
            self.qr_code_data = f"QRAIL_PART_{self.part_number}_{uuid.uuid4().hex[:8]}"
        
        super().save(*args, **kwargs)
        
        # Generate QR code if not exists
        if not self.qr_code:
            self.generate_qr_code()
    
    def generate_qr_code(self):
        """
        Generate QR code for the part.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # QR code data includes part info and API endpoint
        qr_data = {
            'type': 'railway_part',
            'part_number': self.part_number,
            'qr_code_data': self.qr_code_data,
            'api_endpoint': f'/api/parts/{self.id}/',
            'name': self.name,
            'manufacturer': self.manufacturer
        }
        
        qr.add_data(str(qr_data))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code image
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        filename = f"qr_{self.part_number}_{self.qr_code_data[:8]}.png"
        self.qr_code.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=False
        )
        self.save(update_fields=['qr_code'])
    
    def get_absolute_url(self):
        return f"/parts/{self.id}/"
    
    def is_due_for_inspection(self):
        """
        Check if part is due for inspection.
        """
        if not self.next_inspection_date:
            return False
        return timezone.now().date() >= self.next_inspection_date
    
    def get_age_in_months(self):
        """
        Get age of part in months.
        """
        if not self.installation_date:
            return None
        
        today = timezone.now().date()
        delta = today - self.installation_date
        return delta.days // 30


class PartImage(models.Model):
    """
    Images associated with parts.
    """
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='parts/images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'part_images'
        verbose_name = 'Part Image'
        verbose_name_plural = 'Part Images'
        ordering = ['-is_primary', 'uploaded_at']
    
    def __str__(self):
        return f"{self.part.name} - {self.caption or 'Image'}"


class PartDocument(models.Model):
    """
    Documents associated with parts (manuals, certificates, etc.).
    """
    DOCUMENT_TYPES = [
        ('MANUAL', 'User Manual'),
        ('CERTIFICATE', 'Certificate'),
        ('WARRANTY', 'Warranty'),
        ('INSPECTION', 'Inspection Report'),
        ('MAINTENANCE', 'Maintenance Record'),
        ('OTHER', 'Other'),
    ]
    
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='parts/documents/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'part_documents'
        verbose_name = 'Part Document'
        verbose_name_plural = 'Part Documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.part.name} - {self.title}"


class PartMaintenanceRecord(models.Model):
    """
    Maintenance records for parts.
    """
    MAINTENANCE_TYPES = [
        ('ROUTINE', 'Routine Maintenance'),
        ('REPAIR', 'Repair'),
        ('REPLACEMENT', 'Replacement'),
        ('INSPECTION', 'Inspection'),
        ('CLEANING', 'Cleaning'),
        ('CALIBRATION', 'Calibration'),
    ]
    
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='maintenance_records'
    )
    maintenance_type = models.CharField(
        max_length=20,
        choices=MAINTENANCE_TYPES
    )
    description = models.TextField()
    performed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='performed_maintenance'
    )
    performed_date = models.DateTimeField(default=timezone.now)
    next_maintenance_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'part_maintenance_records'
        verbose_name = 'Part Maintenance Record'
        verbose_name_plural = 'Part Maintenance Records'
        ordering = ['-performed_date']
    
    def __str__(self):
        return f"{self.part.name} - {self.get_maintenance_type_display()} ({self.performed_date})"
