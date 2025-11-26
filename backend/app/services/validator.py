"""
Servicio de validación de datos para mosaicos y poses

Valida que los puntos estén dentro de los límites del robot
y que cumplan con las restricciones de seguridad.
"""

import math
from typing import Dict, List, Any, Tuple
from app.config import get_robot_limits


def validate_pose(pose: Dict[str, Any], robot_model: str = "UR16e") -> Dict[str, Any]:
    """
    Valida una pose individual

    Args:
        pose: Dict con la pose a validar (x, y, z, rx, ry, rz)
        robot_model: Modelo del robot

    Returns:
        Dict con:
            - is_valid: bool
            - errors: List[Dict] con errores encontrados
    """
    errors = []
    limits = get_robot_limits(robot_model)

    # Si la pose no es válida (es relleno), no validar
    if not pose.get('is_valid', True):
        return {'is_valid': True, 'errors': []}

    x = pose.get('x', 0)
    y = pose.get('y', 0)
    z = pose.get('z', 0)

    # Calcular alcance desde la base (distancia radial en XY)
    reach = math.sqrt(x**2 + y**2)

    # Validar alcance máximo
    if reach > limits['max_reach']:
        errors.append({
            'field': 'x, y',
            'error': f'Punto fuera del alcance del robot. Distancia: {reach:.3f}m, Máximo: {limits["max_reach"]}m'
        })

    # Validar altura mínima
    if z < limits['min_z']:
        errors.append({
            'field': 'z',
            'error': f'Punto demasiado bajo. Z: {z:.3f}m, Mínimo: {limits["min_z"]}m'
        })

    # Validar altura máxima
    if z > limits['max_z']:
        errors.append({
            'field': 'z',
            'error': f'Punto demasiado alto. Z: {z:.3f}m, Máximo: {limits["max_z"]}m'
        })

    # Validar rotaciones (advertencia si son valores extremos)
    rx = pose.get('rx', 0)
    ry = pose.get('ry', 0)
    rz = pose.get('rz', 0)

    # Advertir si las rotaciones son mayores a 2*pi (posiblemente error)
    if abs(rx) > 2 * math.pi or abs(ry) > 2 * math.pi or abs(rz) > 2 * math.pi:
        errors.append({
            'field': 'rx, ry, rz',
            'error': f'Rotaciones con valores extremos. Verificar si están en radianes.'
        })

    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }


def validate_layer(layer: Dict[str, Any], robot_model: str = "UR16e") -> Dict[str, Any]:
    """
    Valida una capa de mosaico (Tipo 1 o Tipo 2)

    Args:
        layer: Dict con los datos de la capa
        robot_model: Modelo del robot

    Returns:
        Dict con resultados de validación
    """
    errors = []

    points = layer.get('points', [])
    order = layer.get('order', [])
    n_valid_points = layer.get('n_valid_points', 0)

    # Validar cada punto válido
    for idx, point in enumerate(points):
        if point.get('is_valid', False):
            point_validation = validate_pose(point, robot_model)
            if not point_validation['is_valid']:
                for error in point_validation['errors']:
                    errors.append({
                        'field': f'points[{idx}].{error["field"]}',
                        'error': error['error']
                    })

    # Validar que el número de puntos válidos coincida
    actual_valid = sum(1 for p in points if p.get('is_valid', False))
    if actual_valid != n_valid_points:
        errors.append({
            'field': 'n_valid_points',
            'error': f'El número de puntos válidos no coincide. Declarado: {n_valid_points}, Real: {actual_valid}'
        })

    # Validar orden
    if len(order) > 0:
        # Verificar que no haya valores fuera de rango
        valid_order_values = [v for v in order if v >= 1 and v <= len(points)]

        # Verificar que todos los puntos válidos aparezcan en el orden
        unique_order_values = set(valid_order_values)
        for i in range(1, n_valid_points + 1):
            if i not in unique_order_values:
                errors.append({
                    'field': 'order',
                    'error': f'Falta el punto {i} en el orden de visita'
                })
                break  # Solo reportar el primer error

    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }


def validate_mosaic(mosaic: Dict[str, Any], robot_model: str = "UR16e") -> Dict[str, Any]:
    """
    Valida un mosaico completo

    Args:
        mosaic: Dict con los datos del mosaico
        robot_model: Modelo del robot

    Returns:
        Dict con resultados de validación
    """
    errors = []

    mosaic_id = mosaic.get('mosaic_id', 0)

    # Validar ID
    if mosaic_id < 1 or mosaic_id > 12:
        errors.append({
            'field': 'mosaic_id',
            'error': f'ID de mosaico inválido: {mosaic_id}. Debe estar entre 1 y 12'
        })

    # Validar Tipo 1
    type1 = mosaic.get('type1', {})
    type1_validation = validate_layer(type1, robot_model)
    if not type1_validation['is_valid']:
        for error in type1_validation['errors']:
            errors.append({
                'field': f'type1.{error["field"]}',
                'error': error['error']
            })

    # Validar Tipo 2
    type2 = mosaic.get('type2', {})
    type2_validation = validate_layer(type2, robot_model)
    if not type2_validation['is_valid']:
        for error in type2_validation['errors']:
            errors.append({
                'field': f'type2.{error["field"]}',
                'error': error['error']
            })

    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }


