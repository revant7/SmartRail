"""
Forms for parts management.
"""
from django import forms
from django.forms import inlineformset_factory
from .models import Part, PartCategory, PartSpecification, PartImage, PartDocument


class PartForm(forms.ModelForm):
    """
    Form for creating and updating parts.
    """
    class Meta:
        model = Part
        fields = [
            'part_number', 'name', 'description', 'category',
            'manufacturer', 'model_number', 'serial_number',
            'material', 'weight', 'dimensions',
            'status', 'installation_date', 'expected_lifespan',
            'last_inspection_date', 'next_inspection_date',
            'current_location', 'railway_zone', 'railway_division',
            'track_section', 'kilometer_marker',
            'unit_cost', 'currency'
        ]
        widgets = {
            'part_number': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'model_number': forms.TextInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'material': forms.TextInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'installation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_lifespan': forms.NumberInput(attrs={'class': 'form-control'}),
            'last_inspection_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_inspection_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'current_location': forms.TextInput(attrs={'class': 'form-control'}),
            'railway_zone': forms.TextInput(attrs={'class': 'form-control'}),
            'railway_division': forms.TextInput(attrs={'class': 'form-control'}),
            'track_section': forms.TextInput(attrs={'class': 'form-control'}),
            'kilometer_marker': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean_part_number(self):
        part_number = self.cleaned_data.get('part_number')
        if part_number:
            # Check for duplicates
            queryset = Part.objects.filter(part_number=part_number)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("A part with this part number already exists.")
        return part_number


class PartSpecificationForm(forms.ModelForm):
    """
    Form for part specifications.
    """
    class Meta:
        model = PartSpecification
        fields = ['name', 'value', 'unit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.TextInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
        }


# Create formset for specifications
PartSpecificationFormSet = inlineformset_factory(
    Part,
    PartSpecification,
    form=PartSpecificationForm,
    extra=1,
    can_delete=True,
    fields=['name', 'value', 'unit']
)


class PartImageForm(forms.ModelForm):
    """
    Form for uploading part images.
    """
    class Meta:
        model = PartImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PartDocumentForm(forms.ModelForm):
    """
    Form for uploading part documents.
    """
    class Meta:
        model = PartDocument
        fields = ['document_type', 'title', 'file', 'description']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PartSearchForm(forms.Form):
    """
    Form for searching parts.
    """
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by part number, name, or manufacturer...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=PartCategory.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Part.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by location...'
        })
    )
