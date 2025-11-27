"""
Router para endpoints de mosaicos
"""

from fastapi import APIRouter, HTTPException, status, Query, Body, Path
from typing import List, Optional
import logging

from app.models import (
    Mosaic,
    MessageResponse,
    ValidationResponse,
    ValidationError,
    MosaicPointUpdate
)
from app.services.parser import URScriptParser
from app.services.writer import URScriptWriter
from app.services.validator import validate_mosaic, validate_pose
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/mosaics",
    response_model=List[Mosaic],
    status_code=status.HTTP_200_OK,
    summary="Listar mosaicos",
    description="Retorna la lista de todos los mosaicos configurados"
)
async def list_mosaics(
    script_path: Optional[str] = Query(
        None,
        description="Ruta al archivo .script. Si no se proporciona, usa la ruta configurada"
    )
):
    """
    Lista todos los mosaicos configurados en el archivo .script

    Args:
        script_path: Ruta opcional al archivo .script

    Returns:
        Lista de mosaicos

    Raises:
        HTTPException: Si el archivo no existe o hay error al parsear
    """
    try:
        # Usar ruta proporcionada o configurada
        file_path = script_path or settings.SCRIPT_FILE_PATH

        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se ha especificado la ruta del archivo .script"
            )

        # Parsear archivo
        parser = URScriptParser(file_path)
        mosaics = parser.extract_mosaics()

        logger.info(f"Se encontraron {len(mosaics)} mosaicos")
        return mosaics

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archivo no encontrado: {file_path}"
        )
    except Exception as e:
        logger.error(f"Error al listar mosaicos: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al leer el archivo: {str(e)}"
        )


@router.get(
    "/mosaics/{mosaic_id}",
    response_model=Mosaic,
    status_code=status.HTTP_200_OK,
    summary="Obtener mosaico",
    description="Retorna la configuración de un mosaico específico"
)
async def get_mosaic(
    mosaic_id: int = Path(..., ge=1, le=12, description="ID del mosaico (1-12)"),
    script_path: Optional[str] = Query(None, description="Ruta al archivo .script")
):
    """
    Obtiene la configuración de un mosaico específico

    Args:
        mosaic_id: ID del mosaico (1-12)
        script_path: Ruta opcional al archivo .script

    Returns:
        Configuración del mosaico

    Raises:
        HTTPException: Si el mosaico no existe o hay error al parsear
    """
    try:
        file_path = script_path or settings.SCRIPT_FILE_PATH

        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se ha especificado la ruta del archivo .script"
            )

        # Parsear archivo
        parser = URScriptParser(file_path)
        mosaics = parser.extract_mosaics()

        # Buscar mosaico
        mosaic = next((m for m in mosaics if m['mosaic_id'] == mosaic_id), None)

        if not mosaic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mosaico {mosaic_id} no encontrado o no configurado"
            )

        logger.info(f"Mosaico {mosaic_id} obtenido exitosamente")
        return mosaic

    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archivo no encontrado: {file_path}"
        )
    except Exception as e:
        logger.error(f"Error al obtener mosaico {mosaic_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al leer el archivo: {str(e)}"
        )


@router.put(
    "/mosaics/{mosaic_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar mosaico",
    description="Actualiza la configuración completa de un mosaico"
)
async def update_mosaic(
    mosaic_id: int = Path(..., ge=1, le=12, description="ID del mosaico (1-12)"),
    mosaic: Mosaic = Body(..., description="Nueva configuración del mosaico"),
    script_path: Optional[str] = Query(None, description="Ruta al archivo .script"),
    validate_only: bool = Query(False, description="Solo validar sin guardar cambios")
):
    """
    Actualiza la configuración completa de un mosaico

    Args:
        mosaic_id: ID del mosaico a actualizar
        mosaic: Nueva configuración del mosaico
        script_path: Ruta opcional al archivo .script
        validate_only: Si True, solo valida sin guardar

    Returns:
        Mensaje de confirmación

    Raises:
        HTTPException: Si hay errores de validación o al escribir
    """
    try:
        file_path = script_path or settings.SCRIPT_FILE_PATH

        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se ha especificado la ruta del archivo .script"
            )

        # Verificar que el ID coincida
        if mosaic.mosaic_id != mosaic_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El ID del mosaico no coincide: {mosaic.mosaic_id} != {mosaic_id}"
            )

        # Validar el mosaico
        validation_result = validate_mosaic(mosaic.model_dump(), settings.ROBOT_MODEL)

        if not validation_result['is_valid']:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Errores de validación",
                    "errors": validation_result['errors']
                }
            )

        # Si solo es validación, retornar
        if validate_only:
            logger.info(f"Validación exitosa para mosaico {mosaic_id}")
            return MessageResponse(
                message="Validación exitosa. No se guardaron cambios.",
                success=True
            )

        # Parsear archivo actual para obtener todos los datos
        parser = URScriptParser(file_path)
        project_data = parser.parse_to_json()

        # Actualizar el mosaico específico
        mosaic_found = False
        for idx, existing_mosaic in enumerate(project_data['mosaics']):
            if existing_mosaic['mosaic_id'] == mosaic_id:
                project_data['mosaics'][idx] = mosaic.model_dump()
                mosaic_found = True
                break

        if not mosaic_found:
            # Si el mosaico no existe, agregarlo
            project_data['mosaics'].append(mosaic.model_dump())

        # Escribir cambios con backup
        writer = URScriptWriter(file_path)
        writer.write_from_json(project_data, file_path, create_backup=True)

        logger.info(f"Mosaico {mosaic_id} actualizado exitosamente")
        return MessageResponse(
            message=f"Mosaico {mosaic_id} actualizado exitosamente. Backup creado.",
            success=True
        )

    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archivo no encontrado: {file_path}"
        )
    except Exception as e:
        logger.error(f"Error al actualizar mosaico {mosaic_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el mosaico: {str(e)}"
        )


