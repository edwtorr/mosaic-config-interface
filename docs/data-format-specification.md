# Especificación de Formato de Datos - Sistema L16

## Introducción

Este documento describe el formato de datos utilizado en los archivos `.script` del sistema de paletizado L16 para robots Universal Robots.

## Archivos Principales

### 1. Archivo Principal: `002_008_L16_REC_AMB_MF.script`

Contiene todas las variables globales del sistema, incluyendo:
- Puntos de mosaico (P_Tipo1_MosX, P_Tipo2_MosX)
- Puntos de cogida (PuntosCogida)
- Orden de movimientos (ordenMX_TX)
- Configuración de recetas (Rec_*)
- Movimientos dobles (Movs2en2_MX_TX)

### 2. Archivos Modulares: `scripts/mosaicoX.script` (X = 1-12)

Archivos que gestionan la lógica de cada patrón de mosaico. Son plantillas con código idéntico que solo cambian el número de mosaico.

### 3. Archivos de Configuración

- `InitVariables.script`: Inicialización de variables de trabajo
- `AjustesUsuario.script`: Sistema de ajustes dinámicos
- `InitReg.script`: Inicialización de registros (casi vacío en este proyecto)

---

## Estructura de Datos Principal

### Formato de Puntos (Pose)

Los puntos se definen con el formato URScript `p[X, Y, Z, RX, RY, RZ]`:

```urscript
p[1.04122, 0.73691, 0.32186, -3.1356, -0.00672, -0.01102]
```

**Componentes:**
- `X, Y, Z`: Posición cartesiana en **metros**
- `RX, RY, RZ`: Rotación (eje-ángulo) en **radianes**

**Valor de relleno (posición no utilizada):**
```urscript
p[100, 100, 100, 0, 0, 0]
# O también:
p[101.01096, -99.91437, 100.89848, -0.00094, -0.00016, -1.56718]
```

---

## Variables Críticas del Sistema

### 1. Puntos de Mosaico

#### P_Tipo1_MosX (Tipo de Capa 1)
**Ubicación:** Archivo principal (líneas 35-45, 70)
**Formato:** Array de 25 poses
**Descripción:** Puntos de dejada para capas de Tipo 1 en Mosaico X

**Ejemplo:**
```urscript
global P_Tipo1_Mos1=[
  p[1.04122, 0.73691, 0.32186, -3.1356, -0.00672, -0.01102],  # Punto 1
  p[1.04157, 0.63991, 0.32193, -3.1356, -0.00674, -0.01104],  # Punto 2
  ...
  p[101.01096, -99.91437, 100.89848, -0.00094, -0.00016, -1.56718]  # No usado
]
```

#### P_Tipo2_MosX (Tipo de Capa 2)
**Ubicación:** Archivo principal (líneas 49-61)
**Formato:** Array de 25 poses
**Descripción:** Puntos de dejada para capas de Tipo 2 en Mosaico X

**Nota:** Los mosaicos 4-12 suelen estar inicializados con valores de relleno (100,100,100)

---

### 2. Puntos de Cogida

#### PuntosCogida
**Ubicación:** Archivo principal (línea 66)
**Formato:** Array de 15 poses
**Descripción:** Puntos donde el robot recoge las piezas para cada programa

**Ejemplo:**
```urscript
global PuntosCogida=[
  p[-0.01294, -1.11748, -0.04056, -2.21361, -2.21498, -0.00096],  # Programa 1
  p[-0.01294, -1.11748, -0.04056, -2.21361, -2.21498, -0.00096],  # Programa 2
  p[-0.01294, -1.11748, -0.04056, -2.21361, -2.21498, -0.00096],  # Programa 3
  p[100, 100, 100, 0, 0, 0],  # Programa 4 (no usado)
  ...
]
```

**Índice:** `PuntosCogida[Programa_1 - 1]`

---

### 3. Orden de Movimientos

