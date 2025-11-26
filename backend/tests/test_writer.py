"""
Tests unitarios para el escritor de archivos .script
"""

import pytest
import sys
import json
import tempfile
from pathlib import Path

# Agregar el directorio padre al path para importar los módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.writer import URScriptWriter, write_script_from_json
from app.services.parser import URScriptParser


# Path al archivo de prueba
TEST_SCRIPT_PATH = r"C:\Users\V13_Sp2\Desktop\L16 - BACKUP\20205000045_0\002_008_L16_REC_AMB_MF.script"


class TestURScriptWriter:
    """Tests para la clase URScriptWriter"""

    def test_writer_initialization(self):
        """Test de inicialización del escritor"""
        writer = URScriptWriter(TEST_SCRIPT_PATH)
        assert writer.template_path.exists()
        assert len(writer.template_content) > 0

    def test_format_pose(self):
        """Test de formateo de poses"""
        writer = URScriptWriter()

        pose = {
            'x': 1.04122,
            'y': 0.73691,
            'z': 0.32186,
            'rx': -3.1356,
            'ry': -0.00672,
            'rz': -0.01102
        }

        formatted = writer._format_pose(pose)
        assert formatted.startswith('p[')
        assert formatted.endswith(']')
        assert '1.04122' in formatted

    def test_format_pose_array(self):
        """Test de formateo de arrays de poses"""
        writer = URScriptWriter()

        poses = [
            {
                'x': 1.0,
                'y': 2.0,
                'z': 3.0,
                'rx': 0.0,
                'ry': 0.0,
                'rz': 0.0,
                'is_valid': True
            },
            {
                'x': 4.0,
                'y': 5.0,
                'z': 6.0,
                'rx': 0.0,
                'ry': 0.0,
                'rz': 0.0,
                'is_valid': True
            }
        ]

        formatted = writer._format_pose_array(poses, target_size=5)
        assert formatted.startswith('[')
        assert formatted.endswith(']')
        assert formatted.count('p[') == 5  # 2 válidos + 3 de relleno

    def test_format_int_array(self):
        """Test de formateo de arrays de enteros"""
        writer = URScriptWriter()

        values = [1, 2, 3, 4, 5]
        formatted = writer._format_int_array(values, target_size=10)

        assert formatted.startswith('[')
        assert formatted.endswith(']')
        assert '1' in formatted
        assert '5' in formatted

    def test_format_bool_array(self):
        """Test de formateo de arrays de booleanos"""
        writer = URScriptWriter()

        values = [True, False, True, False]
        formatted = writer._format_bool_array(values, target_size=8)

        assert formatted.startswith('[')
        assert formatted.endswith(']')
        assert 'True' in formatted
        assert 'False' in formatted

    def test_write_and_read_cycle(self):
        """Test de ciclo completo: parsear -> escribir -> parsear"""
        # Parsear archivo original
        parser = URScriptParser(TEST_SCRIPT_PATH)
        original_data = parser.parse_to_json()

        # Crear archivo temporal para escribir
        with tempfile.NamedTemporaryFile(mode='w', suffix='.script', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Escribir datos al archivo temporal
            writer = URScriptWriter(TEST_SCRIPT_PATH)
            writer.write_from_json(original_data, temp_path, create_backup=False)

            # Parsear el archivo escrito
            parser2 = URScriptParser(temp_path)
            regenerated_data = parser2.parse_to_json()

            # Verificar que los datos principales se mantienen
            assert len(original_data['mosaics']) == len(regenerated_data['mosaics'])
            assert len(original_data['programs']) == len(regenerated_data['programs'])

            # Verificar mosaicos
            for orig_mosaic, regen_mosaic in zip(original_data['mosaics'], regenerated_data['mosaics']):
                assert orig_mosaic['mosaic_id'] == regen_mosaic['mosaic_id']
                assert orig_mosaic['type1']['n_valid_points'] == regen_mosaic['type1']['n_valid_points']

        finally:
            # Limpiar archivo temporal
            Path(temp_path).unlink(missing_ok=True)

    def test_write_from_json_with_backup(self):
        """Test de creación de backup al escribir"""
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.script', delete=False) as temp_file:
            temp_file.write("# Test content\n")
            temp_path = temp_file.name

        try:
            # Parsear datos originales
            parser = URScriptParser(TEST_SCRIPT_PATH)
            data = parser.parse_to_json()

            # Escribir con backup
            writer = URScriptWriter(TEST_SCRIPT_PATH)
            writer.write_from_json(data, temp_path, create_backup=True)

            # Verificar que existe el backup
            backup_path = Path(temp_path).with_suffix('.script.backup')
            assert backup_path.exists()

            # Limpiar
            backup_path.unlink(missing_ok=True)

        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == '__main__':
    # Ejecutar tests
    pytest.main([__file__, '-v'])
