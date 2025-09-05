"""
Forms for orders management.
"""
from django import forms
from django.forms import inlineformset_factory
from .models import Project, Vendor, PurchaseOrder, OrderLineItem


class ProjectForm(forms.ModelForm):
    """
    Form for creating and updating projects.
    """
    class Meta:
        model = Project
        fields = [
            'project_code', 'name', 'description', 'project_type',
            'status', 'railway_zone', 'railway_division', 'location',
            'start_date', 'expected_end_date', 'budget', 'currency',
            'project_manager'
        ]
        widgets = {
            'project_code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'project_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'railway_zone': forms.TextInput(attrs={'class': 'form-control'}),
            'railway_division': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'project_manager': forms.Select(attrs={'class': 'form-control'}),
        }


class VendorForm(forms.ModelForm):
    """
    Form for creating and updating vendors.
    """
    class Meta:
        model = Vendor
        fields = [
            'vendor_code', 'company_name', 'contact_person', 'email',
            'phone', 'address', 'vendor_type', 'status',
            'registration_number', 'tax_id', 'website',
            'specializations'
        ]
        widgets = {
            'vendor_code': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vendor_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'specializations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class PurchaseOrderForm(forms.ModelForm):
    """
    Form for creating and updating purchase orders.
    """
    class Meta:
        model = PurchaseOrder
        fields = [
            'project', 'vendor', 'priority', 'delivery_address',
            'expected_delivery_date', 'payment_terms', 'delivery_terms',
            'warranty_period'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'vendor': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'delivery_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'expected_delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control'}),
            'delivery_terms': forms.TextInput(attrs={'class': 'form-control'}),
            'warranty_period': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class OrderLineItemForm(forms.ModelForm):
    """
    Form for order line items.
    """
    class Meta:
        model = OrderLineItem
        fields = [
            'part_number', 'part_name', 'part_description',
            'manufacturer', 'quantity', 'unit_price',
            'expected_delivery_date', 'notes'
        ]
        widgets = {
            'part_number': forms.TextInput(attrs={'class': 'form-control'}),
            'part_name': forms.TextInput(attrs={'class': 'form-control'}),
            'part_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'expected_delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


# Create formset for line items
OrderLineItemFormSet = inlineformset_factory(
    PurchaseOrder,
    OrderLineItem,
    form=OrderLineItemForm,
    extra=1,
    can_delete=True,
    fields=[
        'part_number', 'part_name', 'part_description',
        'manufacturer', 'quantity', 'unit_price',
        'expected_delivery_date', 'notes'
    ]
)


class OrderSearchForm(forms.Form):
    """
    Form for searching orders.
    """
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by order number, vendor, or project...'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + PurchaseOrder.ORDER_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + PurchaseOrder.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    vendor = forms.ModelChoiceField(
        queryset=Vendor.objects.filter(status='ACTIVE'),
        required=False,
        empty_label="All Vendors",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        required=False,
        empty_label="All Projects",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