#### ordenMX_T1 (Orden Tipo 1)
**Ubicación:** Archivo principal (líneas 98, 103, 109, etc.)
**Formato:** Array de 25 enteros
**Descripción:** Define el orden en que se visitan los puntos del Mosaico X, Tipo 1

**Ejemplo:**
```urscript
global ordenM1_T1=[6, 7, 8, 3, 4, 5, 2, 1, 14, 15, 16, 11, 12, 13, 10, 9, 22, 23, 24, 19, 20, 21, 18, 17, 30, 31, 32, 27, 28, 29, 26, 25, 1, 1, 1]
```

**Interpretación:**
- El primer movimiento va al punto 6
- El segundo movimiento va al punto 7
- El tercer movimiento va al punto 8
- etc.

#### ordenMX_T2 (Orden Tipo 2)
Similar a ordenMX_T1 pero para Tipo 2

**Ejemplo:**
```urscript
global ordenM1_T2=[8, 7, 4, 5, 6, 1, 2, 3, 16, 15, 12, 13, 14, 9, 10, 11, 24, 23, 20, 21, 22, 17, 18, 19, 32, 31, 28, 29, 30, 25, 26, 27, 1, 1, 1]
```

---

### 4. Movimientos Dobles (Cogida 2 en 2)

#### Movs2en2_MX_T1
**Ubicación:** Archivo principal (líneas 94-95, 100, 104, etc.)
**Formato:** Array de 25 booleanos
**Descripción:** Indica si cada movimiento recoge 2 piezas simultáneamente

**Ejemplo:**
```urscript
global Movs2en2_M1_T1=[False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
```

**Interpretación:**
- `True`: El movimiento recoge 2 piezas
- `False`: El movimiento recoge 1 pieza

---

### 5. Configuración de Recetas (Rec_*)

#### Rec_Mosaico
**Ubicación:** Archivo principal (línea 136)
**Formato:** Array de 10 enteros
**Descripción:** Número de mosaico asignado a cada programa

**Ejemplo:**
```urscript
global Rec_Mosaico=[1, 1, 3, 0, 0, 0, 0, 0, 0, 0]
```

**Interpretación:**
- Programa 1 usa Mosaico 1
- Programa 2 usa Mosaico 1
- Programa 3 usa Mosaico 3
- Programas 4-10 no están configurados (valor 0)

#### Rec_TipoCapa
**Ubicación:** Archivo principal (línea 68)
**Formato:** Array de 30 enteros
**Descripción:** Tipo de capa (1 o 2) para cada capa del pallet

**Ejemplo:**
```urscript
global Rec_TipoCapa=[1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2]
```

**Interpretación:**
- Capa 1: Tipo 1
- Capa 2: Tipo 2
- Capa 3: Tipo 1
- etc. (patrón alternado)

#### Rec_NMovsCapa
**Ubicación:** Archivo principal (línea 107)
**Formato:** Array de 10 enteros
**Descripción:** Número de movimientos por capa para cada programa

**Ejemplo:**
```urscript
global Rec_NMovsCapa=[32, 32, 0, 0, 0, 0, 0, 0, 0, 0]
```

**Interpretación:**
- Programa 1: 32 movimientos por capa
- Programa 2: 32 movimientos por capa

#### Rec_NCapasTot
**Ubicación:** Archivo principal (línea 112)
**Formato:** Array de 10 enteros
**Descripción:** Número total de capas por pallet para cada programa

**Ejemplo:**
```urscript
global Rec_NCapasTot=[6, 7, 7, 0, 0, 0, 0, 0, 0, 0]
```

#### Rec_Cogida2en2
**Ubicación:** Archivo principal (línea 79)
**Formato:** Array de 10 booleanos
**Descripción:** Indica si el programa tiene movimientos dobles

**Ejemplo:**
```urscript
global Rec_Cogida2en2=[False, False, False, False, False, False, False, False, False, False]
```

#### Rec_CapasTrab
**Ubicación:** Archivo principal (línea 114)
**Formato:** Array de 10 booleanos
**Descripción:** Indica si las capas están en modo de trabajo

