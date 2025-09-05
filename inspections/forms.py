"""
Forms for online inspection system.
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import (
    OnlineInspection, InspectionPhoto, InspectionDocument,
    InspectionChecklistResponse, InspectionStage
)
from railway.models import Requirement
from parts.models import Part
from orders.models import PurchaseOrder


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class OnlineInspectionForm(forms.ModelForm):
    """
    Form for creating and updating online inspections.
    """
    class Meta:
        model = OnlineInspection
        fields = [
            'stage', 'requirement', 'part', 'order', 'findings', 'issues_found',
            'recommendations', 'corrective_actions', 'overview_notes',
            'inspection_location', 'railway_zone', 'railway_division',
            'track_section', 'kilometer_marker', 'latitude', 'longitude',
            'quality_rating', 'overall_score', 'result'
        ]
        widgets = {
            'findings': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'issues_found': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'recommendations': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'corrective_actions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'overview_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'stage': forms.Select(attrs={'class': 'form-control'}),
            'requirement': forms.Select(attrs={'class': 'form-control'}),
            'part': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.Select(attrs={'class': 'form-control'}),
            'inspection_location': forms.TextInput(attrs={'class': 'form-control'}),
            'railway_zone': forms.TextInput(attrs={'class': 'form-control'}),
            'railway_division': forms.TextInput(attrs={'class': 'form-control'}),
            'track_section': forms.TextInput(attrs={'class': 'form-control'}),
            'kilometer_marker': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'quality_rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '10'}),
            'overall_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'result': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter choices based on user type
        if user:
            if user.user_type == 'VENDOR':
                self.fields['requirement'].queryset = Requirement.objects.filter(
                    assigned_vendor=user
                )
            elif user.user_type == 'RAILWAY_AUTHORITY':
                self.fields['requirement'].queryset = Requirement.objects.all()
            elif user.user_type == 'RAILWAY_WORKER':
                self.fields['requirement'].queryset = Requirement.objects.filter(
                    status__in=['ACTIVE', 'SHIPPED', 'RECEIVED', 'INSTALLED']
                )
    
    def clean(self):
        cleaned_data = super().clean()
        stage = cleaned_data.get('stage')
        requirement = cleaned_data.get('requirement')
        part = cleaned_data.get('part')
        order = cleaned_data.get('order')
        
        # At least one related object must be selected
        if not any([requirement, part, order]):
            raise ValidationError("At least one related object (requirement, part, or order) must be selected.")
        
        # Validate stage requirements
        if stage:
            if stage.requires_vendor and not cleaned_data.get('vendor'):
                raise ValidationError(f"This stage requires a vendor to be assigned.")
            if stage.requires_receiver and not cleaned_data.get('receiver'):
                raise ValidationError(f"This stage requires a receiver to be assigned.")
            if stage.requires_railway_auth and not cleaned_data.get('railway_auth'):
                raise ValidationError(f"This stage requires a railway authority to be assigned.")
            if stage.requires_worker and not cleaned_data.get('worker'):
                raise ValidationError(f"This stage requires a worker to be assigned.")
        
        return cleaned_data


class InspectionPhotoForm(forms.ModelForm):
    """
    Form for uploading inspection photos.
    """
    class Meta:
        model = InspectionPhoto
        fields = ['photo_type', 'image', 'caption', 'description', 'latitude', 'longitude']
        widgets = {
            'photo_type': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = True


class MultiplePhotoUploadForm(forms.Form):
    """
    Form for uploading multiple photos at once.
    """
    photos = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text="Select multiple photos to upload"
    )
    photo_type = forms.ChoiceField(
        choices=InspectionPhoto.PHOTO_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='OVERVIEW'
    )
    caption = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Caption for all photos'})
    )
    
    def clean_photos(self):
        photos = self.files.getlist('photos')
        if not photos:
            raise ValidationError("At least one photo must be uploaded.")
        
        # Validate file types and sizes
        for photo in photos:
            if not photo.content_type.startswith('image/'):
                raise ValidationError(f"File {photo.name} is not an image.")
            if photo.size > 10 * 1024 * 1024:  # 10MB limit
                raise ValidationError(f"File {photo.name} is too large. Maximum size is 10MB.")
        
        return photos


class InspectionDocumentForm(forms.ModelForm):
    """
    Form for uploading inspection documents.
    """
    class Meta:
        model = InspectionDocument
        fields = ['document_type', 'title', 'file', 'description']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = True
        self.fields['title'].required = True


class InspectionChecklistResponseForm(forms.ModelForm):
    """
    Form for responding to inspection checklist items.
    """
    class Meta:
        model = InspectionChecklistResponse
        fields = ['response', 'notes', 'photo']
        widgets = {
            'response': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'photo': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        inspection = kwargs.pop('inspection', None)
        super().__init__(*args, **kwargs)
        
        if inspection:
            # Filter photos to only those from this inspection
            self.fields['photo'].queryset = InspectionPhoto.objects.filter(
                inspection=inspection
            )


class InspectionSearchForm(forms.Form):
    """
    Form for searching inspections.
    """
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by inspection ID, requirement, part, or findings...'
        })
    )
    stage = forms.ModelChoiceField(
        queryset=InspectionStage.objects.filter(is_active=True),
        required=False,
        empty_label="All Stages",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + OnlineInspection.INSPECTION_STATUS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    result = forms.ChoiceField(
        choices=[('', 'All Results')] + OnlineInspection.INSPECTION_RESULTS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class InspectionStageForm(forms.ModelForm):
    """
    Form for creating and updating inspection stages.
    """
    class Meta:
        model = InspectionStage
        fields = [
            'name', 'stage_type', 'description', 'is_active', 'order',
            'requires_vendor', 'requires_receiver', 'requires_railway_auth', 'requires_worker'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'stage_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'requires_vendor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_receiver': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_railway_auth': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_worker': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
