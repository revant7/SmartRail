"""
Models for tracking and monitoring railway parts.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from parts.models import Part
from orders.models import PurchaseOrder

User = get_user_model()


class TrackingEvent(models.Model):
    """
    Track events and status changes for parts.
    """
    EVENT_TYPES = [
        ('MANUFACTURED', 'Manufactured'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('INSTALLED', 'Installed'),
        ('INSPECTED', 'Inspected'),
        ('MAINTENANCE', 'Maintenance'),
        ('REPAIR', 'Repair'),
        ('REPLACED', 'Replaced'),
        ('DECOMMISSIONED', 'Decommissioned'),
        ('LOCATION_CHANGE', 'Location Changed'),
        ('STATUS_CHANGE', 'Status Changed'),
    ]
    
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='tracking_events'
    )
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPES
    )
    description = models.TextField()
    
    # Location Information
    location = models.CharField(max_length=200)
    railway_zone = models.CharField(max_length=100, blank=True)
    railway_division = models.CharField(max_length=100, blank=True)
    track_section = models.CharField(max_length=100, blank=True)
    kilometer_marker = models.CharField(max_length=50, blank=True)
    
    # GPS Coordinates (if available)
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True
    )
    
    # Event Details
    event_date = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='recorded_events'
    )
    
    # Related Information
    related_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tracking_events'
    )
    
    # Additional Data
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional event data in JSON format"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tracking_events'
        verbose_name = 'Tracking Event'
        verbose_name_plural = 'Tracking Events'
        ordering = ['-event_date']
        indexes = [
            models.Index(fields=['part', 'event_date']),
            models.Index(fields=['event_type', 'event_date']),
            models.Index(fields=['location']),
        ]
    
    def __str__(self):
        return f"{self.part.part_number} - {self.get_event_type_display()} ({self.event_date})"


class InspectionRecord(models.Model):
    """
    Inspection records for parts.
    """
    INSPECTION_TYPES = [
        ('ROUTINE', 'Routine Inspection'),
        ('PERIODIC', 'Periodic Inspection'),
        ('PRE_INSTALLATION', 'Pre-Installation'),
        ('POST_INSTALLATION', 'Post-Installation'),
        ('DEFECT_INSPECTION', 'Defect Inspection'),
        ('SAFETY_INSPECTION', 'Safety Inspection'),
        ('QUALITY_INSPECTION', 'Quality Inspection'),
    ]
    
    INSPECTION_RESULTS = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('CONDITIONAL_PASS', 'Conditional Pass'),
        ('REQUIRES_ATTENTION', 'Requires Attention'),
    ]
    
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='inspection_records'
    )
    inspection_type = models.CharField(
        max_length=20,
        choices=INSPECTION_TYPES
    )
    inspection_date = models.DateTimeField(default=timezone.now)
    inspector = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='conducted_inspections'
    )
    
    # Inspection Results
    result = models.CharField(
        max_length=20,
        choices=INSPECTION_RESULTS
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Inspection score out of 100"
    )
    
    # Findings
    findings = models.TextField()
    recommendations = models.TextField(blank=True)
    defects_found = models.TextField(blank=True)
    
    # Next Actions
    next_inspection_date = models.DateField(null=True, blank=True)
    corrective_actions_required = models.BooleanField(default=False)
    corrective_actions = models.TextField(blank=True)
    
    # Documentation
    inspection_report = models.FileField(
        upload_to='inspections/reports/',
        null=True,
        blank=True
    )
    photos = models.JSONField(
        default=list,
        blank=True,
        help_text="List of photo URLs taken during inspection"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inspection_records'
        verbose_name = 'Inspection Record'
        verbose_name_plural = 'Inspection Records'
        ordering = ['-inspection_date']
    
    def __str__(self):
        return f"{self.part.part_number} - {self.get_inspection_type_display()} ({self.inspection_date})"


class QualityCheck(models.Model):
    """
    Quality checks for parts and orders.
    """
    CHECK_TYPES = [
        ('INCOMING', 'Incoming Quality Check'),
        ('IN_PROCESS', 'In-Process Quality Check'),
        ('FINAL', 'Final Quality Check'),
        ('RANDOM', 'Random Quality Check'),
        ('CUSTOMER_COMPLAINT', 'Customer Complaint Check'),
    ]
    
    CHECK_STATUS = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('PASSED', 'Passed'),
        ('FAILED', 'Failed'),
        ('REQUIRES_RETEST', 'Requires Retest'),
    ]
    
    # Basic Information
    check_number = models.CharField(max_length=50, unique=True)
    check_type = models.CharField(
        max_length=20,
        choices=CHECK_TYPES
    )
    status = models.CharField(
        max_length=20,
        choices=CHECK_STATUS,
        default='PENDING'
    )
    
    # Related Objects
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='quality_checks'
    )
    order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='quality_checks'
    )
    
    # Check Details
    check_date = models.DateTimeField(default=timezone.now)
    checked_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='conducted_quality_checks'
    )
    
    # Results
    passed = models.BooleanField(null=True, blank=True)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    remarks = models.TextField(blank=True)
    
    # Non-conformities
    non_conformities = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    preventive_actions = models.TextField(blank=True)
    
    # Documentation
    test_results = models.JSONField(
        default=dict,
        blank=True,
        help_text="Test results in JSON format"
    )
    certificates = models.JSONField(
        default=list,
        blank=True,
        help_text="List of certificate URLs"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quality_checks'
        verbose_name = 'Quality Check'
        verbose_name_plural = 'Quality Checks'
        ordering = ['-check_date']
    
    def __str__(self):
        return f"{self.check_number} - {self.get_check_type_display()}"


class Alert(models.Model):
    """
    System alerts and notifications.
    """
    ALERT_TYPES = [
        ('MAINTENANCE_DUE', 'Maintenance Due'),
        ('INSPECTION_DUE', 'Inspection Due'),
        ('WARRANTY_EXPIRING', 'Warranty Expiring'),
        ('PART_FAILURE', 'Part Failure'),
        ('QUALITY_ISSUE', 'Quality Issue'),
        ('DELIVERY_DELAY', 'Delivery Delay'),
        ('BUDGET_EXCEEDED', 'Budget Exceeded'),
        ('SYSTEM_ERROR', 'System Error'),
    ]
    
    ALERT_PRIORITIES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    ALERT_STATUS = [
        ('ACTIVE', 'Active'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('RESOLVED', 'Resolved'),
        ('DISMISSED', 'Dismissed'),
    ]
    
    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPES
    )
    priority = models.CharField(
        max_length=10,
        choices=ALERT_PRIORITIES,
        default='MEDIUM'
    )
    status = models.CharField(
        max_length=15,
        choices=ALERT_STATUS,
        default='ACTIVE'
    )
    
    # Alert Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related Objects
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )
    order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )
    
    # Target Users
    target_users = models.ManyToManyField(
        User,
        blank=True,
        related_name='targeted_alerts'
    )
    
    # Alert Management
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_alerts'
    )
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Timing
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Additional Data
    metadata = models.JSONField(
        default=dict,
        blank=True
    )
    
    class Meta:
        db_table = 'alerts'
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['alert_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.title}"
    
    def acknowledge(self, user):
        """
        Acknowledge the alert.
        """
        self.status = 'ACKNOWLEDGED'
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.save()
    
    def resolve(self):
        """
        Mark alert as resolved.
        """
        self.status = 'RESOLVED'
        self.resolved_at = timezone.now()
        self.save()


class AuditLog(models.Model):
    """
    Audit log for tracking system changes.
    """
    ACTION_TYPES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action_type = models.CharField(
        max_length=10,
        choices=ACTION_TYPES
    )
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    
    # Change Details
    old_values = models.JSONField(
        default=dict,
        blank=True
    )
    new_values = models.JSONField(
        default=dict,
        blank=True
    )
    
    # Request Information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['action_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.get_action_type_display()} {self.model_name} ({self.timestamp})"