**Ejemplo:**
```urscript
global Rec_CapasTrab=[True, True, True, False, False, False, False, False, False, False]
```

#### Rec_Carton
**Ubicación:** Archivo principal (línea 102)
**Formato:** Array de 10 booleanos
**Descripción:** Indica si se coloca cartón entre capas

#### Dimensiones del Producto

```urscript
global Rec_LargoPrd=[280, 280, 0, 0, 0, 0, 0, 0, 0, 0]    # mm
global Rec_AnchoPrd=[97, 97, 0, 0, 0, 0, 0, 0, 0, 0]      # mm
global Rec_AltoPrd=[160, 160, 0, 0, 0, 0, 0, 0, 0, 0]     # mm
global Rec_PesoPrd=[1.23, 1.23, 0, 0, 0, 0, 0, 0, 0, 0]   # kg
```

---

### 6. Variables de Estado

#### Programa_1
**Tipo:** Entero
**Descripción:** Número de programa actual (1-10)

#### linea
**Tipo:** Entero
**Descripción:** Número de línea de producción (1 o 2)

#### NCapaAct
**Formato:** Array de 2 enteros
**Descripción:** Número de capa actual por línea

```urscript
global NCapaAct=[1, 1]
```

#### NMovAct
**Formato:** Array de 2 enteros
**Descripción:** Número de movimiento actual por línea

```urscript
global NMovAct=[18, 1]
```

---

### 7. Variables de Referencia

#### wObjDejadaRef
**Tipo:** Pose
**Descripción:** Sistema de coordenadas de referencia para la zona de dejada

```urscript
global wObjDejadaRef=p[-0.3500863019098047,-0.5987226873651141,-0.8779278611891395,9.429729332248367E-4,1.637840708043976E-4,1.5671793604966087]
```

**Nota:** Las coordenadas de mosaico están relativizadas a este sistema de referencia

---

## Estructura de Archivos mosaicoX.script

Los archivos `mosaico1.script` a `mosaico12.script` tienen estructura idéntica:

```urscript
#MOSAICO X
#P_Tipo1 y P_Tipo2 tienen que venir ya relativizados del asistente!

if ModificarMos == True:
	P_Tipo1_MosX = P_Tipo1
	P_Tipo2_MosX = P_Tipo2
	ordenMX_T1 = orden_T1
	ordenMX_T2 = orden_T2
end

ModificarMos = False

P_Tipo1 = P_Tipo1_MosX
P_Tipo2 = P_Tipo2_MosX

# En caso de actualizar movimientos de 2 en 2
if Cogida2en2 == True:
	Movs2en2_MX_T1 = Movs2en2_Tipo1
	Movs2en2_MX_T2 = Movs2en2_Tipo2
end

Cogida2en2 = False

# Siempre, si hay algún movimiento doble, actualizo si el movimiento actual lo es o no
if Rec_Cogida2en2[Programa-1] == True:
	if Rec_TipoCapa[NCapaAct[linea-1]-1] == 1:
		Movs2en2 = Movs2en2_MX_T1
		if linea == 1:
			Movs2en2[NMovAct[linea-1]-1] = Movs2en2[ordenMX_T1[NMovAct[linea-1]-1]-1]
		end
	else:
		Movs2en2 = Movs2en2_MX_T2
		if linea == 1:
			Movs2en2[NMovAct[linea-1]-1] = Movs2en2[ordenMX_T2[NMovAct[linea-1]-1]-1]
		end
	end
else:
	Movs2en2[NMovAct[linea-1]-1] = False
end

if linea == 1:
    P_Tipo1[NMovAct[linea-1]-1] = P_Tipo1[ordenMX_T1[NMovAct[linea-1]-1]-1]
    P_Tipo2[NMovAct[linea-1]-1] = P_Tipo2[ordenMX_T2[NMovAct[linea-1]-1]-1]
end
```

**Patrón:** Solo cambia el número X del mosaico en todas las referencias