def validate_program(program: Dict[str, Any], robot_model: str = "UR16e") -> Dict[str, Any]:
    """
    Valida un programa completo

    Args:
        program: Dict con los datos del programa
        robot_model: Modelo del robot

    Returns:
        Dict con resultados de validación
    """
    errors = []

    program_id = program.get('program_id', 0)
    mosaic_id = program.get('mosaic_id', 0)
    config = program.get('config', {})

    # Validar IDs
    if program_id < 1 or program_id > 10:
        errors.append({
            'field': 'program_id',
            'error': f'ID de programa inválido: {program_id}. Debe estar entre 1 y 10'
        })

    if mosaic_id < 1 or mosaic_id > 12:
        errors.append({
            'field': 'mosaic_id',
            'error': f'ID de mosaico inválido: {mosaic_id}. Debe estar entre 1 y 12'
        })

    # Validar punto de cogida si existe
    pick_point = program.get('pick_point')
    if pick_point:
        pick_validation = validate_pose(pick_point, robot_model)
        if not pick_validation['is_valid']:
            for error in pick_validation['errors']:
                errors.append({
                    'field': f'pick_point.{error["field"]}',
                    'error': error['error']
                })

    # Validar configuración
    n_moves = config.get('n_moves_per_layer', 0)
    n_layers = config.get('n_layers_total', 0)
    layer_pattern = config.get('layer_pattern', [])

    if n_moves < 1:
        errors.append({
            'field': 'config.n_moves_per_layer',
            'error': f'Número de movimientos por capa inválido: {n_moves}'
        })

    if n_layers < 1:
        errors.append({
            'field': 'config.n_layers_total',
            'error': f'Número de capas inválido: {n_layers}'
        })

    if len(layer_pattern) != n_layers:
        errors.append({
            'field': 'config.layer_pattern',
            'error': f'El patrón de capas debe tener {n_layers} elementos, tiene {len(layer_pattern)}'
        })

    # Validar que el patrón solo contenga 1 o 2
    if any(layer not in [1, 2] for layer in layer_pattern):
        errors.append({
            'field': 'config.layer_pattern',
            'error': 'El patrón de capas solo puede contener valores 1 o 2'
        })

    # Validar dimensiones del producto
    product_dims = config.get('product_dimensions', {})
    limits = get_robot_limits(robot_model)

    weight = product_dims.get('weight', 0)
    if weight > limits['max_payload']:
        errors.append({
            'field': 'config.product_dimensions.weight',
            'error': f'Peso del producto ({weight}kg) excede el payload máximo del robot ({limits["max_payload"]}kg)'
        })

    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }


def validate_project(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida un proyecto completo

    Args:
        project_data: Dict con todos los datos del proyecto

    Returns:
        Dict con resultados de validación
    """
    errors = []

    project_info = project_data.get('project_info', {})
    robot_model = project_info.get('robot_model', 'UR16e')

    # Validar mosaicos
    mosaics = project_data.get('mosaics', [])
    for idx, mosaic in enumerate(mosaics):
        mosaic_validation = validate_mosaic(mosaic, robot_model)
        if not mosaic_validation['is_valid']:
            for error in mosaic_validation['errors']:
                errors.append({
                    'field': f'mosaics[{idx}].{error["field"]}',
                    'error': error['error']
                })

    # Validar programas
    programs = project_data.get('programs', [])
    for idx, program in enumerate(programs):
        program_validation = validate_program(program, robot_model)
        if not program_validation['is_valid']:
            for error in program_validation['errors']:
                errors.append({
                    'field': f'programs[{idx}].{error["field"]}',
                    'error': error['error']
                })

    # Validar puntos de cogida
    pick_points = project_data.get('pick_points', [])
    for idx, pick_point in enumerate(pick_points):
        pick_validation = validate_pose(pick_point, robot_model)
        if not pick_validation['is_valid']:
            for error in pick_validation['errors']:
                errors.append({
                    'field': f'pick_points[{idx}].{error["field"]}',
                    'error': error['error']
                })

    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'total_errors': len(errors)
    }


# Funciones auxiliares

def calculate_reach(x: float, y: float) -> float:
    """
    Calcula el alcance radial desde la base del robot

    Args:
        x: Coordenada X en metros
        y: Coordenada Y en metros

    Returns:
        Distancia radial en metros
    """
    return math.sqrt(x**2 + y**2)


def is_within_workspace(pose: Dict[str, Any], robot_model: str = "UR16e") -> bool:
    """
    Verifica si una pose está dentro del workspace del robot

    Args:
        pose: Dict con la pose
        robot_model: Modelo del robot

    Returns:
        True si está dentro del workspace
    """
    validation = validate_pose(pose, robot_model)
    return validation['is_valid']
