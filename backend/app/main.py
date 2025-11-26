"""
Punto de entrada principal de la API FastAPI
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.routers import mosaics, programs, health

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Manejadores de excepciones personalizados

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejador de excepciones HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejador de errores de validación"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Error de validación",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejador general de excepciones"""
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Error interno del servidor",
            "detail": str(exc) if settings.DEBUG else "Internal server error"
        }
    )


# Eventos de inicio y cierre

@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Modo DEBUG: {settings.DEBUG}")
    logger.info(f"Modelo de robot: {settings.ROBOT_MODEL}")

    # Crear directorio de backups si no existe
    backup_dir = Path(settings.BACKUP_DIR)
    if not backup_dir.exists():
        backup_dir.mkdir(parents=True)
        logger.info(f"Directorio de backups creado: {backup_dir}")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    logger.info(f"Cerrando {settings.APP_NAME}")


# Incluir routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(mosaics.router, prefix="/api", tags=["Mosaics"])
app.include_router(programs.router, prefix="/api", tags=["Programs"])


# Endpoint raíz
@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz de la API"""
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
