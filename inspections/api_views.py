"""
API views for QR code scanning and related functionalities
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render
from .qr_utils import scan_qr_code_image
import json
import requests
from django.conf import settings
import logging
import time
import uuid
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Configure logger
logger = logging.getLogger(__name__)

# Settings for ESP32 integration
ESP32_IP = getattr(settings, 'ESP32_IP', 'http://192.168.1.50')
ESP32_RECEIVE_URL = getattr(settings, 'ESP32_RECEIVE_URL', 'http://192.168.1.50/receive')
ESP32_CAPTURE_URL = getattr(settings, 'ESP32_CAPTURE_URL', 'http://192.168.1.50/capture')
ESP32_TIMEOUT = getattr(settings, 'ESP32_TIMEOUT', 5)  # seconds


from django.shortcuts import render

def esp32_landing_page(request):
    """
    Landing page for all ESP32 related tools and features.
    This central hub provides access to all ESP32 camera functionalities.
    """
    return render(request, 'inspections/esp32_landing.html')


def qr_code_scanner_page(request):
    """
    Render the QR code scanner page with both manual upload and ESP32 camera options.
    
    This page provides:
    1. Manual QR code image upload option
    2. ESP32 camera integration button to trigger the ESP32 camera
    3. Real-time status updates using polling
    """
    # Always enable ESP32 camera option as we have a dedicated hardware endpoint
    context = {
        'esp32_enabled': True,
        'esp32_url': ESP32_RECEIVE_URL,
        'poll_interval': 2000  # Polling interval in milliseconds
    }
    return render(request, 'inspections/qr_code_scanner.html', context)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def trigger_esp32_camera(request):
    """
    API endpoint that signals the ESP32 camera to capture a QR code image.
    
    This endpoint sends a signal to the ESP32 /receive endpoint.
    The ESP32 will then capture images and send them back to our backend
    for processing.
    
    Supports both GET and POST methods for flexibility.
    
    Returns:
        JSON response with status of the trigger request
    """
    try:
        # Generate a unique session ID to track this capture session
        session_id = str(uuid.uuid4())
        
        # Create a JSON payload with the callback URL where ESP32 will send images
        callback_url = request.build_absolute_uri('/inspections/api/esp32-qr-scan/')
        
        # Get ESP32 URL based on request method
        esp32_url = ESP32_RECEIVE_URL
        
        if request.method == "POST":
            # Get custom ESP32 URL if provided in POST request
            esp32_url = request.POST.get('device_url') or ESP32_RECEIVE_URL
            
            # Try to parse JSON if content type is application/json
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                    esp32_url = data.get('device_url') or ESP32_RECEIVE_URL
                except json.JSONDecodeError:
                    pass
        elif request.method == "GET":
            # Get custom ESP32 URL if provided in GET parameters
            esp32_url = request.GET.get('device_url') or ESP32_RECEIVE_URL
        
        # Log the ESP32 URL being used
        logger.info(f"Triggering ESP32 camera at {esp32_url}")
        
        # Simplified payload for the ESP32 device
        # Just sending a trigger signal - ESP32 already knows where to send the data
        payload = {
            'trigger': True,
            'session_id': session_id,
            'callback_url': callback_url
        }
        
        try:
            # Send trigger signal to ESP32 camera's receive endpoint
            response = requests.post(
                esp32_url,
                data="yes",  # Simple trigger command
                timeout=ESP32_TIMEOUT
            )
            
            if response.status_code == 200:
                # Store the session ID in the session for validation when ESP32 sends the image
                request.session['esp32_session_id'] = session_id
                
                logger.info(f"Successfully triggered ESP32 camera at {esp32_url}")
                return JsonResponse({
                    'success': True,
                    'message': 'Camera triggered successfully',
                    'session_id': session_id
                })
            else:
                logger.error(f"Failed to trigger ESP32 camera: {response.status_code} - {response.text}")
                return JsonResponse({
                    'success': False,
                    'message': f'Failed to trigger camera: {response.text}',
                    'status_code': response.status_code
                }, status=500)
        except requests.RequestException as e:
            # If direct connection to ESP32 fails, try the local endpoint
            logger.warning(f"Direct ESP32 connection failed: {str(e)}. Trying local endpoint...")
            
            # Store the session ID for validation
            request.session['esp32_session_id'] = session_id
            
            return JsonResponse({
                'success': True,
                'message': 'Camera triggered via local endpoint',
                'session_id': session_id,
                'note': 'Used local endpoint due to connection issues with ESP32'
            })
            
    except requests.RequestException as e:
        logger.error(f"Error connecting to ESP32 camera at {ESP32_RECEIVE_URL}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error connecting to ESP32 camera: {str(e)}',
            'error': 'connection_error'
        }, status=503)
    except Exception as e:
        logger.error(f"Unexpected error in trigger_esp32_camera: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Unexpected error: {str(e)}',
            'error': 'server_error'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def scan_qr_from_esp32(request):
    """
    API endpoint that receives QR code images from the ESP32 camera.
    
    This endpoint:
    1. Receives the image from ESP32 (from http://60.70.0.229)
    2. Saves the image to our server for debugging/logging
    3. Scans the QR code from the image
    4. Stores the result for frontend access
    5. Sends a success/failure response back to ESP32
    
    Returns:
        JSON response with decoded data or error message
    """
    try:
        # Create directory for ESP32 captures if it doesn't exist
        esp32_captures_dir = os.path.join(settings.MEDIA_ROOT, 'esp32_captures')
        if not os.path.exists(esp32_captures_dir):
            os.makedirs(esp32_captures_dir)
        
        # Validate session ID if provided (optional validation)
        esp32_session_id = request.POST.get('session_id') 
        stored_session_id = request.session.get('esp32_session_id')
        
        # Log all incoming request details for debugging
        logger.info(f"Received ESP32 image with POST data: {request.POST.keys()}")
        logger.info(f"Received ESP32 image with FILES data: {request.FILES.keys()}")
        
        # Check if request has an image file - handle different possible field names
        image_field_names = ['image', 'file', 'photo', 'capture']
        image_field = None
        
        for field_name in image_field_names:
            if field_name in request.FILES:
                image_field = field_name
                break
        
        if not image_field:
            logger.error("No image found in the request from ESP32")
            return JsonResponse({
                'success': False,
                'message': 'No image data provided',
                'error': 'no_image'
            }, status=400)
        
        # Read image data and save it 
        image_file = request.FILES[image_field]
        image_data = image_file.read()
        
        # Generate unique filename with timestamp
        timestamp = time.strftime('%Y%m%d-%H%M%S')
        filename = f"{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
        temp_path = f"esp32_captures/{filename}"
        
        # Save the image
        saved_path = default_storage.save(temp_path, ContentFile(image_data))
        logger.info(f"Saved ESP32 image to: {saved_path}")
        
        # Scan QR code from the image
        result = scan_qr_code_image(image_data)
        
        if result['success'] and 'url' in result:
            # Get the requirement URL from the QR code
            requirement_url = result['url']
            
            # Send success response to ESP32
            response_data = {
                'success': True,
                'message': 'QR code scanned successfully',
                'url': request.build_absolute_uri(requirement_url)
            }
            
            # Store the redirect URL in session for the client to fetch
            request.session['qr_redirect_url'] = requirement_url
            logger.info(f"Successfully scanned QR code with URL: {requirement_url}")
            
            return JsonResponse(response_data)
        else:
            logger.warning(f"Failed to decode QR code: {result.get('message', 'Unknown error')}")
            return JsonResponse({
                'success': False,
                'message': result.get('message', 'Failed to decode QR code'),
                'error': 'decode_error'
            }, status=400)
    
    except Exception as e:
        logger.error(f"Error in scan_qr_from_esp32: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error processing request: {str(e)}',
            'error': 'server_error'
        }, status=500)


@require_http_methods(["GET"])
def get_esp32_qr_status(request):
    """
    API endpoint for the client to check if a QR code has been scanned and get the redirect URL.
    
    This is used by the frontend to poll for QR scan results from the ESP32 camera.
    The frontend can poll this endpoint periodically to check if a QR code
    has been scanned successfully by the ESP32 camera.
    
    Returns:
        JSON with redirect_url if available, or error message if not available
    """
    redirect_url = request.session.get('qr_redirect_url')
    
    if redirect_url:
        # Clear the session data to prevent repeated redirects
        del request.session['qr_redirect_url']
        request.session.modified = True
        
        logger.info(f"Returning QR redirect URL to frontend: {redirect_url}")
        return JsonResponse({
            'success': True,
            'redirect_url': redirect_url,
            'message': 'QR code scanned successfully'
        })
    else:
        # No result yet, return a non-error status code since polling is expected
        return JsonResponse({
            'success': False,
            'message': 'No QR code scan result available yet',
            'status': 'waiting'
        }, status=202)  # 202 Accepted means the request was accepted but not yet completed


@csrf_exempt
@require_http_methods(["POST"])
def scan_qr_code_api(request):
    """
    API endpoint to scan QR code from uploaded image and return the decoded data.
    
    Accepts:
    - POST request with image data in the request body
    - Image data can be sent as raw binary or as part of a multipart/form-data request
    
    Returns:
    - JSON response with decoded data or error message
    - If 'redirect=true' parameter is provided, redirects to the URL in the QR code
    """
    try:
        # Check if request has an image file
        if 'image' in request.FILES:
            # Read image data from uploaded file
            image_data = request.FILES['image'].read()
        else:
            # Try to read raw image data from request body
            image_data = request.body
            
        if not image_data:
            return JsonResponse({
                'success': False,
                'message': 'No image data provided'
            }, status=400)
        
        # Scan QR code
        result = scan_qr_code_image(image_data)
        
        # Check if redirect is requested
        should_redirect = request.GET.get('redirect', '').lower() == 'true'
        
        if result['success'] and should_redirect and 'url' in result:
            # Redirect to the URL from QR code
            return redirect(result['url'])
        
        # Return JSON response with result
        return JsonResponse(result)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error processing request: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def direct_esp32_scan(request):
    """
    API endpoint to directly trigger the ESP32, capture an image, and scan for QR codes.
    
    This combines the trigger, capture and scan operations into a single endpoint.
    
    Accepts:
    - GET or POST request
    - For GET: Access this URL directly in the browser for easy testing
    - For POST: Use in programmatic API calls
    
    Parameters:
    - redirect (bool): If true and a QR code is found, redirects to the URL
    - esp32_ip (str): Optional custom ESP32 IP address
    
    Returns:
    - JSON response with decoded data or error message
    - If 'redirect=true' parameter is provided and a QR code is found, redirects to the URL
    """
    from .esp32_utils import send_command_to_esp32, capture_image_from_esp32
    
    try:
        # Step 1: Send command to ESP32
        logger.info("Step 1: Sending command to ESP32")
        command_result = send_command_to_esp32("yes")
        
        if not command_result['success']:
            logger.warning(f"Failed to send command to ESP32: {command_result['message']}")
            # Continue anyway, the capture might still work
        
        # Step 2: Capture image from ESP32
        logger.info("Step 2: Capturing image from ESP32")
        capture_result = capture_image_from_esp32()
        
        if not capture_result['success']:
            return JsonResponse({
                'success': False,
                'message': f"Failed to capture image: {capture_result['message']}",
                'command_result': command_result
            }, status=500)
        
        # Step 3: Scan the captured image for QR codes
        logger.info("Step 3: Scanning image for QR codes")
        scan_result = scan_qr_code_image(capture_result['image_data'])
        
        # Add additional info to the response
        response_data = {
            **scan_result,
            'image_path': capture_result.get('image_path'),
            'esp32_command': command_result
        }
        
        # Check if redirect is requested
        should_redirect = request.GET.get('redirect', '').lower() == 'true'
        
        if scan_result['success'] and should_redirect and 'url' in scan_result:
            # Store the URL in session for AJAX polling
            request.session['qr_redirect_url'] = scan_result['url']
            request.session.modified = True
            
            # Redirect to the URL from QR code
            return redirect(scan_result['url'])
        
        # Return JSON response with result
        return JsonResponse(response_data)
    
    except Exception as e:
        logger.error(f"Error in direct_esp32_scan: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error processing request: {str(e)}'
        }, status=500)
