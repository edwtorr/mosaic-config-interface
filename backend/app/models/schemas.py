"""
Modelos Pydantic para validación de datos de la API

Define la estructura de datos para mosaicos, puntos, programas, etc.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum


class LayerType(int, Enum):
    """Tipo de capa en el mosaico"""
    TYPE_1 = 1
    TYPE_2 = 2


class Pose(BaseModel):
    """
    Modelo para una pose (posición + orientación) del robot

    Coordenadas en metros y radianes
    """
    point_id: Optional[int] = Field(None, description="ID del punto (1-based)")
    x: float = Field(..., description="Posición X en metros")
    y: float = Field(..., description="Posición Y en metros")
    z: float = Field(..., description="Posición Z en metros")
    rx: float = Field(..., description="Rotación RX en radianes")
    ry: float = Field(..., description="Rotación RY en radianes")
    rz: float = Field(..., description="Rotación RZ en radianes")
    is_valid: bool = Field(True, description="Indica si el punto es válido o es relleno")

    class Config:
        json_schema_extra = {
            "example": {
                "point_id": 1,
                "x": 1.04122,
                "y": 0.73691,
                "z": 0.32186,
                "rx": -3.1356,
                "ry": -0.00672,
                "rz": -0.01102,
                "is_valid": True
            }
        }


class LayerData(BaseModel):
    """
    Datos de una capa de mosaico (Tipo 1 o Tipo 2)
    """
    points: List[Pose] = Field(..., description="Lista de puntos de la capa")
    n_valid_points: int = Field(..., ge=0, description="Número de puntos válidos")
    order: List[int] = Field(..., description="Orden de visita de los puntos")
    double_pick: List[bool] = Field(..., description="Indica movimientos con cogida doble")

    @validator('order')
    def validate_order(cls, v, values):
        """Valida que el orden tenga sentido"""
        if len(v) > 0:
            # Los valores deben ser >= 1 (índices base-1)
            if any(val < 1 for val in v):
                raise ValueError("Los valores de orden deben ser >= 1")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "points": [
                    {
                        "point_id": 1,
                        "x": 1.04122,
                        "y": 0.73691,
                        "z": 0.32186,
                        "rx": -3.1356,
                        "ry": -0.00672,
                        "rz": -0.01102,
                        "is_valid": True
                    }
                ],
                "n_valid_points": 32,
                "order": [6, 7, 8, 3, 4, 5, 2, 1],
                "double_pick": [False, False, False, False]
            }
        }


class Mosaic(BaseModel):
    """
    Modelo para un patrón de mosaico completo
    """
    mosaic_id: int = Field(..., ge=1, le=12, description="ID del mosaico (1-12)")
    name: str = Field(..., description="Nombre del mosaico")
    description: Optional[str] = Field(None, description="Descripción del mosaico")
    type1: LayerData = Field(..., description="Datos de capas Tipo 1")
    type2: LayerData = Field(..., description="Datos de capas Tipo 2")

    class Config:
        json_schema_extra = {
            "example": {
                "mosaic_id": 1,
                "name": "Mosaico 1",
                "description": "Patrón principal 4x8 piezas",
                "type1": {
                    "points": [],
                    "n_valid_points": 32,
                    "order": [6, 7, 8, 3, 4, 5, 2, 1],
                    "double_pick": [False, False, False, False]
                },
                "type2": {
                    "points": [],
                    "n_valid_points": 32,
                    "order": [8, 7, 4, 5, 6, 1, 2, 3],
                    "double_pick": [False, False, False, False]
                }
            }
        }


class ProductDimensions(BaseModel):
    """Dimensiones del producto"""
    length: float = Field(..., ge=0, description="Largo en mm")
    width: float = Field(..., ge=0, description="Ancho en mm")
    height: float = Field(..., ge=0, description="Alto en mm")
    weight: float = Field(..., ge=0, description="Peso en kg")

    class Config:
        json_schema_extra = {
            "example": {
                "length": 280,
                "width": 97,
                "height": 160,
                "weight": 1.23
            }
        }


class ProgramConfig(BaseModel):
    """Configuración de un programa (receta)"""
    n_moves_per_layer: int = Field(..., ge=1, description="Número de movimientos por capa")
    n_layers_total: int = Field(..., ge=1, description="Número total de capas")
    layer_pattern: List[int] = Field(..., description="Patrón de capas (1 o 2)")
    double_pick: bool = Field(False, description="Indica si hay movimientos con cogida doble")
    use_cardboard: bool = Field(False, description="Indica si se usa cartón entre capas")
    product_dimensions: ProductDimensions = Field(..., description="Dimensiones del producto")

    @validator('layer_pattern')
    def validate_layer_pattern(cls, v, values):
        """Valida que el patrón de capas coincida con n_layers_total"""
        if 'n_layers_total' in values:
            if len(v) != values['n_layers_total']:
                raise ValueError("El patrón de capas debe tener la misma longitud que n_layers_total")
        # Verificar que solo contenga 1 o 2
        if any(layer not in [1, 2] for layer in v):
            raise ValueError("El patrón de capas solo puede contener valores 1 o 2")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "n_moves_per_layer": 32,
                "n_layers_total": 6,
                "layer_pattern": [1, 2, 1, 2, 1, 2],
                "double_pick": False,
                "use_cardboard": False,
                "product_dimensions": {
                    "length": 280,
                    "width": 97,
                    "height": 160,
                    "weight": 1.23
                }
            }
        }


class Program(BaseModel):
    """Modelo para un programa completo"""
    program_id: int = Field(..., ge=1, le=10, description="ID del programa (1-10)")
    mosaic_id: int = Field(..., ge=1, le=12, description="ID del mosaico usado")
    pick_point: Optional[Pose] = Field(None, description="Punto de cogida")
    config: ProgramConfig = Field(..., description="Configuración del programa")

    class Config:
        json_schema_extra = {
            "example": {
                "program_id": 1,
                "mosaic_id": 1,
                "pick_point": {
                    "x": -0.01294,
                    "y": -1.11748,
                    "z": -0.04056,
                    "rx": -2.21361,
                    "ry": -2.21498,
                    "rz": -0.00096,
                    "is_valid": True
                },
                "config": {
                    "n_moves_per_layer": 32,
                    "n_layers_total": 6,
                    "layer_pattern": [1, 2, 1, 2, 1, 2],
                    "double_pick": False,
                    "use_cardboard": False,
                    "product_dimensions": {
                        "length": 280,
                        "width": 97,
                        "height": 160,
                        "weight": 1.23
                    }
                }
            }
        }


class ReferenceFrame(BaseModel):
    """Marco de referencia del sistema de coordenadas"""
    wObjDejadaRef: Pose = Field(..., description="Sistema de coordenadas de referencia")

    class Config:
        json_schema_extra = {
            "example": {
                "wObjDejadaRef": {
                    "x": -0.35008,
                    "y": -0.59872,
                    "z": -0.87792,
                    "rx": 0.00094,
                    "ry": 0.00016,
                    "rz": 1.56717,
                    "is_valid": True
                }
            }
        }


class ProjectInfo(BaseModel):
    """Información del proyecto"""
    name: str = Field(..., description="Nombre del proyecto")
    robot_model: str = Field("UR16e", description="Modelo del robot")
    file_path: Optional[str] = Field(None, description="Ruta del archivo .script")
    version: str = Field("1.0", description="Versión del proyecto")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "L16_REC_AMB_MF",
                "robot_model": "UR16e",
                "file_path": "C:/path/to/script.script",
                "version": "1.0"
            }
        }


class ProjectData(BaseModel):
    """
    Modelo completo del proyecto con todos los datos
    """
    project_info: ProjectInfo = Field(..., description="Información del proyecto")
    reference_frame: ReferenceFrame = Field(..., description="Marco de referencia")
    mosaics: List[Mosaic] = Field(..., description="Lista de mosaicos")
    pick_points: List[Pose] = Field(..., description="Puntos de cogida")
    programs: List[Program] = Field(..., description="Programas configurados")

    class Config:
        json_schema_extra = {
            "example": {
                "project_info": {
                    "name": "L16_REC_AMB_MF",
                    "robot_model": "UR16e",
                    "version": "1.0"
                },
                "reference_frame": {
                    "wObjDejadaRef": {
                        "x": -0.35008,
                        "y": -0.59872,
                        "z": -0.87792,
                        "rx": 0.00094,
                        "ry": 0.00016,
                        "rz": 1.56717,
                        "is_valid": True
                    }
                },
                "mosaics": [],
                "pick_points": [],
                "programs": []
            }
        }


# Modelos para respuestas de la API

class MessageResponse(BaseModel):
    """Respuesta simple con mensaje"""
    message: str = Field(..., description="Mensaje de respuesta")
    success: bool = Field(True, description="Indica si la operación fue exitosa")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operación completada exitosamente",
                "success": True
            }
        }


class ValidationError(BaseModel):
    """Error de validación"""
    field: str = Field(..., description="Campo que falló la validación")
    error: str = Field(..., description="Descripción del error")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "x",
                "error": "El valor X está fuera del workspace del robot"
            }
        }


class ValidationResponse(BaseModel):
    """Respuesta de validación"""
    is_valid: bool = Field(..., description="Indica si los datos son válidos")
    errors: List[ValidationError] = Field([], description="Lista de errores de validación")

    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": False,
                "errors": [
                    {
                        "field": "mosaics[0].type1.points[5].x",
                        "error": "El punto está fuera del alcance del robot"
                    }
                ]
            }
        }


# Modelos para actualización parcial

class PoseUpdate(BaseModel):
    """Actualización de una pose específica"""
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    rx: Optional[float] = None
    ry: Optional[float] = None
    rz: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "x": 1.05,
                "y": 0.74
            }
        }


class MosaicPointUpdate(BaseModel):
    """Actualización de un punto específico de un mosaico"""
    mosaic_id: int = Field(..., ge=1, le=12)
    layer_type: LayerType = Field(...)
    point_id: int = Field(..., ge=1)
    pose: PoseUpdate = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "mosaic_id": 1,
                "layer_type": 1,
                "point_id": 5,
                "pose": {
                    "x": 1.05,
                    "y": 0.74
                }
            }
        }
