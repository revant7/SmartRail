"""
Mock ESP32 camera module for testing the QR code scanning API.

This module provides endpoints to simulate ESP32 camera behavior for testing
the QR code scanning functionality without a physical ESP32 device.
It also includes real ESP32 integration endpoints.
"""
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests
import time
from datetime import datetime
import os
import logging
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

# Path to sample QR code image for testing
SAMPLE_QR_PATH = os.path.join(os.path.dirname(__file__), '..', 'media', 'qr_codes', 'requirements')

@csrf_exempt
@require_http_methods(["GET"])
def mock_esp32_ui(request):
    """
    Renders a simple UI for testing the ESP32 camera integration.
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mock ESP32 Camera</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { border: 1px solid #ddd; padding: 20px; border-radius: 5px; }
            .btn { padding: 10px 15px; background: #4CAF50; color: white; border: none; cursor: pointer; border-radius: 4px; }
            .btn:hover { background: #45a049; }
            pre { background: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }
            .status { margin-top: 20px; padding: 10px; border-radius: 4px; }
            .success { background-color: #d4edda; color: #155724; }
            .error { background-color: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <h1>Mock ESP32 Camera</h1>
        <div class="container">
            <h2>Camera Simulator</h2>
            <p>This page simulates an ESP32 camera for testing the QR code scanning API.</p>
            
            <div>
                <button id="waitForTrigger" class="btn">Wait for Trigger</button>
                <button id="simulateCapture" class="btn">Simulate Capture & Send</button>
            </div>
            
            <div id="status" class="status" style="display: none;"></div>
            
            <h3>Last Request</h3>
            <pre id="lastRequest">No requests yet</pre>
            
            <h3>Last Response</h3>
            <pre id="lastResponse">No responses yet</pre>
        </div>
        
        <script>
            const waitForTriggerBtn = document.getElementById('waitForTrigger');
            const simulateCaptureBtn = document.getElementById('simulateCapture');
            const statusDiv = document.getElementById('status');
            const lastRequestPre = document.getElementById('lastRequest');
            const lastResponsePre = document.getElementById('lastResponse');
            
            let pollingInterval = null;
            let callbackUrl = null;
            let sessionId = null;
            
            // Function to wait for trigger from the main application
            waitForTriggerBtn.addEventListener('click', function() {
                // Show status
                statusDiv.className = 'status';
                statusDiv.innerHTML = 'Waiting for trigger...';
                statusDiv.style.display = 'block';
                
                // Clear any existing polling
                if (pollingInterval) {
                    clearInterval(pollingInterval);
                }
                
                // Start polling for trigger
                pollForTrigger();
            });
            
            // Function to poll for trigger
            function pollForTrigger() {
                fetch('/inspections/mock-esp32/check-trigger/')
                    .then(response => response.json())
                    .then(data => {
                        if (data.triggered) {
                            // Trigger received
                            statusDiv.className = 'status success';
                            statusDiv.innerHTML = 'Trigger received! Ready to capture.';
                            
                            // Save callback URL and session ID
                            callbackUrl = data.callback_url;
                            sessionId = data.session_id;
                            
                            // Display request details
                            lastRequestPre.textContent = JSON.stringify(data, null, 2);
                            
                            // Clear polling interval
                            if (pollingInterval) {
                                clearInterval(pollingInterval);
                                pollingInterval = null;
                            }
                        }
                    })
                    .catch(error => {
                        statusDiv.className = 'status error';
                        statusDiv.innerHTML = `Error checking for trigger: ${error.message}`;
                    });
            }
            
            // Function to simulate capture and send
            simulateCaptureBtn.addEventListener('click', function() {
                if (!callbackUrl) {
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML = 'No trigger received yet. Click "Wait for Trigger" first.';
                    statusDiv.style.display = 'block';
                    return;
                }
                
                statusDiv.className = 'status';
                statusDiv.innerHTML = 'Simulating capture and sending QR code...';
                
                // Create form data with the QR code image
                const formData = new FormData();
                formData.append('session_id', sessionId);
                
                // Get the QR code image from the server
                fetch('/inspections/mock-esp32/get-sample-qr/')
                    .then(response => response.blob())
                    .then(blob => {
                        formData.append('image', blob, 'qr_code.png');
                        
                        // Send the image to the callback URL
                        return fetch(callbackUrl, {
                            method: 'POST',
                            body: formData
                        });
                    })
                    .then(response => response.json())
                    .then(data => {
                        statusDiv.className = 'status success';
                        statusDiv.innerHTML = 'QR code sent successfully!';
                        
                        // Display response
                        lastResponsePre.textContent = JSON.stringify(data, null, 2);
                        
                        // Reset session
                        callbackUrl = null;
                        sessionId = null;
                    })
                    .catch(error => {
                        statusDiv.className = 'status error';
                        statusDiv.innerHTML = `Error sending QR code: ${error.message}`;
                    });
            });
            
            // Start polling automatically
            pollingInterval = setInterval(pollForTrigger, 1000);
            statusDiv.className = 'status';
            statusDiv.innerHTML = 'Waiting for trigger...';
            statusDiv.style.display = 'block';
        </script>
    </body>
    </html>
    """
    return HttpResponse(html)


# Store the last trigger received
last_trigger = {
    'timestamp': None,
    'callback_url': None,
    'session_id': None,
    'triggered': False
}

