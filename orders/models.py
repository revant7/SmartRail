"""
Models for order management system.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Project(models.Model):
    """
    Railway projects for organizing orders.
    """
    PROJECT_STATUS_CHOICES = [
        ('PLANNING', 'Planning'),
        ('ACTIVE', 'Active'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PROJECT_TYPES = [
        ('NEW_CONSTRUCTION', 'New Construction'),
        ('MAINTENANCE', 'Maintenance'),
        ('UPGRADE', 'Upgrade'),
        ('REPAIR', 'Repair'),
        ('INSPECTION', 'Inspection'),
    ]
    
    project_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    project_type = models.CharField(
        max_length=20,
        choices=PROJECT_TYPES
    )
    status = models.CharField(
        max_length=20,
        choices=PROJECT_STATUS_CHOICES,
        default='PLANNING'
    )
    
    # Location Information
    railway_zone = models.CharField(max_length=100)
    railway_division = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    
    # Timeline
    start_date = models.DateField()
    expected_end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)
    
    # Budget
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(max_length=3, default='INR')
    
    # Project Management
    project_manager = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='managed_projects'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_projects'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'projects'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project_code} - {self.name}"
    
    def get_total_orders_value(self):
        """
        Get total value of all orders for this project.
        """
        return self.orders.aggregate(
            total=models.Sum('total_amount')
        )['total'] or 0


class Vendor(models.Model):
    """
    Vendor information for parts supply.
    """
    VENDOR_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
        ('BLACKLISTED', 'Blacklisted'),
    ]
    
    VENDOR_TYPES = [
        ('MANUFACTURER', 'Manufacturer'),
        ('SUPPLIER', 'Supplier'),
        ('DISTRIBUTOR', 'Distributor'),
        ('SERVICE_PROVIDER', 'Service Provider'),
    ]
    
    vendor_code = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    
    vendor_type = models.CharField(
        max_length=20,
        choices=VENDOR_TYPES,
        default='SUPPLIER'
    )
    status = models.CharField(
        max_length=20,
        choices=VENDOR_STATUS_CHOICES,
        default='ACTIVE'
    )
    
    # Business Information
    registration_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    
    # Performance Metrics
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)]
    )
    delivery_performance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Delivery performance percentage"
    )
    
    # Specializations
    specializations = models.TextField(
        blank=True,
        help_text="Comma-separated list of specializations"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_vendors'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vendors'
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
        ordering = ['company_name']
    
    def __str__(self):
        return f"{self.vendor_code} - {self.company_name}"


class PurchaseOrder(models.Model):
    """
    Purchase orders for parts.
    """
    ORDER_STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('SENT_TO_VENDOR', 'Sent to Vendor'),
        ('CONFIRMED', 'Confirmed by Vendor'),
        ('IN_PRODUCTION', 'In Production'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
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
    
    order_number = models.CharField(max_length=50, unique=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        related_name='orders'
    )
    
    # Order Details
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='DRAFT'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    
    # Financial Information
    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    tax_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    currency = models.CharField(max_length=3, default='INR')
    
    # Delivery Information
    delivery_address = models.TextField()
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Terms and Conditions
    payment_terms = models.CharField(max_length=100, blank=True)
    delivery_terms = models.CharField(max_length=100, blank=True)
    warranty_period = models.IntegerField(
        null=True,
        blank=True,
        help_text="Warranty period in months"
    )
    
    # Management
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_orders'
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='approved_orders',
        null=True,
        blank=True
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'purchase_orders'
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.vendor.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"PO-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """
        Calculate order totals from line items.
        """
        line_items = self.line_items.all()
        self.subtotal = sum(item.total_price for item in line_items)
        self.total_amount = self.subtotal + self.tax_amount
        self.save(update_fields=['subtotal', 'total_amount'])


class OrderLineItem(models.Model):
    """
    Individual items in a purchase order.
    """
    order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='line_items'
    )
    
    # Part Information
    part_number = models.CharField(max_length=50)
    part_name = models.CharField(max_length=200)
    part_description = models.TextField(blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    
    # Quantity and Pricing
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    total_price = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )
    
    # Delivery Information
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=PurchaseOrder.ORDER_STATUS_CHOICES,
        default='DRAFT'
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'order_line_items'
        verbose_name = 'Order Line Item'
        verbose_name_plural = 'Order Line Items'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.part_name} (Qty: {self.quantity})"
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Update order totals
        self.order.calculate_totals()


class OrderDocument(models.Model):
    """
    Documents associated with orders.
    """
    DOCUMENT_TYPES = [
        ('QUOTATION', 'Quotation'),
        ('PURCHASE_ORDER', 'Purchase Order'),
        ('INVOICE', 'Invoice'),
        ('DELIVERY_CHALLAN', 'Delivery Challan'),
        ('RECEIPT', 'Receipt'),
        ('WARRANTY', 'Warranty Certificate'),
        ('OTHER', 'Other'),
    ]
    
    order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPES
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='orders/documents/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'order_documents'
        verbose_name = 'Order Document'
        verbose_name_plural = 'Order Documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.title}"


class OrderStatusHistory(models.Model):
    """
    Track status changes for orders.
    """
    order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    from_status = models.CharField(
        max_length=20,
        choices=PurchaseOrder.ORDER_STATUS_CHOICES,
        null=True,
        blank=True
    )
    to_status = models.CharField(
        max_length=20,
        choices=PurchaseOrder.ORDER_STATUS_CHOICES
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )
    changed_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'order_status_history'
        verbose_name = 'Order Status History'
        verbose_name_plural = 'Order Status Histories'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.order.order_number}: {self.from_status} → {self.to_status}"
