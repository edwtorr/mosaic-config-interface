"""
Router para endpoints de programas
"""

from fastapi import APIRouter, HTTPException, status, Query, Body
from typing import List, Optional
import logging

from app.models import Program, MessageResponse, Pose
from app.services.parser import URScriptParser
from app.services.writer import URScriptWriter
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/programs",
    response_model=List[Program],
    status_code=status.HTTP_200_OK,
    summary="Listar programas",
    description="Retorna la lista de todos los programas configurados"
)
async def list_programs(
    script_path: Optional[str] = Query(None, description="Ruta al archivo .script")
):
    """
    Lista todos los programas configurados

    Args:
        script_path: Ruta opcional al archivo .script

    Returns:
        Lista de programas configurados
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
        programs = parser.extract_programs_config()
        pick_points = parser.extract_pick_points()

        # Combinar programas con sus puntos de cogida
        for program in programs:
            pick_point = next(
                (pp for pp in pick_points if pp['program_id'] == program['program_id']),
                None
            )
            program['pick_point'] = pick_point

        logger.info(f"Se encontraron {len(programs)} programas")
        return programs

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archivo no encontrado: {file_path}"
        )
    except Exception as e:
        logger.error(f"Error al listar programas: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al leer el archivo: {str(e)}"
        )


@router.get(
    "/programs/{program_id}",
    response_model=Program,
    status_code=status.HTTP_200_OK,
    summary="Obtener programa",
    description="Retorna la configuración de un programa específico"
)
async def get_program(
    program_id: int = Query(..., ge=1, le=10, description="ID del programa (1-10)"),
    script_path: Optional[str] = Query(None, description="Ruta al archivo .script")
):
    """
    Obtiene la configuración de un programa específico

    Args:
        program_id: ID del programa (1-10)
        script_path: Ruta opcional al archivo .script

    Returns:
        Configuración del programa
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
        programs = parser.extract_programs_config()
        pick_points = parser.extract_pick_points()

        # Buscar programa
        program = next((p for p in programs if p['program_id'] == program_id), None)

        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Programa {program_id} no encontrado o no configurado"
            )

        # Agregar punto de cogida
        pick_point = next(
            (pp for pp in pick_points if pp['program_id'] == program_id),
            None
        )
        program['pick_point'] = pick_point

        logger.info(f"Programa {program_id} obtenido exitosamente")
        return program

    except HTTPException:
        raise
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archivo no encontrado: {file_path}"
        )
    except Exception as e:
        logger.error(f"Error al obtener programa {program_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al leer el archivo: {str(e)}"
        )


@router.put(
    "/programs/{program_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar programa",
    description="Actualiza la configuración de un programa"
)
async def update_program(
    program_id: int = Query(..., ge=1, le=10, description="ID del programa (1-10)"),
    program: Program = Body(..., description="Nueva configuración del programa"),
    script_path: Optional[str] = Query(None, description="Ruta al archivo .script")
):
    """
    Actualiza la configuración de un programa

    Args:
        program_id: ID del programa
        program: Nueva configuración
        script_path: Ruta opcional al archivo .script

    Returns:
        Mensaje de confirmación
    """
    try:
        file_path = script_path or settings.SCRIPT_FILE_PATH

        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se ha especificado la ruta del archivo .script"
            )

        # Verificar que el ID coincida
        if program.program_id != program_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El ID del programa no coincide: {program.program_id} != {program_id}"
            )

        # Parsear archivo actual
        parser = URScriptParser(file_path)
        project_data = parser.parse_to_json()

        # Actualizar el programa
        program_found = False
        for idx, existing_program in enumerate(project_data['programs']):
            if existing_program['program_id'] == program_id:
                project_data['programs'][idx] = program.model_dump(exclude={'pick_point'})
                program_found = True
                break

        if not program_found:
            # Si el programa no existe, agregarlo
            project_data['programs'].append(program.model_dump(exclude={'pick_point'}))

        # Actualizar punto de cogida si está presente
        if program.pick_point:
            pick_point_found = False
            for idx, pick_point in enumerate(project_data['pick_points']):
                if pick_point['program_id'] == program_id:
                    project_data['pick_points'][idx] = program.pick_point.model_dump()
                    pick_point_found = True
                    break

            if not pick_point_found:
                # Agregar punto de cogida
                pick_point_data = program.pick_point.model_dump()
                pick_point_data['program_id'] = program_id
                project_data['pick_points'].append(pick_point_data)

        # Escribir cambios
        writer = URScriptWriter(file_path)
        writer.write_from_json(project_data, file_path, create_backup=True)

        logger.info(f"Programa {program_id} actualizado exitosamente")
        return MessageResponse(
            message=f"Programa {program_id} actualizado exitosamente. Backup creado.",
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
        logger.error(f"Error al actualizar programa {program_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el programa: {str(e)}"
        )


@router.get(
    "/pick-points",
    response_model=List[Pose],
    status_code=status.HTTP_200_OK,
    summary="Listar puntos de cogida",
    description="Retorna todos los puntos de cogida configurados"
)
async def list_pick_points(
    script_path: Optional[str] = Query(None, description="Ruta al archivo .script")
):
    """
    Lista todos los puntos de cogida

    Args:
        script_path: Ruta opcional al archivo .script

    Returns:
        Lista de puntos de cogida
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
        pick_points = parser.extract_pick_points()

        logger.info(f"Se encontraron {len(pick_points)} puntos de cogida")
        return pick_points

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archivo no encontrado: {file_path}"
        )
    except Exception as e:
        logger.error(f"Error al listar puntos de cogida: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al leer el archivo: {str(e)}"
        )
