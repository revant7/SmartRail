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
    
    # Use direct URL in QR code for immediate redirection
    qr_data = f"/railway/requirements/{batch.requirement.requirement_id}/"
    
    qr.add_data(qr_data)
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
    Validate if QR code data contains a valid URL.
    
    Args:
        qr_data: String data from QR code (URL format)
    
    Returns:
        dict with validation result and requirement info if valid
    """
    try:
        # Format of URL is expected to be: /railway/requirements/{uuid}/
        parts = qr_data.strip('/').split('/')
        
        if len(parts) < 3 or 'requirements' not in parts:
            return {
                'valid': False,
                'message': 'Invalid QR code URL format'
            }
        
        # Find the index of 'requirements' and get the UUID that should follow it
        req_index = parts.index('requirements')
        if req_index + 1 >= len(parts):
            return {
                'valid': False,
                'message': 'Missing requirement UUID in QR code URL'
            }
            
        requirement_id = parts[req_index + 1]
        
        # Get requirement
        from railway.models import Requirement
        try:
            requirement = Requirement.objects.get(requirement_id=requirement_id)
            
            return {
                'valid': True,
                'requirement': requirement,
                'message': 'Valid requirement found'
            }
        except Requirement.DoesNotExist:
            return {
                'valid': False,
                'requirement_id': requirement_id,
                'message': 'Requirement not found'
            }
            
    except Exception as e:
        return {
            'valid': False,
            'message': f'Error validating QR code: {str(e)}'
        }


def scan_qr_code_image(image_data):
    """
    Scan a QR code from an image and extract the URL.
    
    Args:
        image_data: Image data as bytes or file-like object
        
    Returns:
        Dictionary with decoded data and status
    """
    import cv2
    import numpy as np
    from pyzbar.pyzbar import decode
    
    try:
        # Convert image data to numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        
        # Check if image was loaded successfully
        if image is None:
            return {
                'success': False,
                'message': 'Failed to decode image data'
            }
        
        # Decode QR code
        decoded_objects = decode(image)
        
        if not decoded_objects:
            return {
                'success': False,
                'message': 'No QR code found in the image'
            }
        
        # Get the data from the first QR code
        qr_data = decoded_objects[0].data.decode('utf-8')
        
        # Validate the QR code data
        validation = validate_qr_code_data(qr_data)
        
        if validation.get('valid', False):
            return {
                'success': True,
                'url': qr_data,
                'requirement': validation.get('requirement')
            }
        else:
            return {
                'success': False,
                'message': validation.get('message', 'Invalid QR code data')
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error scanning QR code: {str(e)}'
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
