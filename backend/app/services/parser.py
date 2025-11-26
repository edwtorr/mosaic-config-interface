"""
Parser de archivos .script de Universal Robots para el sistema L16

Este módulo se encarga de leer archivos .script y extraer la información
de configuración de mosaicos, puntos de cogida/dejada, órdenes, etc.
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path


class URScriptParser:
    """Parser para archivos .script de Universal Robots"""

    # Expresiones regulares para parsear
    POSE_PATTERN = r'p\[([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)\s*,\s*([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)\s*,\s*([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)\s*,\s*([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)\s*,\s*([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)\s*,\s*([-+]?\d+\.?\d*(?:[eE][-+]?\d+)?)\]'
    GLOBAL_VAR_PATTERN = r'global\s+(\w+)\s*=\s*(.+?)(?=\n\s*global|\n\s*#|$)'
    ARRAY_START_PATTERN = r'\[(.+?)\]'

    # Valor de relleno para detectar posiciones no utilizadas
    FILL_VALUES = [
        (100.0, 100.0, 100.0, 0.0, 0.0, 0.0),
        (101.01096, -99.91437, 100.89848, -0.00094, -0.00016, -1.56718)
    ]

    def __init__(self, script_path: str):
        """
        Inicializa el parser con la ruta al archivo .script principal

        Args:
            script_path: Ruta al archivo .script principal (ej: 002_008_L16_REC_AMB_MF.script)
        """
        self.script_path = Path(script_path)
        if not self.script_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {script_path}")

        self.raw_content = ""
        self.variables = {}
        self._load_file()

    def _load_file(self):
        """Carga el contenido del archivo .script"""
        with open(self.script_path, 'r', encoding='utf-8') as f:
            self.raw_content = f.read()

    def _parse_pose(self, pose_str: str) -> Optional[Dict[str, float]]:
        """
        Parsea una pose en formato p[x, y, z, rx, ry, rz]

        Args:
            pose_str: String con formato "p[x, y, z, rx, ry, rz]"

        Returns:
            Dict con keys: x, y, z, rx, ry, rz o None si no es válido
        """
        match = re.search(self.POSE_PATTERN, pose_str)
        if not match:
            return None

        x, y, z, rx, ry, rz = map(float, match.groups())

        # Verificar si es un valor de relleno
        is_valid = True
        for fill_x, fill_y, fill_z, fill_rx, fill_ry, fill_rz in self.FILL_VALUES:
            if (abs(x - fill_x) < 0.001 and
                abs(y - fill_y) < 0.001 and
                abs(z - fill_z) < 0.001):
                is_valid = False
                break

        return {
            'x': x,
            'y': y,
            'z': z,
            'rx': rx,
            'ry': ry,
            'rz': rz,
            'is_valid': is_valid
        }

    def _parse_pose_array(self, array_str: str) -> List[Dict[str, float]]:
        """
        Parsea un array de poses

        Args:
            array_str: String con formato "[p[...], p[...], ...]"

        Returns:
            Lista de dicts con poses parseadas
        """
        poses = []
        for pose_match in re.finditer(self.POSE_PATTERN, array_str):
            pose_str = f"p[{pose_match.group(0)[2:]}"
            pose = self._parse_pose(pose_str)
            if pose:
                poses.append(pose)

        return poses

    def _parse_int_array(self, array_str: str) -> List[int]:
        """
        Parsea un array de enteros

        Args:
            array_str: String con formato "[1, 2, 3, ...]"

        Returns:
            Lista de enteros
        """
        # Extraer contenido entre corchetes
        match = re.search(r'\[(.+)\]', array_str, re.DOTALL)
        if not match:
            return []

        content = match.group(1)
        # Dividir por comas y convertir a int
        values = []
        for item in content.split(','):
            item = item.strip()
            if item:
                try:
                    values.append(int(item))
                except ValueError:
                    pass

        return values

    def _parse_bool_array(self, array_str: str) -> List[bool]:
        """
        Parsea un array de booleanos

        Args:
            array_str: String con formato "[True, False, ...]"

        Returns:
            Lista de booleanos
        """
        # Extraer contenido entre corchetes
        match = re.search(r'\[(.+)\]', array_str, re.DOTALL)
        if not match:
            return []

        content = match.group(1)
        values = []
        for item in content.split(','):
            item = item.strip()
            if item == 'True':
                values.append(True)
            elif item == 'False':
                values.append(False)

        return values

    def _parse_float_array(self, array_str: str) -> List[float]:
        """
        Parsea un array de floats

        Args:
            array_str: String con formato "[1.0, 2.5, ...]"

        Returns:
            Lista de floats
        """
        match = re.search(r'\[(.+)\]', array_str, re.DOTALL)
        if not match:
            return []

        content = match.group(1)
        values = []
        for item in content.split(','):
            item = item.strip()
            if item:
                try:
                    values.append(float(item))
                except ValueError:
                    pass

        return values

    def extract_global_variables(self) -> Dict[str, Any]:
        """
        Extrae todas las variables globales del archivo

        Returns:
            Dict con todas las variables globales encontradas
        """
        variables = {}

        # Buscar todas las líneas con "global"
        for match in re.finditer(self.GLOBAL_VAR_PATTERN, self.raw_content, re.DOTALL | re.MULTILINE):
            var_name = match.group(1)
            var_value_str = match.group(2).strip()

            # Determinar el tipo de variable
            if 'p[' in var_value_str:
                if var_value_str.startswith('p['):
                    # Variable pose simple
                    variables[var_name] = self._parse_pose(var_value_str)
                elif var_value_str.startswith('['):
                    # Array de poses
                    variables[var_name] = self._parse_pose_array(var_value_str)
            elif var_value_str.startswith('['):
                # Detectar tipo de array
                if 'True' in var_value_str or 'False' in var_value_str:
                    variables[var_name] = self._parse_bool_array(var_value_str)
                elif '.' in var_value_str or 'e' in var_value_str.lower():
                    variables[var_name] = self._parse_float_array(var_value_str)
                else:
                    variables[var_name] = self._parse_int_array(var_value_str)
            elif var_value_str in ['True', 'False']:
                variables[var_name] = var_value_str == 'True'
            elif '.' in var_value_str or 'e' in var_value_str.lower() or 'E' in var_value_str:
                try:
                    variables[var_name] = float(var_value_str)
                except ValueError:
                    variables[var_name] = var_value_str
            else:
                try:
                    variables[var_name] = int(var_value_str)
                except ValueError:
                    variables[var_name] = var_value_str

        self.variables = variables
        return variables

    def extract_mosaics(self) -> List[Dict[str, Any]]:
        """
        Extrae información de todos los mosaicos configurados

        Returns:
            Lista de dicts con información de cada mosaico
        """
        if not self.variables:
            self.extract_global_variables()

        mosaics = []

        # Extraer mosaicos 1-12
        for mosaic_id in range(1, 13):
            tipo1_key = f'P_Tipo1_Mos{mosaic_id}'
            tipo2_key = f'P_Tipo2_Mos{mosaic_id}'
            orden_t1_key = f'ordenM{mosaic_id}_T1'
            orden_t2_key = f'ordenM{mosaic_id}_T2'
            movs2en2_t1_key = f'Movs2en2_M{mosaic_id}_T1'
            movs2en2_t2_key = f'Movs2en2_M{mosaic_id}_T2'

            # Verificar si el mosaico existe
            if tipo1_key not in self.variables:
                continue

            tipo1_points = self.variables.get(tipo1_key, [])
            tipo2_points = self.variables.get(tipo2_key, [])
            orden_t1 = self.variables.get(orden_t1_key, [])
            orden_t2 = self.variables.get(orden_t2_key, [])
            movs2en2_t1 = self.variables.get(movs2en2_t1_key, [])
            movs2en2_t2 = self.variables.get(movs2en2_t2_key, [])

            # Contar puntos válidos
            n_valid_t1 = sum(1 for p in tipo1_points if p.get('is_valid', False))
            n_valid_t2 = sum(1 for p in tipo2_points if p.get('is_valid', False))

            # Solo agregar si tiene puntos válidos
            if n_valid_t1 > 0 or n_valid_t2 > 0:
                mosaic = {
                    'mosaic_id': mosaic_id,
                    'name': f'Mosaico {mosaic_id}',
                    'description': f'Patrón de mosaico {mosaic_id}',
                    'type1': {
                        'points': [
                            {
                                'point_id': idx + 1,
                                **point
                            }
                            for idx, point in enumerate(tipo1_points)
                        ],
                        'n_valid_points': n_valid_t1,
                        'order': orden_t1,
                        'double_pick': movs2en2_t1
                    },
                    'type2': {
                        'points': [
                            {
                                'point_id': idx + 1,
                                **point
                            }
                            for idx, point in enumerate(tipo2_points)
                        ],
                        'n_valid_points': n_valid_t2,
                        'order': orden_t2,
                        'double_pick': movs2en2_t2
                    }
                }
                mosaics.append(mosaic)

        return mosaics

    def extract_pick_points(self) -> List[Dict[str, Any]]:
        """
        Extrae los puntos de cogida (PuntosCogida)

        Returns:
            Lista de puntos de cogida por programa
        """
        if not self.variables:
            self.extract_global_variables()

        pick_points_array = self.variables.get('PuntosCogida', [])

        pick_points = []
        for idx, point in enumerate(pick_points_array):
            if point and point.get('is_valid', False):
                pick_points.append({
                    'program_id': idx + 1,
                    **point
                })

        return pick_points

    def extract_programs_config(self) -> List[Dict[str, Any]]:
        """
        Extrae la configuración de programas (recetas)

        Returns:
            Lista de configuraciones de programa
        """
        if not self.variables:
            self.extract_global_variables()

        rec_mosaico = self.variables.get('Rec_Mosaico', [])
        rec_tipo_capa = self.variables.get('Rec_TipoCapa', [])
        rec_n_movs_capa = self.variables.get('Rec_NMovsCapa', [])
        rec_n_capas_tot = self.variables.get('Rec_NCapasTot', [])
        rec_cogida2en2 = self.variables.get('Rec_Cogida2en2', [])
        rec_carton = self.variables.get('Rec_Carton', [])
        rec_largo_prd = self.variables.get('Rec_LargoPrd', [])
        rec_ancho_prd = self.variables.get('Rec_AnchoPrd', [])
        rec_alto_prd = self.variables.get('Rec_AltoPrd', [])
        rec_peso_prd = self.variables.get('Rec_PesoPrd', [])

        programs = []
        for program_id in range(10):
            mosaic_id = rec_mosaico[program_id] if program_id < len(rec_mosaico) else 0
            n_moves = rec_n_movs_capa[program_id] if program_id < len(rec_n_movs_capa) else 0
            n_layers = rec_n_capas_tot[program_id] if program_id < len(rec_n_capas_tot) else 0

            # Solo agregar programas configurados
            if mosaic_id > 0 and n_moves > 0:
                # Extraer patrón de capas
                layer_pattern = rec_tipo_capa[:n_layers] if n_layers <= len(rec_tipo_capa) else []

                program = {
                    'program_id': program_id + 1,
                    'mosaic_id': mosaic_id,
                    'config': {
                        'n_moves_per_layer': n_moves,
                        'n_layers_total': n_layers,
                        'layer_pattern': layer_pattern,
                        'double_pick': rec_cogida2en2[program_id] if program_id < len(rec_cogida2en2) else False,
                        'use_cardboard': rec_carton[program_id] if program_id < len(rec_carton) else False,
                        'product_dimensions': {
                            'length': rec_largo_prd[program_id] if program_id < len(rec_largo_prd) else 0,
                            'width': rec_ancho_prd[program_id] if program_id < len(rec_ancho_prd) else 0,
                            'height': rec_alto_prd[program_id] if program_id < len(rec_alto_prd) else 0,
                            'weight': rec_peso_prd[program_id] if program_id < len(rec_peso_prd) else 0.0
                        }
                    }
                }
                programs.append(program)

        return programs

    def extract_reference_frame(self) -> Dict[str, float]:
        """
        Extrae el marco de referencia (wObjDejadaRef)

        Returns:
            Dict con la pose del marco de referencia
        """
        if not self.variables:
            self.extract_global_variables()

        return self.variables.get('wObjDejadaRef', None)

    def parse_to_json(self) -> Dict[str, Any]:
        """
        Parsea todo el archivo y devuelve un dict JSON estructurado

        Returns:
            Dict con toda la información estructurada
        """
        self.extract_global_variables()

        # Información del proyecto
        project_name = self.script_path.stem

        data = {
            'project_info': {
                'name': project_name,
                'robot_model': 'UR16e',  # Por defecto, podría detectarse automáticamente
                'file_path': str(self.script_path),
                'version': '1.0'
            },
            'reference_frame': {
                'wObjDejadaRef': self.extract_reference_frame()
            },
            'mosaics': self.extract_mosaics(),
            'pick_points': self.extract_pick_points(),
            'programs': self.extract_programs_config()
        }

        return data

    def save_to_json_file(self, output_path: str):
        """
        Parsea y guarda el resultado en un archivo JSON

        Args:
            output_path: Ruta del archivo JSON de salida
        """
        data = self.parse_to_json()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Datos guardados en: {output_path}")


# Funciones auxiliares de conveniencia

def parse_script_file(script_path: str) -> Dict[str, Any]:
    """
    Parsea un archivo .script y devuelve el JSON estructurado

    Args:
        script_path: Ruta al archivo .script

    Returns:
        Dict con toda la información estructurada
    """
    parser = URScriptParser(script_path)
    return parser.parse_to_json()


def parse_script_to_json_file(script_path: str, output_path: str):
    """
    Parsea un archivo .script y guarda el resultado en JSON

    Args:
        script_path: Ruta al archivo .script
        output_path: Ruta del archivo JSON de salida
    """
    parser = URScriptParser(script_path)
    parser.save_to_json_file(output_path)


# Script de ejemplo para testing
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Uso: python parser.py <ruta_al_archivo.script> [salida.json]")
        sys.exit(1)

    script_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'output.json'

    try:
        parse_script_to_json_file(script_path, output_path)
        print(f"[OK] Parseo completado exitosamente")
    except Exception as e:
        print(f"[ERROR] Error durante el parseo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