@router.patch(
    "/mosaics/{mosaic_id}/points",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar punto de mosaico",
    description="Actualiza un punto específico de un mosaico"
)
async def update_mosaic_point(
    mosaic_id: int = Path(..., ge=1, le=12, description="ID del mosaico (1-12)"),
    update: MosaicPointUpdate = Body(..., description="Datos de actualización del punto"),
    script_path: Optional[str] = Query(None, description="Ruta al archivo .script")
):
    """
    Actualiza un punto específico de un mosaico

    Args:
        mosaic_id: ID del mosaico
        update: Datos de actualización (layer_type, point_id, pose)
        script_path: Ruta opcional al archivo .script

    Returns:
        Mensaje de confirmación

    Raises:
        HTTPException: Si hay errores de validación o al escribir
    """
    try:
        file_path = script_path or settings.SCRIPT_FILE_PATH

        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se ha especificado la ruta del archivo .script"
            )

        # Parsear archivo actual
        parser = URScriptParser(file_path)
        project_data = parser.parse_to_json()

        # Buscar el mosaico
        mosaic = next((m for m in project_data['mosaics'] if m['mosaic_id'] == mosaic_id), None)

        if not mosaic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mosaico {mosaic_id} no encontrado"
            )

        # Determinar qué tipo de capa actualizar
        layer_key = 'type1' if update.layer_type == 1 else 'type2'
        points = mosaic[layer_key]['points']

        # Buscar el punto
        point_idx = update.point_id - 1  # Convertir a índice 0-based

        if point_idx < 0 or point_idx >= len(points):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Punto {update.point_id} no existe en el mosaico"
            )

        # Actualizar solo los campos proporcionados
        point = points[point_idx]
        for field, value in update.pose.model_dump(exclude_unset=True).items():
            if value is not None:
                point[field] = value

        # Validar el punto actualizado
        validation_result = validate_pose(point, settings.ROBOT_MODEL)

        if not validation_result['is_valid']:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Errores de validación",
                    "errors": validation_result['errors']
                }
            )

        # Escribir cambios
        writer = URScriptWriter(file_path)
        writer.write_from_json(project_data, file_path, create_backup=True)

        logger.info(f"Punto {update.point_id} del mosaico {mosaic_id} actualizado exitosamente")
        return MessageResponse(
            message=f"Punto {update.point_id} actualizado exitosamente. Backup creado.",
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al actualizar punto: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el punto: {str(e)}"
        )


@router.post(
    "/mosaics/{mosaic_id}/validate",
    response_model=ValidationResponse,
    status_code=status.HTTP_200_OK,
    summary="Validar mosaico",
    description="Valida un mosaico sin guardarlo"
)
async def validate_mosaic_endpoint(
    mosaic_id: int = Path(..., ge=1, le=12, description="ID del mosaico (1-12)"),
    mosaic: Mosaic = Body(..., description="Configuración del mosaico a validar")
):
    """
    Valida un mosaico sin guardarlo

    Args:
        mosaic_id: ID del mosaico
        mosaic: Configuración del mosaico a validar

    Returns:
        Resultado de la validación
    """
    try:
        # Verificar que el ID coincida
        if mosaic.mosaic_id != mosaic_id:
            return ValidationResponse(
                is_valid=False,
                errors=[ValidationError(
                    field="mosaic_id",
                    error=f"El ID del mosaico no coincide: {mosaic.mosaic_id} != {mosaic_id}"
                )]
            )

        # Validar el mosaico
        validation_result = validate_mosaic(mosaic.model_dump(), settings.ROBOT_MODEL)

        return ValidationResponse(
            is_valid=validation_result['is_valid'],
            errors=[
                ValidationError(field=err['field'], error=err['error'])
                for err in validation_result['errors']
            ]
        )

    except Exception as e:
        logger.error(f"Error al validar mosaico: {e}", exc_info=True)
        return ValidationResponse(
            is_valid=False,
            errors=[ValidationError(
                field="general",
                error=f"Error en la validación: {str(e)}"
            )]
        )
