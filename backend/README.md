# Backend - API de Configuración de Mosaicos

Backend en Python con FastAPI para la gestión de configuraciones de mosaicos del robot paletizador L16.

## Tecnologías

- Python 3.10+
- FastAPI
- Pydantic
- Uvicorn

## Estructura

```
backend/
├── app/
│   ├── main.py              # Entry point de FastAPI
│   ├── config.py            # Configuración de la aplicación
│   ├── models/              # Modelos Pydantic
│   ├── routers/             # Endpoints de la API
│   ├── services/            # Lógica de negocio
│   │   ├── parser.py       # Parser de archivos .script
│   │   ├── writer.py       # Escritor de archivos .script
│   │   ├── validator.py    # Validaciones
│   │   └── backup.py       # Sistema de backup
│   └── utils/               # Utilidades
├── tests/                   # Tests unitarios y de integración
└── requirements.txt         # Dependencias
```

## Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

## Desarrollo

```bash
# Activar entorno virtual
venv\Scripts\activate

# Ejecutar servidor de desarrollo
uvicorn app.main:app --reload --port 8000

# Ejecutar tests
pytest

# Ver cobertura
pytest --cov=app tests/
```

## API Endpoints (Planificados)

### Mosaicos
- `GET /api/mosaics` - Listar todos los mosaicos
- `GET /api/mosaic/{id}` - Obtener configuración de un mosaico
- `PUT /api/mosaic/{id}` - Actualizar configuración de un mosaico
- `POST /api/mosaic/{id}/validate` - Validar configuración sin guardar

### Sistema
- `GET /api/health` - Health check
- `GET /api/backups` - Listar backups disponibles
- `POST /api/backup/{id}/restore` - Restaurar desde backup

## Documentación de la API

Una vez el servidor esté corriendo, la documentación automática estará disponible en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Estado del Desarrollo

Ver [PROGRESS.md](../PROGRESS.md) para el estado actual del proyecto.
