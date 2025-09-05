"""
QR Code utilities for equipment batch management.
"""
import qrcode
import uuid
from io import BytesIO
from django.core.files.base import ContentFile
from django.http import HttpResponse
from .models import EquipmentBatch


def generate_qr_code_for_batch(batch_uuid, size=200):
    """
    Generate QR code for an equipment batch UUID.
    
    Args:
        batch_uuid: UUID string of the equipment batch
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
    qr.add_data(str(batch_uuid))
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


def create_qr_code_response(batch_uuid, size=200):
    """
    Create HTTP response with QR code image.
    
    Args:
        batch_uuid: UUID string of the equipment batch
        size: Size of the QR code image
    
    Returns:
        HttpResponse with QR code image
    """
    qr_buffer = generate_qr_code_for_batch(batch_uuid, size)
    
    response = HttpResponse(qr_buffer.getvalue(), content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="qr_code_{batch_uuid}.png"'
    
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
            qr_buffer = generate_qr_code_for_batch(batch.batch_uuid)
            generated_codes.append({
                'batch': batch,
                'qr_code': qr_buffer
            })
        except Exception as e:
            print(f"Error generating QR code for batch {batch.batch_uuid}: {e}")
    
    return generated_codes


def validate_qr_code_data(qr_data):
    """
    Validate if QR code data contains a valid equipment batch UUID.
    
    Args:
        qr_data: String data from QR code
    
    Returns:
        dict with validation result and batch info if valid
    """
    try:
        # Try to parse as UUID
        batch_uuid = uuid.UUID(qr_data)
        
        # Check if batch exists
        try:
            batch = EquipmentBatch.objects.get(batch_uuid=batch_uuid)
            return {
                'valid': True,
                'batch_uuid': str(batch_uuid),
                'batch': batch,
                'message': 'Valid equipment batch UUID'
            }
        except EquipmentBatch.DoesNotExist:
            return {
                'valid': True,
                'batch_uuid': str(batch_uuid),
                'batch': None,
                'message': 'Valid UUID format but batch not found (will be created)'
            }
            
    except ValueError:
        return {
            'valid': False,
            'batch_uuid': None,
            'batch': None,
            'message': 'Invalid UUID format'
        }


def create_test_qr_codes():
    """
    Create test QR codes for development and testing purposes.
    """
    test_batches = [
        {
            'batch_name': 'Test Railway Track - Batch 001',
            'equipment_type': 'Railway Track',
            'manufacturer': 'Test Manufacturer',
            'model_number': 'TR-001',
            'serial_number': 'SN-001'
        },
        {
            'batch_name': 'Test Signal Equipment - Batch 002',
            'equipment_type': 'Signal Equipment',
            'manufacturer': 'Signal Corp',
            'model_number': 'SE-002',
            'serial_number': 'SN-002'
        },
        {
            'batch_name': 'Test Power Equipment - Batch 003',
            'equipment_type': 'Power Equipment',
            'manufacturer': 'Power Systems',
            'model_number': 'PE-003',
            'serial_number': 'SN-003'
        }
    ]
    
    created_batches = []
    
    for batch_data in test_batches:
        try:
            batch = EquipmentBatch.objects.create(**batch_data)
            created_batches.append(batch)
            print(f"Created test batch: {batch.batch_name} ({batch.batch_uuid})")
        except Exception as e:
            print(f"Error creating test batch: {e}")
    
    return created_batches
