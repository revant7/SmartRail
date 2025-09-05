"""
Forms for railway management.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    RailwayZone, RailwayDivision, RailwayLocation, Requirement, 
    VendorRequest, RequirementInspection
)


class RequirementForm(forms.ModelForm):
    """
    Form for creating and editing requirements.
    """
    class Meta:
        model = Requirement
        fields = [
            'title', 'description', 'category', 'zone', 'division',
            'location', 'track_section', 'kilometer_marker',
            'specifications', 'quantity', 'unit', 'deadline_days',
            'priority', 'budget', 'currency'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter requirement title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter detailed description'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'zone': forms.Select(attrs={'class': 'form-control'}),
            'division': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'track_section': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter track section (optional)'
            }),
            'kilometer_marker': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter kilometer marker (optional)'
            }),
            'specifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter technical specifications (JSON format)'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., pieces, meters, kg'
            }),
            'deadline_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Number of days to complete'
            }),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Budget amount (optional)'
            }),
            'currency': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default currency
        if not self.instance.pk:
            self.fields['currency'].initial = 'INR'
        
        # Add division choices based on selected zone
        if 'zone' in self.data:
            try:
                zone_id = int(self.data.get('zone'))
                self.fields['division'].queryset = RailwayDivision.objects.filter(
                    zone_id=zone_id, is_active=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['division'].queryset = self.instance.zone.divisions.filter(is_active=True)
        else:
            self.fields['division'].queryset = RailwayDivision.objects.none()
        
        # Add location choices based on selected division
        if 'division' in self.data:
            try:
                division_id = int(self.data.get('division'))
                self.fields['location'].queryset = RailwayLocation.objects.filter(
                    division_id=division_id, is_active=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.division:
            self.fields['location'].queryset = self.instance.division.locations.filter(is_active=True)
        else:
            self.fields['location'].queryset = RailwayLocation.objects.none()
    
    def clean_specifications(self):
        """
        Validate specifications JSON format.
        """
        specifications = self.cleaned_data.get('specifications')
        if specifications:
            try:
                import json
                json.loads(specifications)
            except json.JSONDecodeError:
                raise ValidationError('Specifications must be valid JSON format.')
        return specifications
    
    def clean_deadline_days(self):
        """
        Validate deadline days.
        """
        deadline_days = self.cleaned_data.get('deadline_days')
        if deadline_days and deadline_days < 1:
            raise ValidationError('Deadline must be at least 1 day.')
        return deadline_days


class VendorRequestForm(forms.ModelForm):
    """
    Form for vendor requests.
    """
    class Meta:
        model = VendorRequest
        fields = [
            'proposed_price', 'delivery_time_days', 'proposal_description',
            'technical_specifications'
        ]
        widgets = {
            'proposed_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Enter proposed price'
            }),
            'delivery_time_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Delivery time in days'
            }),
            'proposal_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your proposal and approach'
            }),
            'technical_specifications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Technical specifications (JSON format)'
            }),
        }
    
    def clean_proposed_price(self):
        """
        Validate proposed price.
        """
        price = self.cleaned_data.get('proposed_price')
        if price and price <= 0:
            raise ValidationError('Proposed price must be greater than 0.')
        return price
    
    def clean_delivery_time_days(self):
        """
        Validate delivery time.
        """
        days = self.cleaned_data.get('delivery_time_days')
        if days and days < 1:
            raise ValidationError('Delivery time must be at least 1 day.')
        return days
    
    def clean_technical_specifications(self):
        """
        Validate technical specifications JSON format.
        """
        specs = self.cleaned_data.get('technical_specifications')
        if specs:
            try:
                import json
                json.loads(specs)
            except json.JSONDecodeError:
                raise ValidationError('Technical specifications must be valid JSON format.')
        return specs


class RequirementInspectionForm(forms.ModelForm):
    """
    Form for requirement inspections.
    """
    class Meta:
        model = RequirementInspection
        fields = [
            'inspection_type', 'result', 'findings', 'quality_rating',
            'issues_found', 'recommendations', 'photos', 'documents'
        ]
        widgets = {
            'inspection_type': forms.Select(attrs={'class': 'form-control'}),
            'result': forms.Select(attrs={'class': 'form-control'}),
            'findings': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe inspection findings'
            }),
            'quality_rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 10,
                'step': '0.1',
                'placeholder': 'Rating out of 10'
            }),
            'issues_found': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe any issues found (optional)'
            }),
            'recommendations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Provide recommendations (optional)'
            }),
        }
    
    def clean_quality_rating(self):
        """
        Validate quality rating.
        """
        rating = self.cleaned_data.get('quality_rating')
        if rating is not None and (rating < 0 or rating > 10):
            raise ValidationError('Quality rating must be between 0 and 10.')
        return rating


class RailwayZoneForm(forms.ModelForm):
    """
    Form for railway zones.
    """
    class Meta:
        model = RailwayZone
        fields = ['zone_code', 'name', 'description', 'headquarters', 'jurisdiction']
        widgets = {
            'zone_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., SR, ER, WR'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Southern Railway'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of the zone'
            }),
            'headquarters': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Zone headquarters location'
            }),
            'jurisdiction': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Geographical jurisdiction'
            }),
        }
    
    def clean_zone_code(self):
        """
        Validate zone code format.
        """
        code = self.cleaned_data.get('zone_code')
        if code:
            code = code.upper().strip()
            if len(code) < 2 or len(code) > 10:
                raise ValidationError('Zone code must be between 2 and 10 characters.')
        return code


class RailwayDivisionForm(forms.ModelForm):
    """
    Form for railway divisions.
    """
    class Meta:
        model = RailwayDivision
        fields = ['division_code', 'name', 'zone', 'headquarters', 'jurisdiction']
        widgets = {
            'division_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., MAS, SBC, TPTY'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Chennai Division'
            }),
            'zone': forms.Select(attrs={'class': 'form-control'}),
            'headquarters': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Division headquarters location'
            }),
            'jurisdiction': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Division jurisdiction'
            }),
        }
    
    def clean_division_code(self):
        """
        Validate division code format.
        """
        code = self.cleaned_data.get('division_code')
        if code:
            code = code.upper().strip()
            if len(code) < 2 or len(code) > 10:
                raise ValidationError('Division code must be between 2 and 10 characters.')
        return code


class RequirementStatusUpdateForm(forms.Form):
    """
    Form for updating requirement status.
    """
    status = forms.ChoiceField(
        choices=Requirement.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add notes about the status change (optional)'
        })
    )
    
    def __init__(self, *args, **kwargs):
        requirement = kwargs.pop('requirement', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if requirement and user:
            # Filter available statuses based on current status and user type
            available_statuses = []
            current_status = requirement.status
            
            if user.is_railway_authority():
                # Railway authority can change to any status
                available_statuses = Requirement.STATUS_CHOICES
            elif user.is_vendor():
                # Vendor can only change to shipped status
                if current_status == 'ACTIVE':
                    available_statuses = [('SHIPPED', 'Shipped')]
            elif user.is_railway_worker():
                # Railway worker can change received to installed
                if current_status == 'RECEIVED':
                    available_statuses = [('INSTALLED', 'Installed')]
            
            self.fields['status'].choices = available_statuses
