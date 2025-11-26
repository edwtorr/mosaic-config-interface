"""
Script de prueba para la API
"""

import requests
import json
import sys
from pathlib import Path

# Configuración
API_BASE_URL = "http://localhost:8000"
SCRIPT_FILE_PATH = r"C:\Users\V13_Sp2\Desktop\L16 - BACKUP\20205000045_0\002_008_L16_REC_AMB_MF.script"


def test_health():
    """Test del endpoint de health"""
    print("\n=== Test: Health Check ===")
    response = requests.get(f"{API_BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_info():
    """Test del endpoint de info"""
    print("\n=== Test: API Info ===")
    response = requests.get(f"{API_BASE_URL}/api/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_list_mosaics():
    """Test de listar mosaicos"""
    print("\n=== Test: List Mosaics ===")
    response = requests.get(
        f"{API_BASE_URL}/api/mosaics",
        params={"script_path": SCRIPT_FILE_PATH}
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Mosaicos encontrados: {len(data)}")
        for mosaic in data:
            print(f"  - Mosaico {mosaic['mosaic_id']}: {mosaic['name']}")
            print(f"    Tipo 1: {mosaic['type1']['n_valid_points']} puntos válidos")
            print(f"    Tipo 2: {mosaic['type2']['n_valid_points']} puntos válidos")
    else:
        print(f"Error: {response.text}")

    return response.status_code == 200


def test_get_mosaic(mosaic_id=1):
    """Test de obtener un mosaico específico"""
    print(f"\n=== Test: Get Mosaic {mosaic_id} ===")
    response = requests.get(
        f"{API_BASE_URL}/api/mosaics/{mosaic_id}",
        params={"script_path": SCRIPT_FILE_PATH}
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Mosaico: {data['name']}")
        print(f"Tipo 1: {data['type1']['n_valid_points']} puntos")
        print(f"Tipo 2: {data['type2']['n_valid_points']} puntos")
        # Mostrar primer punto válido de Tipo 1
        for point in data['type1']['points']:
            if point['is_valid']:
                print(f"Primer punto válido (Tipo 1): x={point['x']}, y={point['y']}, z={point['z']}")
                break
    else:
        print(f"Error: {response.text}")

    return response.status_code == 200


def test_list_programs():
    """Test de listar programas"""
    print("\n=== Test: List Programs ===")
    response = requests.get(
        f"{API_BASE_URL}/api/programs",
        params={"script_path": SCRIPT_FILE_PATH}
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Programas encontrados: {len(data)}")
        for program in data:
            print(f"  - Programa {program['program_id']}: Mosaico {program['mosaic_id']}")
            print(f"    {program['config']['n_moves_per_layer']} movs/capa, {program['config']['n_layers_total']} capas")
    else:
        print(f"Error: {response.text}")

    return response.status_code == 200


def test_list_pick_points():
    """Test de listar puntos de cogida"""
    print("\n=== Test: List Pick Points ===")
    response = requests.get(
        f"{API_BASE_URL}/api/pick-points",
        params={"script_path": SCRIPT_FILE_PATH}
    )
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Puntos de cogida encontrados: {len(data)}")
        for point in data:
            print(f"  - Programa {point['program_id']}: x={point['x']:.4f}, y={point['y']:.4f}, z={point['z']:.4f}")
    else:
        print(f"Error: {response.text}")

    return response.status_code == 200


def run_all_tests():
    """Ejecuta todos los tests"""
    print("=" * 60)
    print("PRUEBAS DE LA API")
    print("=" * 60)

    tests = [
        ("Health Check", test_health),
        ("API Info", test_info),
        ("List Mosaics", test_list_mosaics),
        ("Get Mosaic", lambda: test_get_mosaic(1)),
        ("List Programs", test_list_programs),
        ("List Pick Points", test_list_pick_points),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except requests.exceptions.ConnectionError:
            print(f"\n[ERROR] No se pudo conectar a {API_BASE_URL}")
            print("Asegúrate de que el servidor esté corriendo.")
            print("Ejecuta: python app/main.py")
            sys.exit(1)
        except Exception as e:
            print(f"\n[ERROR] Error en {test_name}: {e}")
            results.append((test_name, False))

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    print(f"\nTotal: {passed}/{total} pruebas pasadas")

    if passed == total:
        print("\n[SUCCESS] Todas las pruebas pasaron correctamente!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} prueba(s) fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
