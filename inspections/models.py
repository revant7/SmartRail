"""
Online inspection models for railway manufacturing stages.
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from parts.models import Part
from orders.models import PurchaseOrder
from railway.models import Requirement
import uuid

User = get_user_model()


class InspectionStage(models.Model):
    """
    Different stages of manufacturing and supply chain where inspections occur.
    """
    STAGE_TYPES = [
        ('MANUFACTURING', 'Manufacturing Stage'),
        ('SUPPLY', 'Supply Stage'),
        ('RECEIVING', 'Receiving Stage'),
        ('FITTING', 'Fitting/Track Installation Stage'),
        ('FINAL', 'Final Inspection Stage'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    stage_type = models.CharField(
        max_length=20,
        choices=STAGE_TYPES
    )
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    # Required participants for this stage
    requires_vendor = models.BooleanField(default=False)
    requires_receiver = models.BooleanField(default=False)
    requires_railway_auth = models.BooleanField(default=False)
    requires_worker = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inspection_stages'
        verbose_name = 'Inspection Stage'
        verbose_name_plural = 'Inspection Stages'
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_stage_type_display()})"


class EquipmentBatch(models.Model):
    """
    Equipment batch tracking with UUID for QR code scanning.
    """
    batch_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    batch_number = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Unique batch number for this equipment batch")
    batch_name = models.CharField(max_length=200)
    equipment_type = models.CharField(
        max_length=100,
        choices=[
            ('LINERS', 'Liners'),
            ('PADS', 'Pads'),
            ('CLIPS', 'Clips'),
        ]
    )
    manufacturer = models.CharField(max_length=200, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    manufacturing_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    
    # Related Objects - requirement is now required for new records
    requirement = models.ForeignKey(
        Requirement,
        on_delete=models.CASCADE,
        related_name='equipment_batches',
        null=True,  # For backward compatibility with existing records
        blank=False
    )
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='equipment_batches',
        null=True,
        blank=True
    )
    
    # Status tracking
    current_stage = models.CharField(
        max_length=20,
        choices=[
            ('MANUFACTURING', 'Manufacturing'),
            ('SUPPLY', 'Supply'),
            ('RECEIVING', 'Receiving'),
            ('FITTING', 'Fitting/Installation'),
            ('FINAL', 'Final Inspection'),
            ('COMPLETED', 'Completed'),
        ],
        default='MANUFACTURING'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'equipment_batches'
        verbose_name = 'Equipment Batch'
        verbose_name_plural = 'Equipment Batches'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.batch_name} ({self.batch_uuid})"


class OnlineInspection(models.Model):
    """
    Streamlined online inspection records for equipment batches.
    """
    INSPECTION_STATUS = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    INSPECTION_RESULTS = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('CONDITIONAL_PASS', 'Conditional Pass'),
        ('REQUIRES_RETEST', 'Requires Retest'),
    ]
    
    INSPECTION_SOURCES = [
        ('VENDOR', 'Vendor Side'),
        ('RAILWAY_AUTH', 'Railway Authority Side'),
        ('WORKER', 'Worker Side'),
    ]
    
    # Basic Information
    inspection_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    equipment_batch = models.ForeignKey(
        EquipmentBatch,
        on_delete=models.CASCADE,
        related_name='inspections',
        null=True,
        blank=True
    )
    stage = models.ForeignKey(
        InspectionStage,
        on_delete=models.PROTECT,
        related_name='inspections'
    )
    inspection_source = models.CharField(
        max_length=20,
        choices=INSPECTION_SOURCES,
        help_text="Which side conducted this inspection",
        default='VENDOR'
    )
    
    # Related Objects (for backward compatibility)
    requirement = models.ForeignKey(
        Requirement,
        on_delete=models.CASCADE,
        related_name='online_inspections',
        null=True,
        blank=True
    )
    part = models.ForeignKey(
        Part,
        on_delete=models.CASCADE,
        related_name='online_inspections',
        null=True,
        blank=True
    )
    order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='online_inspections',
        null=True,
        blank=True
    )
    
    # Inspection Details
    status = models.CharField(
        max_length=20,
        choices=INSPECTION_STATUS,
        default='PENDING'
    )
    result = models.CharField(
        max_length=20,
        choices=INSPECTION_RESULTS,
        null=True,
        blank=True
    )
    
    # Quality Assessment
    quality_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Quality rating out of 10"
    )
    overall_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Overall inspection score out of 100"
    )
    
    # Findings and Notes
    findings = models.TextField(blank=True)
    issues_found = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    overview_notes = models.TextField(
        blank=True,
        help_text="Optional overview notes from inspector"
    )
    
    # Location Information
    inspection_location = models.CharField(max_length=200)
    railway_zone = models.CharField(max_length=100, blank=True)
    railway_division = models.CharField(max_length=100, blank=True)
    track_section = models.CharField(max_length=100, blank=True)
    kilometer_marker = models.CharField(max_length=50, blank=True)
    
    # GPS Coordinates
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
    
    # Participants
    vendor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendor_inspections',
        limit_choices_to={'user_type': 'VENDOR'}
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='receiver_inspections',
        limit_choices_to={'user_type': 'RAILWAY_AUTHORITY'}
    )
    railway_auth = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='railway_auth_inspections',
        limit_choices_to={'user_type': 'RAILWAY_AUTHORITY'}
    )
    worker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='worker_inspections',
        limit_choices_to={'user_type': 'RAILWAY_WORKER'}
    )
    
    # Timing
    inspection_date = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # AI Training Data
    ai_training_data_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="Data for AI model training"
    )
    ai_summary_generated = models.BooleanField(default=False)
    ai_summary_text = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'online_inspections'
        verbose_name = 'Online Inspection'
        verbose_name_plural = 'Online Inspections'
        ordering = ['-inspection_date']
        indexes = [
            models.Index(fields=['stage', 'status']),
            models.Index(fields=['requirement', 'stage']),
            models.Index(fields=['inspection_date']),
        ]
    
    def __str__(self):
        return f"{self.stage.name} - {self.requirement} ({self.get_status_display()})"
    
    def get_participants(self):
        """Get all participants in this inspection."""
        participants = []
        if self.vendor:
            participants.append(('Vendor', self.vendor))
        if self.receiver:
            participants.append(('Receiver', self.receiver))
        if self.railway_auth:
            participants.append(('Railway Authority', self.railway_auth))
        if self.worker:
            participants.append(('Worker', self.worker))
        return participants
    
    def is_complete(self):
        """Check if inspection is complete."""
        return self.status == 'COMPLETED'
    
    def can_be_completed(self):
        """Check if inspection can be completed based on required participants."""
        if not self.stage:
            return False
        
        # Check if all required participants are present
        if self.stage.requires_vendor and not self.vendor:
            return False
        if self.stage.requires_receiver and not self.receiver:
            return False
        if self.stage.requires_railway_auth and not self.railway_auth:
            return False
        if self.stage.requires_worker and not self.worker:
            return False
        
        return True


class InspectionPhoto(models.Model):
    """
    Photos uploaded during streamlined inspections with QR code scanning.
    """
    PHOTO_TYPES = [
        ('EQUIPMENT_OVERVIEW', 'Equipment Overview'),
        ('EQUIPMENT_DETAIL', 'Equipment Detail'),
        ('QR_CODE', 'QR Code Scan'),
        ('DEFECT', 'Defect Found'),
        ('COMPLETION', 'Completion Photo'),
        ('DOCUMENT', 'Document Photo'),
        ('OTHER', 'Other'),
    ]
    
    inspection = models.ForeignKey(
        OnlineInspection,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    equipment_batch = models.ForeignKey(
        EquipmentBatch,
        on_delete=models.CASCADE,
        related_name='photos',
        null=True,
        blank=True
    )
    photo_type = models.CharField(
        max_length=20,
        choices=PHOTO_TYPES,
        default='EQUIPMENT_OVERVIEW'
    )
    image = models.ImageField(
        upload_to='inspections/photos/%Y/%m/%d/',
        help_text="Upload inspection photos"
    )
    caption = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    # QR Code Data (if this photo contains a QR code)
    qr_code_data = models.CharField(max_length=500, blank=True)
    qr_code_uuid = models.UUIDField(null=True, blank=True)
    
    # AI Analysis Data
    ai_analysis = models.JSONField(
        default=dict,
        blank=True,
        help_text="AI analysis results for this photo"
    )
    ai_tags = models.JSONField(
        default=list,
        blank=True,
        help_text="AI-generated tags for this photo"
    )
    ai_confidence_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="AI confidence score for this photo analysis"
    )
    
    # Upload Information
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='uploaded_inspection_photos'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # GPS Coordinates (if photo has location data)
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
    
    class Meta:
        db_table = 'inspection_photos'
        verbose_name = 'Inspection Photo'
        verbose_name_plural = 'Inspection Photos'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.inspection} - {self.get_photo_type_display()} ({self.uploaded_at})"


class InspectionDocument(models.Model):
    """
    Documents uploaded during online inspections.
    """
    DOCUMENT_TYPES = [
        ('CERTIFICATE', 'Certificate'),
        ('REPORT', 'Report'),
        ('MANUAL', 'Manual'),
        ('WARRANTY', 'Warranty'),
        ('TEST_RESULT', 'Test Result'),
        ('OTHER', 'Other'),
    ]
    
    inspection = models.ForeignKey(
        OnlineInspection,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES,
        default='OTHER'
    )
    title = models.CharField(max_length=200)
    file = models.FileField(
        upload_to='inspections/documents/%Y/%m/%d/',
        help_text="Upload inspection documents"
    )
    description = models.TextField(blank=True)
    
    # Upload Information
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='uploaded_inspection_documents'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inspection_documents'
        verbose_name = 'Inspection Document'
        verbose_name_plural = 'Inspection Documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.inspection} - {self.title}"


class InspectionChecklist(models.Model):
    """
    Checklist items for each inspection stage.
    """
    stage = models.ForeignKey(
        InspectionStage,
        on_delete=models.CASCADE,
        related_name='checklist_items'
    )
    item_text = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inspection_checklist'
        verbose_name = 'Inspection Checklist Item'
        verbose_name_plural = 'Inspection Checklist Items'
        ordering = ['stage', 'order']
    
    def __str__(self):
        return f"{self.stage.name} - {self.item_text[:50]}..."


class InspectionChecklistResponse(models.Model):
    """
    Responses to checklist items during inspections.
    """
    RESPONSE_TYPES = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('N/A', 'Not Applicable'),
        ('PENDING', 'Pending'),
    ]
    
    inspection = models.ForeignKey(
        OnlineInspection,
        on_delete=models.CASCADE,
        related_name='checklist_responses'
    )
    checklist_item = models.ForeignKey(
        InspectionChecklist,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    response = models.CharField(
        max_length=10,
        choices=RESPONSE_TYPES
    )
    notes = models.TextField(blank=True)
    photo = models.ForeignKey(
        InspectionPhoto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checklist_responses'
    )
    
    # Response Information
    responded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='checklist_responses'
    )
    responded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inspection_checklist_responses'
        verbose_name = 'Inspection Checklist Response'
        verbose_name_plural = 'Inspection Checklist Responses'
        unique_together = ['inspection', 'checklist_item']
        ordering = ['checklist_item__order']
    
    def __str__(self):
        return f"{self.inspection} - {self.checklist_item.item_text[:30]}... - {self.get_response_display()}"


class AITrainingData(models.Model):
    """
    Data collected for AI model training from inspections.
    """
    inspection = models.ForeignKey(
        OnlineInspection,
        on_delete=models.CASCADE,
        related_name='ai_training_records'
    )
    
    # Training Data
    stage_data = models.JSONField(
        default=dict,
        help_text="Stage-specific training data"
    )
    photo_analysis = models.JSONField(
        default=dict,
        help_text="Photo analysis data for AI training"
    )
    quality_metrics = models.JSONField(
        default=dict,
        help_text="Quality metrics for AI training"
    )
    defect_patterns = models.JSONField(
        default=dict,
        help_text="Defect patterns identified"
    )
    
    # AI Processing Status
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    ai_model_version = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_training_data'
        verbose_name = 'AI Training Data'
        verbose_name_plural = 'AI Training Data'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"AI Training Data - {self.inspection} ({self.created_at})"


class AISmartReport(models.Model):
    """
    AI-generated smart inspection reports for equipment batches.
    """
    REPORT_STATUS = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    equipment_batch = models.ForeignKey(
        EquipmentBatch,
        on_delete=models.CASCADE,
        related_name='ai_reports'
    )
    
    # Report Content
    executive_summary = models.TextField()
    quality_assessment = models.TextField()
    defect_analysis = models.JSONField(
        default=dict,
        help_text="Analysis of defects found across all inspection stages"
    )
    stage_comparison = models.JSONField(
        default=dict,
        help_text="Comparison of quality across different stages"
    )
    recommendations = models.JSONField(
        default=list,
        help_text="AI-generated recommendations"
    )
    risk_assessment = models.JSONField(
        default=dict,
        help_text="Risk assessment data"
    )
    compliance_status = models.JSONField(
        default=dict,
        help_text="Compliance status with standards"
    )
    
    # Data Sources
    vendor_inspections = models.JSONField(
        default=list,
        help_text="Data from vendor-side inspections"
    )
    railway_auth_inspections = models.JSONField(
        default=list,
        help_text="Data from railway authority inspections"
    )
    worker_inspections = models.JSONField(
        default=list,
        help_text="Data from worker-side inspections"
    )
    
    # AI Processing Information
    ai_model_version = models.CharField(max_length=50)
    confidence_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="AI confidence score (0-1)"
    )
    processing_time_seconds = models.IntegerField(null=True, blank=True)
    
    # Status and Timing
    status = models.CharField(
        max_length=20,
        choices=REPORT_STATUS,
        default='PENDING'
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_smart_reports'
        verbose_name = 'AI Smart Report'
        verbose_name_plural = 'AI Smart Reports'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"AI Smart Report - {self.equipment_batch} ({self.generated_at})"


class InspectionSummary(models.Model):
    """
    AI-generated summaries of individual inspections (legacy support).
    """
    inspection = models.OneToOneField(
        OnlineInspection,
        on_delete=models.CASCADE,
        related_name='ai_summary_record'
    )
    
    # Summary Content
    executive_summary = models.TextField()
    key_findings = models.JSONField(
        default=list,
        help_text="Key findings from the inspection"
    )
    quality_assessment = models.TextField()
    recommendations = models.JSONField(
        default=list,
        help_text="AI-generated recommendations"
    )
    risk_assessment = models.JSONField(
        default=dict,
        help_text="Risk assessment data"
    )
    
    # AI Processing Information
    ai_model_version = models.CharField(max_length=50)
    confidence_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="AI confidence score (0-1)"
    )
    
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inspection_summaries'
        verbose_name = 'Inspection Summary'
        verbose_name_plural = 'Inspection Summaries'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"AI Summary - {self.inspection} ({self.generated_at})"
