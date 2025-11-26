"""
Tests unitarios para el parser de archivos .script
"""

import pytest
import sys
from pathlib import Path

# Agregar el directorio padre al path para importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.parser import URScriptParser, parse_script_file


# Path al archivo de prueba
TEST_SCRIPT_PATH = r"C:\Users\V13_Sp2\Desktop\L16 - BACKUP\20205000045_0\002_008_L16_REC_AMB_MF.script"


class TestURScriptParser:
    """Tests para la clase URScriptParser"""

    def test_parser_initialization(self):
        """Test de inicialización del parser"""
        parser = URScriptParser(TEST_SCRIPT_PATH)
        assert parser.script_path.exists()
        assert len(parser.raw_content) > 0

    def test_parse_pose(self):
        """Test de parseo de poses individuales"""
        parser = URScriptParser(TEST_SCRIPT_PATH)

        # Pose válida
        pose_str = "p[1.04122, 0.73691, 0.32186, -3.1356, -0.00672, -0.01102]"
        pose = parser._parse_pose(pose_str)

        assert pose is not None
        assert pose['x'] == 1.04122
        assert pose['y'] == 0.73691
        assert pose['z'] == 0.32186
        assert pose['rx'] == -3.1356
        assert pose['ry'] == -0.00672
        assert pose['rz'] == -0.01102
        assert pose['is_valid'] == True

        # Pose de relleno
        fill_pose_str = "p[100, 100, 100, 0, 0, 0]"
        fill_pose = parser._parse_pose(fill_pose_str)

        assert fill_pose is not None
        assert fill_pose['is_valid'] == False

    def test_parse_int_array(self):
        """Test de parseo de arrays de enteros"""
        parser = URScriptParser(TEST_SCRIPT_PATH)

        array_str = "[1, 2, 3, 4, 5, 6, 7, 8]"
        array = parser._parse_int_array(array_str)

        assert len(array) == 8
        assert array == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_parse_bool_array(self):
        """Test de parseo de arrays de booleanos"""
        parser = URScriptParser(TEST_SCRIPT_PATH)

        array_str = "[True, False, True, False]"
        array = parser._parse_bool_array(array_str)

        assert len(array) == 4
        assert array == [True, False, True, False]

    def test_extract_global_variables(self):
        """Test de extracción de variables globales"""
        parser = URScriptParser(TEST_SCRIPT_PATH)
        variables = parser.extract_global_variables()

        assert len(variables) > 0
        assert 'P_Tipo1_Mos1' in variables
        assert 'PuntosCogida' in variables
        assert 'Rec_Mosaico' in variables

    def test_extract_mosaics(self):
        """Test de extracción de mosaicos"""
        parser = URScriptParser(TEST_SCRIPT_PATH)
        mosaics = parser.extract_mosaics()

        assert len(mosaics) > 0
        assert mosaics[0]['mosaic_id'] == 1
        assert 'type1' in mosaics[0]
        assert 'type2' in mosaics[0]
        assert len(mosaics[0]['type1']['points']) > 0

    def test_extract_pick_points(self):
        """Test de extracción de puntos de cogida"""
        parser = URScriptParser(TEST_SCRIPT_PATH)
        pick_points = parser.extract_pick_points()

        assert len(pick_points) > 0
        assert 'program_id' in pick_points[0]
        assert 'x' in pick_points[0]
        assert 'y' in pick_points[0]
        assert 'z' in pick_points[0]

    def test_extract_programs_config(self):
        """Test de extracción de configuración de programas"""
        parser = URScriptParser(TEST_SCRIPT_PATH)
        programs = parser.extract_programs_config()

        assert len(programs) > 0
        assert 'program_id' in programs[0]
        assert 'mosaic_id' in programs[0]
        assert 'config' in programs[0]
        assert 'n_moves_per_layer' in programs[0]['config']
        assert 'n_layers_total' in programs[0]['config']

    def test_parse_to_json(self):
        """Test de parseo completo a JSON"""
        parser = URScriptParser(TEST_SCRIPT_PATH)
        json_data = parser.parse_to_json()

        assert 'project_info' in json_data
        assert 'reference_frame' in json_data
        assert 'mosaics' in json_data
        assert 'pick_points' in json_data
        assert 'programs' in json_data

        assert len(json_data['mosaics']) > 0
        assert len(json_data['programs']) > 0

    def test_parse_script_file_function(self):
        """Test de función auxiliar parse_script_file"""
        json_data = parse_script_file(TEST_SCRIPT_PATH)

        assert json_data is not None
        assert 'mosaics' in json_data
        assert len(json_data['mosaics']) > 0


if __name__ == '__main__':
    # Ejecutar tests
    pytest.main([__file__, '-v'])