---

## Formato JSON Propuesto para la Interfaz

### Estructura Completa del Proyecto

```json
{
  "project_info": {
    "name": "L16_REC_AMB_MF",
    "robot_model": "UR16e",
    "version": "1.0",
    "last_modified": "2025-01-26T12:00:00Z"
  },
  "reference_frame": {
    "wObjDejadaRef": {
      "x": -0.3500863019098047,
      "y": -0.5987226873651141,
      "z": -0.8779278611891395,
      "rx": 9.429729332248367e-4,
      "ry": 1.637840708043976e-4,
      "rz": 1.5671793604966087
    }
  },
  "programs": [
    {
      "program_id": 1,
      "mosaic_id": 1,
      "pick_point": {
        "x": -0.01294,
        "y": -1.11748,
        "z": -0.04056,
        "rx": -2.21361,
        "ry": -2.21498,
        "rz": -0.00096
      },
      "config": {
        "n_moves_per_layer": 32,
        "n_layers_total": 6,
        "layer_pattern": [1, 2, 1, 2, 1, 2],
        "double_pick": false,
        "use_cardboard": false,
        "product_dimensions": {
          "length": 280,
          "width": 97,
          "height": 160,
          "weight": 1.23
        }
      }
    },
    {
      "program_id": 2,
      "mosaic_id": 1,
      "pick_point": {
        "x": -0.01294,
        "y": -1.11748,
        "z": -0.04056,
        "rx": -2.21361,
        "ry": -2.21498,
        "rz": -0.00096
      },
      "config": {
        "n_moves_per_layer": 32,
        "n_layers_total": 7,
        "layer_pattern": [1, 2, 1, 2, 1, 2, 1],
        "double_pick": false,
        "use_cardboard": false,
        "product_dimensions": {
          "length": 280,
          "width": 97,
          "height": 160,
          "weight": 1.23
        }
      }
    }
  ],
  "mosaics": [
    {
      "mosaic_id": 1,
      "name": "Mosaico 1",
      "description": "Patrón principal 4x8 piezas",
      "type1": {
        "points": [
          {
            "point_id": 1,
            "x": 1.04122,
            "y": 0.73691,
            "z": 0.32186,
            "rx": -3.1356,
            "ry": -0.00672,
            "rz": -0.01102,
            "is_valid": true
          },
          {
            "point_id": 2,
            "x": 1.04157,
            "y": 0.63991,
            "z": 0.32193,
            "rx": -3.1356,
            "ry": -0.00674,
            "rz": -0.01104,
            "is_valid": true
          }
          // ... más puntos
        ],
        "order": [6, 7, 8, 3, 4, 5, 2, 1, 14, 15, 16, 11, 12, 13, 10, 9, 22, 23, 24, 19, 20, 21, 18, 17, 30, 31, 32, 27, 28, 29, 26, 25],
        "double_pick": [false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false]
      },
      "type2": {
        "points": [
          {
            "point_id": 1,
            "x": 1.13563,
            "y": 0.65237,
            "z": 0.48446,
            "rx": -2.21948,
            "ry": 2.21033,
            "rz": -0.00109,
            "is_valid": true
          }
          // ... más puntos
        ],
        "order": [8, 7, 4, 5, 6, 1, 2, 3, 16, 15, 12, 13, 14, 9, 10, 11, 24, 23, 20, 21, 22, 17, 18, 19, 32, 31, 28, 29, 30, 25, 26, 27],
        "double_pick": [false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false, false]
      }
    },
    {
      "mosaic_id": 2,
      "name": "Mosaico 2",
      "description": "Patrón secundario",
      "type1": {
        "points": [
          // ... puntos
        ],
        "order": [7, 8, 9, 10, 12, 11, 2, 1, 3, 4, 5, 6],
        "double_pick": [false, false, false, false, false, false, false, false, false, false, false, false]
      },
      "type2": {
        "points": [
          // ... puntos
        ],
        "order": [8, 7, 9, 10, 11, 12, 1, 2, 3, 4, 6, 5],
        "double_pick": [false, false, false, false, false, false, false, false, false, false, false, false]
      }
    }
  ]
}
```

