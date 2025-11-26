"""
Escritor de archivos .script de Universal Robots para el sistema L16

Este módulo se encarga de tomar datos en formato JSON y generar
archivos .script válidos manteniendo el formato original.
"""

import json
from typing import Dict, List, Any
from pathlib import Path
import re


class URScriptWriter:
    """Escritor para archivos .script de Universal Robots"""

    def __init__(self, template_path: str = None):
        """
        Inicializa el escritor

        Args:
            template_path: Ruta al archivo .script original para usar como plantilla
        """
        self.template_path = Path(template_path) if template_path else None
        self.template_content = ""

        if self.template_path and self.template_path.exists():
            self._load_template()

    def _load_template(self):
        """Carga el archivo plantilla"""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            self.template_content = f.read()

    def _format_pose(self, pose: Dict[str, float]) -> str:
        """
        Formatea una pose en formato URScript

        Args:
            pose: Dict con keys x, y, z, rx, ry, rz

        Returns:
            String en formato p[x, y, z, rx, ry, rz]
        """
        if pose is None:
            return "p[100, 100, 100, 0, 0, 0]"

        # Usar notación científica si los valores son muy pequeños
        def format_num(val):
            if abs(val) < 0.001 and val != 0:
                return f"{val:.17E}"
            else:
                return str(val)

        x = format_num(pose['x'])
        y = format_num(pose['y'])
        z = format_num(pose['z'])
        rx = format_num(pose['rx'])
        ry = format_num(pose['ry'])
        rz = format_num(pose['rz'])

        return f"p[{x}, {y}, {z}, {rx}, {ry}, {rz}]"

    def _format_pose_array(self, poses: List[Dict[str, float]], target_size: int = 25) -> str:
        """
        Formatea un array de poses

        Args:
            poses: Lista de dicts con poses
            target_size: Tamaño objetivo del array (rellena con valores por defecto)

        Returns:
            String en formato [p[...], p[...], ...]
        """
        formatted_poses = []

        for pose in poses:
            if pose is not None and pose.get('is_valid', False):
                formatted_poses.append(self._format_pose(pose))
            else:
                formatted_poses.append("p[100, 100, 100, 0, 0, 0]")

        # Rellenar hasta el tamaño objetivo si es necesario
        while len(formatted_poses) < target_size:
            formatted_poses.append("p[100, 100, 100, 0, 0, 0]")

        # Formatear con saltos de línea para mejor legibilidad
        return "[" + ", ".join(formatted_poses[:target_size]) + "]"

    def _format_int_array(self, values: List[int], target_size: int = 25) -> str:
        """
        Formatea un array de enteros

        Args:
            values: Lista de enteros
            target_size: Tamaño objetivo del array

        Returns:
            String en formato [1, 2, 3, ...]
        """
        formatted_values = [str(v) for v in values]

        # Rellenar hasta el tamaño objetivo
        while len(formatted_values) < target_size:
            formatted_values.append("1")

        return "[" + ", ".join(formatted_values[:target_size]) + "]"

    def _format_bool_array(self, values: List[bool], target_size: int = 25) -> str:
        """
        Formatea un array de booleanos

        Args:
            values: Lista de booleanos
            target_size: Tamaño objetivo del array

        Returns:
            String en formato [True, False, ...]
        """
        formatted_values = [str(v) for v in values]

        # Rellenar hasta el tamaño objetivo
        while len(formatted_values) < target_size:
            formatted_values.append("False")

        return "[" + ", ".join(formatted_values[:target_size]) + "]"

    def _format_float_array(self, values: List[float], target_size: int = 10) -> str:
        """
        Formatea un array de floats

        Args:
            values: Lista de floats
            target_size: Tamaño objetivo del array

        Returns:
            String en formato [1.0, 2.5, ...]
        """
        formatted_values = [str(v) for v in values]

        # Rellenar hasta el tamaño objetivo
        while len(formatted_values) < target_size:
            formatted_values.append("0")

        return "[" + ", ".join(formatted_values[:target_size]) + "]"

    def _replace_global_variable(self, content: str, var_name: str, var_value: str) -> str:
        """
        Reemplaza el valor de una variable global en el contenido

        Args:
            content: Contenido del archivo .script
            var_name: Nombre de la variable a reemplazar
            var_value: Nuevo valor de la variable

        Returns:
            Contenido con la variable reemplazada
        """
        # Patrón para encontrar la variable global
        pattern = rf'(global\s+{var_name}\s*=\s*)(.+?)(?=\n\s*global|\n\s*#|$)'

        def replacer(match):
            return match.group(1) + var_value

        new_content = re.sub(pattern, replacer, content, flags=re.DOTALL)

        # Si no se encontró la variable, agregarla al final (antes del último end o # end)
        if new_content == content:
            # Buscar la última línea con "global"
            lines = content.split('\n')
            last_global_idx = -1
            for i, line in enumerate(lines):
                if line.strip().startswith('global '):
                    last_global_idx = i

            if last_global_idx >= 0:
                # Insertar después de la última variable global
                new_line = f"  global {var_name}={var_value}"
                lines.insert(last_global_idx + 1, new_line)
                new_content = '\n'.join(lines)

        return new_content

    def update_mosaic_data(self, content: str, mosaic_data: Dict[str, Any]) -> str:
        """
        Actualiza los datos de los mosaicos en el contenido

        Args:
            content: Contenido del archivo .script
            mosaic_data: Dict con información de mosaicos

        Returns:
            Contenido actualizado
        """
        for mosaic in mosaic_data:
            mosaic_id = mosaic['mosaic_id']

            # Tipo 1
            tipo1_var = f"P_Tipo1_Mos{mosaic_id}"
            tipo1_points = [p for p in mosaic['type1']['points']]
            tipo1_value = self._format_pose_array(tipo1_points, target_size=25)
            content = self._replace_global_variable(content, tipo1_var, tipo1_value)

            # Tipo 2
            tipo2_var = f"P_Tipo2_Mos{mosaic_id}"
            tipo2_points = [p for p in mosaic['type2']['points']]
            tipo2_value = self._format_pose_array(tipo2_points, target_size=25)
            content = self._replace_global_variable(content, tipo2_var, tipo2_value)

            # Orden Tipo 1
            orden_t1_var = f"ordenM{mosaic_id}_T1"
            orden_t1_value = self._format_int_array(mosaic['type1']['order'], target_size=25)
            content = self._replace_global_variable(content, orden_t1_var, orden_t1_value)

            # Orden Tipo 2
            orden_t2_var = f"ordenM{mosaic_id}_T2"
            orden_t2_value = self._format_int_array(mosaic['type2']['order'], target_size=25)
            content = self._replace_global_variable(content, orden_t2_var, orden_t2_value)

            # Movimientos dobles Tipo 1
            movs2en2_t1_var = f"Movs2en2_M{mosaic_id}_T1"
            movs2en2_t1_value = self._format_bool_array(mosaic['type1']['double_pick'], target_size=25)
            content = self._replace_global_variable(content, movs2en2_t1_var, movs2en2_t1_value)

            # Movimientos dobles Tipo 2
            movs2en2_t2_var = f"Movs2en2_M{mosaic_id}_T2"
            movs2en2_t2_value = self._format_bool_array(mosaic['type2']['double_pick'], target_size=25)
            content = self._replace_global_variable(content, movs2en2_t2_var, movs2en2_t2_value)

        return content

    def update_pick_points(self, content: str, pick_points_data: List[Dict[str, Any]]) -> str:
        """
        Actualiza los puntos de cogida en el contenido

        Args:
            content: Contenido del archivo .script
            pick_points_data: Lista de puntos de cogida

        Returns:
            Contenido actualizado
        """
        # Crear array de 15 posiciones
        pick_points_array = [None] * 15

        for pick_point in pick_points_data:
            program_id = pick_point['program_id'] - 1  # Convertir a índice 0-based
            if 0 <= program_id < 15:
                pick_points_array[program_id] = pick_point

        # Formatear array
        pick_points_value = self._format_pose_array(pick_points_array, target_size=15)

        # Reemplazar en el contenido
        content = self._replace_global_variable(content, "PuntosCogida", pick_points_value)

        return content

    def update_programs_config(self, content: str, programs_data: List[Dict[str, Any]]) -> str:
        """
        Actualiza la configuración de programas (recetas) en el contenido

        Args:
            content: Contenido del archivo .script
            programs_data: Lista de configuraciones de programa

        Returns:
            Contenido actualizado
        """
        # Inicializar arrays de configuración
        rec_mosaico = [0] * 10
        rec_n_movs_capa = [0] * 10
        rec_n_capas_tot = [0] * 10
        rec_cogida2en2 = [False] * 10
        rec_carton = [False] * 10
        rec_largo_prd = [0] * 10
        rec_ancho_prd = [0] * 10
        rec_alto_prd = [0] * 10
        rec_peso_prd = [0.0] * 10

        # Llenar con datos de programas
        for program in programs_data:
            program_id = program['program_id'] - 1  # Convertir a índice 0-based
            if 0 <= program_id < 10:
                rec_mosaico[program_id] = program['mosaic_id']
                rec_n_movs_capa[program_id] = program['config']['n_moves_per_layer']
                rec_n_capas_tot[program_id] = program['config']['n_layers_total']
                rec_cogida2en2[program_id] = program['config']['double_pick']
                rec_carton[program_id] = program['config']['use_cardboard']
                rec_largo_prd[program_id] = program['config']['product_dimensions']['length']
                rec_ancho_prd[program_id] = program['config']['product_dimensions']['width']
                rec_alto_prd[program_id] = program['config']['product_dimensions']['height']
                rec_peso_prd[program_id] = program['config']['product_dimensions']['weight']

        # Reemplazar variables
        content = self._replace_global_variable(content, "Rec_Mosaico", self._format_int_array(rec_mosaico, 10))
        content = self._replace_global_variable(content, "Rec_NMovsCapa", self._format_int_array(rec_n_movs_capa, 10))
        content = self._replace_global_variable(content, "Rec_NCapasTot", self._format_int_array(rec_n_capas_tot, 10))
        content = self._replace_global_variable(content, "Rec_Cogida2en2", self._format_bool_array(rec_cogida2en2, 10))
        content = self._replace_global_variable(content, "Rec_Carton", self._format_bool_array(rec_carton, 10))
        content = self._replace_global_variable(content, "Rec_LargoPrd", self._format_int_array(rec_largo_prd, 10))
        content = self._replace_global_variable(content, "Rec_AnchoPrd", self._format_int_array(rec_ancho_prd, 10))
        content = self._replace_global_variable(content, "Rec_AltoPrd", self._format_int_array(rec_alto_prd, 10))
        content = self._replace_global_variable(content, "Rec_PesoPrd", self._format_float_array(rec_peso_prd, 10))

        return content

    def write_from_json(self, json_data: Dict[str, Any], output_path: str, create_backup: bool = True):
        """
        Escribe un archivo .script desde datos JSON

        Args:
            json_data: Datos en formato JSON
            output_path: Ruta del archivo .script de salida
            create_backup: Si True, crea un backup del archivo original
        """
        output_path = Path(output_path)

        # Cargar contenido base (plantilla o archivo existente)
        if output_path.exists():
            # Si el archivo existe, usarlo como base
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Crear backup
            if create_backup:
                backup_path = output_path.with_suffix('.script.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[OK] Backup creado: {backup_path}")

        elif self.template_path:
            # Usar plantilla
            content = self.template_content
        else:
            raise ValueError("No hay archivo de destino ni plantilla disponible")

        # Actualizar datos
        if 'mosaics' in json_data:
            content = self.update_mosaic_data(content, json_data['mosaics'])

        if 'pick_points' in json_data:
            content = self.update_pick_points(content, json_data['pick_points'])

        if 'programs' in json_data:
            content = self.update_programs_config(content, json_data['programs'])

        # Actualizar marco de referencia si está presente
        if 'reference_frame' in json_data and 'wObjDejadaRef' in json_data['reference_frame']:
            ref_frame = json_data['reference_frame']['wObjDejadaRef']
            if ref_frame:
                ref_frame_value = self._format_pose(ref_frame)
                content = self._replace_global_variable(content, "wObjDejadaRef", ref_frame_value)

        # Escribir archivo
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[OK] Archivo escrito: {output_path}")

    def write_from_json_file(self, json_file_path: str, output_path: str, create_backup: bool = True):
        """
        Escribe un archivo .script desde un archivo JSON

        Args:
            json_file_path: Ruta al archivo JSON
            output_path: Ruta del archivo .script de salida
            create_backup: Si True, crea un backup del archivo original
        """
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        self.write_from_json(json_data, output_path, create_backup)


# Funciones auxiliares de conveniencia

def write_script_from_json(json_data: Dict[str, Any], output_path: str, template_path: str = None, create_backup: bool = True):
    """
    Escribe un archivo .script desde datos JSON

    Args:
        json_data: Datos en formato JSON
        output_path: Ruta del archivo .script de salida
        template_path: Ruta al archivo plantilla (opcional)
        create_backup: Si True, crea un backup del archivo original
    """
    writer = URScriptWriter(template_path)
    writer.write_from_json(json_data, output_path, create_backup)


def write_script_from_json_file(json_file_path: str, output_path: str, template_path: str = None, create_backup: bool = True):
    """
    Escribe un archivo .script desde un archivo JSON

    Args:
        json_file_path: Ruta al archivo JSON
        output_path: Ruta del archivo .script de salida
        template_path: Ruta al archivo plantilla (opcional)
        create_backup: Si True, crea un backup del archivo original
    """
    writer = URScriptWriter(template_path)
    writer.write_from_json_file(json_file_path, output_path, create_backup)


# Script de ejemplo para testing
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print("Uso: python writer.py <archivo.json> <salida.script> [template.script]")
        sys.exit(1)

    json_file = sys.argv[1]
    output_file = sys.argv[2]
    template_file = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        write_script_from_json_file(json_file, output_file, template_file, create_backup=True)
        print(f"[OK] Escritura completada exitosamente")
    except Exception as e:
        print(f"[ERROR] Error durante la escritura: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
