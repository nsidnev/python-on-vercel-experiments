from django.http import JsonResponse
from datetime import datetime
import sys
import platform


def index(request):
    """Simple view that returns current time and system info"""
    return JsonResponse({
        "message": "Django on Vercel",
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "note": "Django works on Vercel but has limitations (no persistent storage, sessions don't work reliably)",
    })
