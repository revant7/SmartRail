"""
Core models for the QRAIL system.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class SystemConfiguration(models.Model):
    """
    System-wide configuration settings.
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('STRING', 'String'),
            ('INTEGER', 'Integer'),
            ('BOOLEAN', 'Boolean'),
            ('JSON', 'JSON'),
            ('FLOAT', 'Float'),
        ],
        default='STRING'
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Whether this setting can be accessed by non-admin users"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_configurations'
        verbose_name = 'System Configuration'
        verbose_name_plural = 'System Configurations'
    
    def __str__(self):
        return f"{self.key}: {self.value}"


class QRCodeScan(models.Model):
    """
    Track QR code scans for analytics and security.
    """
    qr_code_data = models.CharField(max_length=500)
    scanned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    scan_result = models.JSONField(
        default=dict,
        blank=True,
        help_text="Result of the scan (part found, error, etc.)"
    )
    scan_timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'qr_code_scans'
        verbose_name = 'QR Code Scan'
        verbose_name_plural = 'QR Code Scans'
        ordering = ['-scan_timestamp']
        indexes = [
            models.Index(fields=['qr_code_data', 'scan_timestamp']),
            models.Index(fields=['scanned_by', 'scan_timestamp']),
        ]
    
    def __str__(self):
        return f"Scan: {self.qr_code_data[:20]}... by {self.scanned_by or 'Anonymous'}"


class DashboardWidget(models.Model):
    """
    Dashboard widgets configuration for users.
    """
    WIDGET_TYPES = [
        ('CHART', 'Chart'),
        ('TABLE', 'Table'),
        ('METRIC', 'Metric'),
        ('ALERT', 'Alert'),
        ('CALENDAR', 'Calendar'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dashboard_widgets'
    )
    widget_type = models.CharField(
        max_length=10,
        choices=WIDGET_TYPES
    )
    title = models.CharField(max_length=100)
    configuration = models.JSONField(
        default=dict,
        help_text="Widget configuration in JSON format"
    )
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=4)
    height = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_widgets'
        verbose_name = 'Dashboard Widget'
        verbose_name_plural = 'Dashboard Widgets'
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
