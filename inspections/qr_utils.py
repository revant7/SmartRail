"""
QR Code utilities for equipment batch management.
"""
import qrcode
import uuid
import json
from io import BytesIO
from django.core.files.base import ContentFile
from django.http import HttpResponse
from .models import EquipmentBatch


def generate_qr_code_for_batch(batch, size=200):
    """
    Generate QR code containing requirement UUID, batch number and detail URL.
    
    Args:
        batch: EquipmentBatch object
        size: Size of the QR code image (default: 200x200)
    
    Returns:
        BytesIO object containing the QR code image
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # Create JSON data to be encoded in the QR code
    qr_data = {
        'requirement_id': str(batch.requirement.requirement_id),
        'batch_number': batch.batch_number,
        'url': f"/railway/requirement/{batch.requirement.requirement_id}/"
    }
    
    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize image if needed
    if size != 200:
        img = img.resize((size, size))
    
    # Convert to BytesIO
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer


def create_qr_code_response(batch, size=200):
    """
    Create HTTP response with QR code image.
    
    Args:
        batch: EquipmentBatch object
        size: Size of the QR code image
    
    Returns:
        HttpResponse with QR code image
    """
    qr_buffer = generate_qr_code_for_batch(batch, size)
    
    response = HttpResponse(qr_buffer.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="qr_code_{batch.batch_number}.png"'
    
    return response


def generate_qr_codes_for_all_batches():
    """
    Generate QR codes for all existing equipment batches.
    This is useful for creating QR codes for equipment that was created before QR integration.
    """
    batches = EquipmentBatch.objects.all()
    generated_codes = []
    
    for batch in batches:
        try:
            qr_buffer = generate_qr_code_for_batch(batch)
            generated_codes.append({
                'batch': batch,
                'qr_code': qr_buffer
            })
        except Exception as e:
            print(f"Error generating QR code for batch {batch.batch_number}: {e}")
    
    return generated_codes


def validate_qr_code_data(qr_data):
    """
    Validate if QR code data contains valid requirement and batch data.
    
    Args:
        qr_data: String data from QR code (JSON format)
    
    Returns:
        dict with validation result and batch info if valid
    """
    try:
        # Try to parse as JSON
        data = json.loads(qr_data)
        
        # Validate JSON structure
        if not all(key in data for key in ['requirement_id', 'batch_number']):
            return {
                'valid': False,
                'message': 'Invalid QR code format - missing required fields'
            }
        
        # Get requirement
        from railway.models import Requirement
        try:
            requirement = Requirement.objects.get(requirement_id=data['requirement_id'])
        except Requirement.DoesNotExist:
            return {
                'valid': False,
                'requirement_id': data['requirement_id'],
                'message': 'Requirement not found'
            }
        
        # Check if batch exists
        try:
            batch = EquipmentBatch.objects.get(batch_number=data['batch_number'])
            return {
                'valid': True,
                'requirement': requirement,
                'batch_number': data['batch_number'],
                'batch': batch,
                'message': 'Valid equipment batch found'
            }
        except EquipmentBatch.DoesNotExist:
            return {
                'valid': True,
                'requirement': requirement,
                'batch_number': data['batch_number'],
                'batch': None,
                'message': 'Valid requirement found but batch not found'
            }
            
    except (ValueError, json.JSONDecodeError):
        return {
            'valid': False,
            'message': 'Invalid QR code format - cannot parse JSON data'
        }
    except Exception as e:
        return {
            'valid': False,
            'message': f'Error validating QR code: {str(e)}'
        }


def create_test_qr_codes():
    """
    Create test QR codes for development and testing purposes.
    """
    from railway.models import Requirement
    
    # Get a requirement for testing
    requirements = Requirement.objects.all()
    if not requirements.exists():
        raise ValueError("No requirements found. Create requirements first.")
    
    test_batches = [
        {
            'batch_number': 'BATCH-001',
            'batch_name': 'Test Liners - Batch 001',
            'equipment_type': 'LINERS',
            'manufacturer': 'Test Manufacturer',
            'model_number': 'LN-001',
            'serial_number': 'SN-001',
            'requirement': requirements.first()
        },
        {
            'batch_number': 'BATCH-002',
            'batch_name': 'Test Pads - Batch 002',
            'equipment_type': 'PADS',
            'manufacturer': 'Pad Corp',
            'model_number': 'PD-002',
            'serial_number': 'SN-002',
            'requirement': requirements.first()
        },
        {
            'batch_number': 'BATCH-003',
            'batch_name': 'Test Clips - Batch 003',
            'equipment_type': 'CLIPS',
            'manufacturer': 'Clip Systems',
            'model_number': 'CL-003',
            'serial_number': 'SN-003',
            'requirement': requirements.first()
        }
    ]
    
    created_batches = []
    
    for batch_data in test_batches:
        try:
            # Check if batch with this number already exists
            if not EquipmentBatch.objects.filter(batch_number=batch_data['batch_number']).exists():
                batch = EquipmentBatch.objects.create(**batch_data)
                created_batches.append(batch)
            print(f"Created test batch: {batch.batch_name} ({batch.batch_uuid})")
        except Exception as e:
            print(f"Error creating test batch: {e}")
    
    return created_batches