---

## Validaciones Necesarias

### 1. Validación de Puntos

```python
def validate_point(point):
    """
    Valida que un punto esté dentro de los límites del robot UR16e
    """
    # Workspace UR16e: alcance 900mm
    x, y, z = point['x'], point['y'], point['z']

    # Alcance máximo desde la base
    distance = math.sqrt(x**2 + y**2)
    if distance > 0.9:  # 900mm
        return False, "Punto fuera del alcance del robot"

    # Altura mínima (sobre la base del robot)
    if z < -0.1:  # -100mm
        return False, "Punto demasiado bajo"

    # Altura máxima
    if z > 1.2:  # 1200mm
        return False, "Punto demasiado alto"

    return True, "OK"
```

### 2. Validación de Orden

```python
def validate_order(order, n_valid_points):
    """
    Valida que el array de orden sea coherente
    """
    # Eliminar valores de relleno (1 repetido al final)
    valid_order = []
    for i, val in enumerate(order):
        if i > 0 and val == 1 and order[i-1] == 1:
            break
        valid_order.append(val)

    # Verificar que todos los puntos válidos aparezcan
    for i in range(1, n_valid_points + 1):
        if i not in valid_order:
            return False, f"Falta el punto {i} en el orden"

    return True, "OK"
```

### 3. Validación de Configuración

```python
def validate_program_config(program):
    """
    Valida la configuración de un programa
    """
    # Número de capas vs patrón de capas
    if len(program['config']['layer_pattern']) != program['config']['n_layers_total']:
        return False, "El patrón de capas no coincide con el número total"

    # Tipos de capa válidos (1 o 2)
    for layer_type in program['config']['layer_pattern']:
        if layer_type not in [1, 2]:
            return False, f"Tipo de capa inválido: {layer_type}"

    return True, "OK"
```

---

## Notas Importantes

### Coordenadas Relativizadas

Los puntos de mosaico están **relativizados** al sistema de referencia `wObjDejadaRef`. Para obtener las coordenadas absolutas del robot, se debe aplicar la transformación:

```python
punto_absoluto = pose_trans(wObjDejadaRef, punto_relativo)
```

### Valores de Relleno

Los valores `p[100, 100, 100, 0, 0, 0]` o `p[101.01096, -99.91437, 100.89848, ...]` indican posiciones no utilizadas y deben ser ignorados por el parser.

### Arrays de Tamaño Fijo

Todos los arrays tienen tamaño fijo (25 o 40 elementos) independientemente del número real de puntos utilizados. Los elementos no usados se rellenan con valores predeterminados.

### Índices Base-1 vs Base-0

- **URScript:** Usa índices base-0 (`array[0]` es el primer elemento)
- **orden arrays:** Contienen valores base-1 (el valor `1` se refiere al primer punto)
- **Programa_1:** Variable base-1 (Programa_1 = 1 es el primer programa)

---

## Resumen de Archivos a Parsear

| Archivo | Contenido | Prioridad |
|---------|-----------|-----------|
| `002_008_L16_REC_AMB_MF.script` | Variables globales (puntos, órdenes, configuración) | **ALTA** |
| `scripts/mosaicoX.script` | Lógica de mosaico (plantilla) | MEDIA |
| `InitVariables.script` | Inicialización de variables | BAJA |
| `AjustesUsuario.script` | Sistema de ajustes dinámicos | BAJA |

**Archivo prioritario para el parser:** `002_008_L16_REC_AMB_MF.script`

---

## Próximos Pasos

1. Implementar parser para extraer variables globales del archivo principal
2. Convertir datos a formato JSON estructurado
3. Implementar escritor para regenerar archivo .script desde JSON
4. Crear validadores de datos
5. Implementar tests unitarios

---

**Última actualización:** 2025-01-26
**Versión:** 1.0
