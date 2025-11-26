"""
Configuración de la aplicación FastAPI
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Configuración de la aplicación

    Las variables pueden ser sobrescritas por variables de entorno
    """

    # Información de la aplicación
    APP_NAME: str = "Mosaic Config Interface API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API para configuración de mosaicos del sistema L16"

    # Configuración del servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternativa
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # Rutas de archivos
    SCRIPT_FILE_PATH: Optional[str] = None  # Se configurará en runtime
    BACKUP_DIR: str = "./backups"

    # Límites del robot UR16e (en metros)
    ROBOT_MODEL: str = "UR16e"
    ROBOT_MAX_REACH: float = 0.9  # 900mm
    ROBOT_MIN_Z: float = -0.1  # -100mm
    ROBOT_MAX_Z: float = 1.2  # 1200mm
    ROBOT_MAX_PAYLOAD: float = 16.0  # kg
    ROBOT_MAX_SPEED: float = 1.0  # m/s

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()


# Configuración de límites por modelo de robot
ROBOT_LIMITS = {
    "UR3": {
        "max_reach": 0.5,  # 500mm
        "min_z": -0.1,
        "max_z": 0.8,
        "max_payload": 3.0,
        "max_speed": 1.0
    },
    "UR3e": {
        "max_reach": 0.5,
        "min_z": -0.1,
        "max_z": 0.8,
        "max_payload": 3.0,
        "max_speed": 1.0
    },
    "UR5": {
        "max_reach": 0.85,  # 850mm
        "min_z": -0.1,
        "max_z": 1.0,
        "max_payload": 5.0,
        "max_speed": 1.0
    },
    "UR5e": {
        "max_reach": 0.85,
        "min_z": -0.1,
        "max_z": 1.0,
        "max_payload": 5.0,
        "max_speed": 1.0
    },
    "UR10": {
        "max_reach": 1.3,  # 1300mm
        "min_z": -0.1,
        "max_z": 1.5,
        "max_payload": 12.5,
        "max_speed": 1.0
    },
    "UR10e": {
        "max_reach": 1.3,
        "min_z": -0.1,
        "max_z": 1.5,
        "max_payload": 12.5,
        "max_speed": 1.0
    },
    "UR16e": {
        "max_reach": 0.9,  # 900mm
        "min_z": -0.1,
        "max_z": 1.2,
        "max_payload": 16.0,
        "max_speed": 1.0
    },
    "UR20": {
        "max_reach": 1.75,  # 1750mm
        "min_z": -0.1,
        "max_z": 2.0,
        "max_payload": 20.0,
        "max_speed": 1.5
    },
    "UR30": {
        "max_reach": 1.3,  # 1300mm
        "min_z": -0.1,
        "max_z": 1.5,
        "max_payload": 30.0,
        "max_speed": 1.5
    }
}


def get_robot_limits(robot_model: str) -> dict:
    """
    Obtiene los límites del robot según el modelo

    Args:
        robot_model: Modelo del robot (ej: "UR16e")

    Returns:
        Dict con los límites del robot
    """
    return ROBOT_LIMITS.get(robot_model, ROBOT_LIMITS["UR16e"])
