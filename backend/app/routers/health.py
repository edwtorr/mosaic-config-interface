"""
Router para endpoints de health check
"""

from fastapi import APIRouter, status
from app.models import MessageResponse
from app.config import settings
import sys
from pathlib import Path

router = APIRouter()


@router.get(
    "/health",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Verifica el estado de la API"
)
async def health_check():
    """
    Health check endpoint

    Retorna el estado de la API y la configuración actual
    """
    return MessageResponse(
        message="API funcionando correctamente",
        success=True
    )


@router.get(
    "/info",
    status_code=status.HTTP_200_OK,
    summary="Información de la API",
    description="Retorna información sobre la configuración actual"
)
async def api_info():
    """
    Información de la API

    Retorna información sobre la versión, configuración y estado
    """
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "robot_model": settings.ROBOT_MODEL,
        "debug_mode": settings.DEBUG,
        "script_file_path": settings.SCRIPT_FILE_PATH,
        "backup_dir": settings.BACKUP_DIR,
        "python_version": sys.version,
        "success": True
    }
