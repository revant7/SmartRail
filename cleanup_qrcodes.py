#!/usr/bin/env python
"""
Script to delete current requirements and QR codes,
and update QR code generation to use direct URLs
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qrail.settings')
django.setup()

from railway.models import Requirement
from inspections.models import EquipmentBatch
import os

def clean_requirements_and_qr_codes():
    """Delete all requirements and their QR codes"""
    print("Starting cleanup process...")
    
    # Count requirements and equipment batches
    req_count = Requirement.objects.count()
    batch_count = EquipmentBatch.objects.count()
    print(f"Found {req_count} requirements and {batch_count} equipment batches")
    
    # Delete QR code files first
    qr_paths = []
    
    # Get QR code paths from requirements
    for req in Requirement.objects.all():
        if req.qr_code:
            qr_paths.append(req.qr_code.path)
    
    # Delete the requirements from database
    print("Deleting requirements from database...")
    Requirement.objects.all().delete()
    print("All requirements deleted from database")
    
    # Delete actual files
    print("Deleting QR code files...")
    deleted_count = 0
    for path in qr_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
                deleted_count += 1
        except Exception as e:
            print(f"Error deleting QR code file {path}: {e}")
    
    print(f"Deleted {deleted_count} QR code files")
    print("Cleanup completed successfully")

if __name__ == "__main__":
    clean_requirements_and_qr_codes()
