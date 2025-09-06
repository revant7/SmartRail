"""
Utility functions to interact directly with the ESP32 camera.
"""
import requests
import logging
from django.conf import settings
import time
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

def send_command_to_esp32(command="yes"):
    """
    Send a command to the ESP32 camera.
    
    Args:
        command (str): The command to send to the ESP32
        
    Returns:
        dict: The response from the ESP32, with 'success' and 'message' keys
    """
    try:
        # Get ESP32 URL from settings
        esp32_receive_url = getattr(settings, 'ESP32_RECEIVE_URL', 'http://192.168.1.50/receive')
        
        # Send the command
        response = requests.post(
            esp32_receive_url, 
            data=command,
            timeout=getattr(settings, 'ESP32_TIMEOUT', 5)
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            logger.info(f"Successfully sent command to ESP32: {command}")
            return {
                'success': True,
                'message': 'Command sent successfully',
                'response': response.text
            }
        else:
            logger.error(f"Failed to send command to ESP32: {response.status_code} - {response.text}")
            return {
                'success': False,
                'message': f'Failed to send command: {response.text}',
                'status_code': response.status_code
            }
    
    except requests.RequestException as e:
        logger.error(f"Error connecting to ESP32: {str(e)}")
        return {
            'success': False,
            'message': f'Error connecting to ESP32: {str(e)}',
            'error': 'connection_error'
        }
    
    except Exception as e:
        logger.error(f"Unexpected error in send_command_to_esp32: {str(e)}")
        return {
            'success': False,
            'message': f'Unexpected error: {str(e)}',
            'error': 'server_error'
        }

def capture_image_from_esp32():
    """
    Capture an image from the ESP32 camera.
    
    Returns:
        dict: A dictionary with the following keys:
            - 'success': Boolean indicating if the capture was successful
            - 'message': Message describing the result
            - 'image_path': Path to the saved image (if successful)
            - 'image_data': Binary image data (if successful)
    """
    try:
        # Get ESP32 URL from settings
        esp32_capture_url = getattr(settings, 'ESP32_CAPTURE_URL', 'http://192.168.1.50/capture')
        
        # Send request to capture image
        response = requests.get(
            esp32_capture_url,
            timeout=getattr(settings, 'ESP32_TIMEOUT', 5)
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            # Create directory for ESP32 captures if it doesn't exist
            esp32_captures_dir = os.path.join(settings.MEDIA_ROOT, 'esp32_captures')
            if not os.path.exists(esp32_captures_dir):
                os.makedirs(esp32_captures_dir)
                
            # Generate unique filename with timestamp
            timestamp = time.strftime('%Y%m%d-%H%M%S')
            filename = f"esp32_{timestamp}.jpg"
            temp_path = f"esp32_captures/{filename}"
            
            # Save the image
            saved_path = default_storage.save(temp_path, ContentFile(response.content))
            logger.info(f"Saved ESP32 image to: {saved_path}")
            
            return {
                'success': True,
                'message': 'Image captured successfully',
                'image_path': saved_path,
                'image_data': response.content
            }
        else:
            logger.error(f"Failed to capture image from ESP32: {response.status_code} - {response.text}")
            return {
                'success': False,
                'message': f'Failed to capture image: {response.text}',
                'status_code': response.status_code
            }
    
    except requests.RequestException as e:
        logger.error(f"Error connecting to ESP32: {str(e)}")
        return {
            'success': False,
            'message': f'Error connecting to ESP32: {str(e)}',
            'error': 'connection_error'
        }
    
    except Exception as e:
        logger.error(f"Unexpected error in capture_image_from_esp32: {str(e)}")
        return {
            'success': False,
            'message': f'Unexpected error: {str(e)}',
            'error': 'server_error'
        }
