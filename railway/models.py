"""
Railway management models for zones, divisions, and requirements.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

User = get_user_model()


class RailwayZone(models.Model):
    """
    Railway zones (e.g., Southern Railway, Eastern Railway, etc.)
    """
    zone_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    headquarters = models.CharField(max_length=200)
    jurisdiction = models.TextField(help_text="Geographical jurisdiction")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'railway_zones'
        verbose_name = 'Railway Zone'
        verbose_name_plural = 'Railway Zones'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.zone_code} - {self.name}"


class RailwayDivision(models.Model):
    """
    Railway divisions within zones
    """
    division_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    zone = models.ForeignKey(
        RailwayZone,
        on_delete=models.CASCADE,
        related_name='divisions'
    )
    headquarters = models.CharField(max_length=200)
    jurisdiction = models.TextField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'railway_divisions'
        verbose_name = 'Railway Division'
        verbose_name_plural = 'Railway Divisions'
        ordering = ['zone', 'name']
    
    def __str__(self):
        return f"{self.division_code} - {self.name} ({self.zone.name})"


class RailwayLocation(models.Model):
    """
    Railway locations/stations within divisions
    """
    location_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    division = models.ForeignKey(
        RailwayDivision,
        on_delete=models.CASCADE,
        related_name='locations'
    )
    location_type = models.CharField(
        max_length=20,
        choices=[
            ('STATION', 'Station'),
            ('JUNCTION', 'Junction'),
            ('YARD', 'Yard'),
            ('DEPOT', 'Depot'),
            ('SIGNAL_CABIN', 'Signal Cabin'),
            ('BRIDGE', 'Bridge'),
            ('TUNNEL', 'Tunnel'),
            ('OTHER', 'Other'),
        ],
        default='STATION'
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'railway_locations'
        verbose_name = 'Railway Location'
        verbose_name_plural = 'Railway Locations'
        ordering = ['division', 'name']
    
    def __str__(self):
        return f"{self.location_code} - {self.name} ({self.division.name})"


class Requirement(models.Model):
    """
    Railway requirements that can be created by Railway Authority
    """
    STATUS_CHOICES = [
        ('INACTIVE', 'Inactive'),
        ('ACTIVE', 'Active'),
        ('SHIPPED', 'Shipped'),
        ('RECEIVED', 'Received'),
        ('INSTALLED', 'Installed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    CURRENCY_CHOICES = [
        ('INR', 'Indian Rupee (INR)'),
        ('USD', 'US Dollar (USD)'),
        ('EUR', 'Euro (EUR)'),
        ('GBP', 'Pound Sterling (GBP)'),
        ('JPY', 'Japanese Yen (JPY)'),
    ]
    
    CATEGORY_CHOICES = [
        ('TRACK_CLIPS', 'Track Clips'),
        ('LINERS', 'Liners'),
        ('TRACK_PADS', 'Track Pads'),
    ]
    
    # Basic Information
    requirement_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES
    )
    
    # Location Information
    zone = models.ForeignKey(
        RailwayZone,
        on_delete=models.PROTECT,
        related_name='requirements'
    )
    division = models.ForeignKey(
        RailwayDivision,
        on_delete=models.PROTECT,
        related_name='requirements'
    )
    location = models.ForeignKey(
        RailwayLocation,
        on_delete=models.PROTECT,
        related_name='requirements',
        null=True,
        blank=True
    )
    track_section = models.CharField(max_length=100, blank=True)
    kilometer_marker = models.CharField(max_length=50, blank=True)
    
    # Specifications
    specifications = models.JSONField(
        default=dict,
        blank=True,
        help_text="Technical specifications in JSON format"
    )
    quantity = models.PositiveIntegerField(default=1)
    unit = models.CharField(max_length=50, default='pieces')
    
    # Timeline
    deadline_days = models.PositiveIntegerField(
        help_text="Number of days to complete the requirement"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deadline_date = models.DateTimeField(null=True, blank=True)
    
    # Status and Priority
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='INACTIVE'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    
    # Financial Information
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='INR'
    )
    
    # Assignment
    assigned_vendor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requirements',
        limit_choices_to={'user_type': 'VENDOR'}
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    
    # Management
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_requirements',
        limit_choices_to={'user_type': 'RAILWAY_AUTHORITY'}
    )
    
    # QR Code
    qr_code = models.ImageField(
        upload_to='qr_codes/requirements/',
        null=True,
        blank=True
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'requirements'
        verbose_name = 'Requirement'
        verbose_name_plural = 'Requirements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['requirement_id']),
            models.Index(fields=['status']),
            models.Index(fields=['zone', 'division']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.zone.name}"
    
    def save(self, *args, **kwargs):
        if not self.deadline_date and self.deadline_days:
            self.deadline_date = timezone.now() + timezone.timedelta(days=self.deadline_days)
        
        super().save(*args, **kwargs)
        
        # Generate QR code if not exists
        if not self.qr_code:
            self.generate_qr_code()
    
    def generate_qr_code(self):
        """
        Generate QR code for the requirement.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Use direct URL in QR code for immediate redirection
        qr_data = f"/railway/requirements/{self.requirement_id}/"
        
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code image
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        filename = f"qr_requirement_{self.requirement_id}.png"
        self.qr_code.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=False
        )
        self.save(update_fields=['qr_code'])
    
    def get_days_remaining(self):
        """
        Get number of days remaining until deadline.
        """
        if not self.deadline_date:
            return None
        
        now = timezone.now()
        if now >= self.deadline_date:
            return 0
        
        delta = self.deadline_date - now
        return delta.days
    
    def is_overdue(self):
        """
        Check if requirement is overdue.
        """
        if not self.deadline_date:
            return False
        return timezone.now() > self.deadline_date and self.status not in ['COMPLETED', 'CANCELLED']


