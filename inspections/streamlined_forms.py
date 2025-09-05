"""
Forms for streamlined inspection system.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import InspectionStage, EquipmentBatch
import uuid


class StreamlinedInspectionForm(forms.Form):
    """
    Form for starting streamlined inspection with QR code or manual UUID entry.
    """
    batch_uuid = forms.UUIDField(
        label="Equipment Batch UUID",
        help_text="Scan QR code or enter UUID manually",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter or scan equipment batch UUID',
            'id': 'batch-uuid-input'
        })
    )
    stage = forms.ModelChoiceField(
        queryset=InspectionStage.objects.filter(is_active=True),
        label="Inspection Stage",
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select the inspection stage"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter stages based on user type
        if user:
            if user.user_type == 'VENDOR':
                # Vendors typically do manufacturing and supply inspections
                self.fields['stage'].queryset = InspectionStage.objects.filter(
                    stage_type__in=['MANUFACTURING', 'SUPPLY'],
                    is_active=True
                )
            elif user.user_type == 'RAILWAY_AUTHORITY':
                # Railway authority does receiving and final inspections
                self.fields['stage'].queryset = InspectionStage.objects.filter(
                    stage_type__in=['RECEIVING', 'FINAL'],
                    is_active=True
                )
            elif user.user_type == 'RAILWAY_WORKER':
                # Workers do fitting/installation inspections
                self.fields['stage'].queryset = InspectionStage.objects.filter(
                    stage_type='FITTING',
                    is_active=True
                )
    
    def clean_batch_uuid(self):
        batch_uuid = self.cleaned_data['batch_uuid']
        
        # Check if batch exists, if not we'll create it
        try:
            EquipmentBatch.objects.get(batch_uuid=batch_uuid)
        except EquipmentBatch.DoesNotExist:
            # This is okay - we'll create the batch
            pass
        
        return batch_uuid


class QRCodeScanForm(forms.Form):
    """
    Form for QR code scanning.
    """
    qr_data = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'QR code data will appear here',
            'readonly': True,
            'id': 'qr-data-input'
        }),
        required=False
    )
    
    def clean_qr_data(self):
        qr_data = self.cleaned_data.get('qr_data', '')
        
        if qr_data:
            try:
                # Try to parse as UUID
                uuid.UUID(qr_data)
                return qr_data
            except ValueError:
                raise ValidationError("Invalid UUID format in QR code data.")
        
        return qr_data


class PhotoUploadForm(forms.Form):
    """
    Form for uploading photos during streamlined inspection.
    """
    PHOTO_TYPES = [
        ('EQUIPMENT_OVERVIEW', 'Equipment Overview'),
        ('EQUIPMENT_DETAIL', 'Equipment Detail'),
        ('QR_CODE', 'QR Code Scan'),
        ('DEFECT', 'Defect Found'),
        ('COMPLETION', 'Completion Photo'),
        ('OTHER', 'Other'),
    ]
    
    photo = forms.ImageField(
        label="Photo",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'capture': 'environment'  # For mobile camera
        })
    )
    photo_type = forms.ChoiceField(
        choices=PHOTO_TYPES,
        initial='EQUIPMENT_OVERVIEW',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    caption = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional caption for this photo'
        })
    )
    qr_code_data = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.HiddenInput()
    )
    qr_code_uuid = forms.UUIDField(
        required=False,
        widget=forms.HiddenInput()
    )


class InspectionSubmissionForm(forms.Form):
    """
    Form for submitting streamlined inspection.
    """
    INSPECTION_RESULTS = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('CONDITIONAL_PASS', 'Conditional Pass'),
        ('REQUIRES_RETEST', 'Requires Retest'),
    ]
    
    result = forms.ChoiceField(
        choices=INSPECTION_RESULTS,
        initial='PASS',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    findings = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe your findings...'
        }),
        required=False
    )
    issues_found = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describe any issues found...'
        }),
        required=False
    )
    recommendations = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Provide recommendations...'
        }),
        required=False
    )


class BatchSearchForm(forms.Form):
    """
    Form for searching equipment batches.
    """
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by batch name, UUID, or equipment type...'
        })
    )
    equipment_type = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by equipment type...'
        })
    )
    current_stage = forms.ChoiceField(
        choices=[
            ('', 'All Stages'),
            ('MANUFACTURING', 'Manufacturing'),
            ('SUPPLY', 'Supply'),
            ('RECEIVING', 'Receiving'),
            ('FITTING', 'Fitting/Installation'),
            ('FINAL', 'Final Inspection'),
            ('COMPLETED', 'Completed'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