@csrf_exempt
@require_http_methods(["POST"])
def mock_esp32_trigger_endpoint(request):
    """
    Mock endpoint for the ESP32 camera trigger.
    This simulates the endpoint on the ESP32 that receives trigger requests.
    """
    global last_trigger
    
    try:
        # Parse JSON body
        data = json.loads(request.body)
        
        # Store trigger data
        last_trigger = {
            'timestamp': datetime.now().isoformat(),
            'callback_url': data.get('callback_url'),
            'session_id': data.get('session_id'),
            'triggered': True
        }
        
        # Log the trigger
        logger.info(f"Mock ESP32 triggered: {last_trigger}")
        
        # Return success response
        return JsonResponse({
            'success': True,
            'message': 'Trigger received, ready to capture',
            'timestamp': last_trigger['timestamp']
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON format'
        }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def mock_esp32_check_trigger(request):
    """
    Endpoint to check if a trigger has been received.
    """
    global last_trigger
    
    # If triggered, return the trigger data and reset the triggered flag
    if last_trigger['triggered']:
        response_data = last_trigger.copy()
        last_trigger['triggered'] = False
        return JsonResponse(response_data)
    
    # If not triggered, return empty response
    return JsonResponse({
        'triggered': False,
        'timestamp': datetime.now().isoformat()
    })


@require_http_methods(["GET"])
def mock_esp32_get_sample_qr(request):
    """
    Endpoint to get a sample QR code image for testing.
    """
    try:
        # Find a QR code image in the media directory
        qr_files = [f for f in os.listdir(SAMPLE_QR_PATH) if f.endswith('.png')]
        
        if not qr_files:
            return HttpResponse('No QR code images found', status=404)
        
        # Get the first QR code image
        qr_file = qr_files[0]
        qr_path = os.path.join(SAMPLE_QR_PATH, qr_file)
        
        # Read the image file
        with open(qr_path, 'rb') as f:
            image_data = f.read()
        
        # Return the image
        response = HttpResponse(image_data, content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="{qr_file}"'
        return response
    
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)


# Real ESP32 Integration Endpoints

@csrf_exempt
@require_http_methods(["POST"])
def esp32_receive_endpoint(request):
    """
    Endpoint for ESP32 to receive commands from the application.
    
    This endpoint:
    1. Receives a POST request with "data" parameter
    2. Returns a response indicating if the request was successful
    
    Example usage:
    POST /esp32/receive HTTP/1.1
    Content-Type: application/x-www-form-urlencoded
    
    data=yes
    """
    try:
        # Get the data from the request (can be form data or JSON)
        data = None
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                logger.info(f"Received JSON data at ESP32 receive endpoint: {data}")
            except json.JSONDecodeError:
                data = {"command": request.body.decode('utf-8')}
        else:
            data = request.POST.get('data')
            logger.info(f"Received form data at ESP32 receive endpoint: {data}")
            
        # If data is empty, try to get it from the raw body
        if not data and request.body:
            data = request.body.decode('utf-8')
            logger.info(f"Received raw data at ESP32 receive endpoint: {data}")
        
        # Process the command (in a real ESP32, this would trigger the camera)
        response_message = "Command received by ESP32, preparing to capture image"
        
        # Log the received command
        logger.info(f"ESP32 receive endpoint processed command: {data}")
        
        # Return success response
        return JsonResponse({
            "status": "success",
            "message": response_message,
            "received": str(data)
        })
    
    except Exception as e:
        logger.error(f"Error in ESP32 receive endpoint: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def esp32_capture_endpoint(request):
    """
    Endpoint to capture and return an image from the ESP32 camera.
    
    This endpoint:
    1. Simulates capturing an image from the ESP32 camera
    2. Returns the image data directly
    
    In a real ESP32, this would trigger the camera to take a photo
    and return the binary image data.
    """
    try:
        # In a real ESP32, this would capture an actual photo
        # Here we'll return a sample QR code image
        
        # Find a QR code image in the media directory
        qr_files = [f for f in os.listdir(SAMPLE_QR_PATH) if f.endswith('.png')]
        
        if not qr_files:
            return HttpResponse('No QR code images found', status=404)
        
        # Get the first QR code image
        qr_file = qr_files[0]
        qr_path = os.path.join(SAMPLE_QR_PATH, qr_file)
        
        # Read the image file
        with open(qr_path, 'rb') as f:
            image_data = f.read()
        
        logger.info(f"ESP32 capture endpoint returning image: {qr_path}")
        
        # Return the image with appropriate content type
        response = HttpResponse(image_data, content_type='image/jpeg')
        response['Content-Disposition'] = 'inline; filename="esp32_capture.jpg"'
        return response
    
    except Exception as e:
        logger.error(f"Error in ESP32 capture endpoint: {str(e)}")
        return HttpResponse(f'Error: {str(e)}', status=500)


def esp32_controller_page(request):
    """
    Page to control the ESP32 camera and display captured images.
    
    This page provides a UI to:
    1. Send signals to the ESP32
    2. Capture images from the ESP32
    3. Display the captured images
    """
    # ESP32 settings from the environment or default to a mock address
    esp32_ip = getattr(settings, 'ESP32_IP', 'http://192.168.1.50')
    
    context = {
        'esp32_ip': esp32_ip,
    }
    
    return render(request, 'inspections/esp32_controller.html', context)