class VendorRequest(models.Model):
    """
    Vendor requests for requirements (bidding system)
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    requirement = models.ForeignKey(
        Requirement,
        on_delete=models.CASCADE,
        related_name='vendor_requests'
    )
    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vendor_requests',
        limit_choices_to={'user_type': 'VENDOR'}
    )
    
    # Proposal Details
    proposed_price = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    delivery_time_days = models.PositiveIntegerField(
        help_text="Proposed delivery time in days"
    )
    proposal_description = models.TextField()
    
    # Technical Details
    technical_specifications = models.JSONField(
        default=dict,
        blank=True,
        help_text="Technical specifications proposed by vendor"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Review Information
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_vendor_requests',
        limit_choices_to={'user_type': 'RAILWAY_AUTHORITY'}
    )
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vendor_requests'
        verbose_name = 'Vendor Request'
        verbose_name_plural = 'Vendor Requests'
        ordering = ['-created_at']
        unique_together = ['requirement', 'vendor']
    
    def __str__(self):
        return f"{self.requirement.title} - {self.vendor.get_full_name()}"


class RequirementInspection(models.Model):
    """
    Inspections at different stages of requirement fulfillment
    """
    INSPECTION_TYPES = [
        ('PRE_SHIPMENT', 'Pre-Shipment Inspection'),
        ('POST_DELIVERY', 'Post-Delivery Inspection'),
        ('PRE_INSTALLATION', 'Pre-Installation Inspection'),
        ('POST_INSTALLATION', 'Post-Installation Inspection'),
        ('FINAL', 'Final Inspection'),
    ]
    
    INSPECTION_RESULTS = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('CONDITIONAL_PASS', 'Conditional Pass'),
        ('REQUIRES_RETEST', 'Requires Retest'),
    ]
    
    requirement = models.ForeignKey(
        Requirement,
        on_delete=models.CASCADE,
        related_name='inspections'
    )
    inspection_type = models.CharField(
        max_length=20,
        choices=INSPECTION_TYPES
    )
    
    # Inspection Details
    inspected_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='conducted_requirement_inspections'
    )
    inspection_date = models.DateTimeField(default=timezone.now)
    result = models.CharField(
        max_length=20,
        choices=INSPECTION_RESULTS
    )
    
    # Findings
    findings = models.TextField()
    quality_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Quality rating out of 10"
    )
    issues_found = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    # Documentation
    photos = models.JSONField(
        default=list,
        blank=True,
        help_text="List of photo URLs taken during inspection"
    )
    documents = models.JSONField(
        default=list,
        blank=True,
        help_text="List of document URLs"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'requirement_inspections'
        verbose_name = 'Requirement Inspection'
        verbose_name_plural = 'Requirement Inspections'
        ordering = ['-inspection_date']
    
    def __str__(self):
        return f"{self.requirement.title} - {self.get_inspection_type_display()}"


class RequirementStatusHistory(models.Model):
    """
    Track status changes for requirements
    """
    requirement = models.ForeignKey(
        Requirement,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    from_status = models.CharField(
        max_length=20,
        choices=Requirement.STATUS_CHOICES,
        null=True,
        blank=True
    )
    to_status = models.CharField(
        max_length=20,
        choices=Requirement.STATUS_CHOICES
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )
    changed_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'requirement_status_history'
        verbose_name = 'Requirement Status History'
        verbose_name_plural = 'Requirement Status Histories'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.requirement.title}: {self.from_status} → {self.to_status}"
