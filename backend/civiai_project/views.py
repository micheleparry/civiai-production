from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os
from datetime import datetime

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for Railway deployment.
    Returns basic application status and environment information.
    """
    try:
        # Basic health check response
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv('CIVIAI_ENVIRONMENT', 'development'),
            "version": os.getenv('CIVIAI_APP_VERSION', '1.0.0'),
            "app_name": os.getenv('CIVIAI_APP_NAME', 'CivAI'),
        }
        
        return JsonResponse(health_data, status=200)
    
    except Exception as e:
        # Return error response if health check fails
        error_data = {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "environment": os.getenv('CIVIAI_ENVIRONMENT', 'development'),
        }
        
        return JsonResponse(error_data, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def root_view(request):
    """
    Root endpoint for the CivAI application.
    Returns basic application information.
    """
    try:
        app_data = {
            "name": "CivAI",
            "description": "AI-Powered Permitting & Compliance Management",
            "version": os.getenv('CIVIAI_APP_VERSION', '1.0.0'),
            "environment": os.getenv('CIVIAI_ENVIRONMENT', 'development'),
            "status": "running",
            "timestamp": datetime.utcnow().isoformat(),
            "endpoints": {
                "health": "/health/",
                "admin": "/admin/",
                "api": "/api/",
                "mcp": "/mcp/"
            }
        }
        
        return JsonResponse(app_data, status=200)
    
    except Exception as e:
        error_data = {
            "error": "Application error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return JsonResponse(error_data, status=500)
