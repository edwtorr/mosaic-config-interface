# Visualización 3D del Robot UR16e

## Descripción

Sistema avanzado de visualización 3D que muestra el robot Universal Robots UR16e en tiempo real, incluyendo el efector final (plano aspirante con ventosas) y el producto a manipular.

## Características

### Robot UR16e
- Modelo 3D con dimensiones reales según especificaciones de Universal Robots
- 6 grados de libertad (DOF) completamente articulados
- Cinemática inversa simplificada para posicionamiento
- Visualización de todas las articulaciones y links
- Colores y materiales realistas con iluminación PBR

### Efector Final - Plano Aspirante
- Plano aspirante de dimensiones configurables (400x600mm por defecto)
- **Ventosas**:
  - 6 ventosas distribuidas en 2 filas x 3 columnas
  - Diámetro: 50mm cada una
  - Espaciado configurable
  - Representación realista con materiales metálicos
- Marco de soporte estructural
- Montaje configurable al flange del robot

### Producto/Caja
- Dimensiones configurables desde la configuración del programa
- Visualización con bordes y wireframe para mejor comprensión
- Colores diferenciados para identificación
- Sombras y materiales realistas

### Workspace del Robot
- Visualización del alcance máximo (900mm de radio)
- Cilindro transparente mostrando volumen de trabajo
- Límites de altura (min: -100mm, max: 1200mm)
- Verificación en tiempo real de límites

### Controles de Visualización

#### Vistas Predefinidas
- **Frontal**: Vista desde el frente del robot
- **Superior**: Vista desde arriba (bird's eye)
- **Lateral**: Vista desde el costado
- **Isométrica**: Vista 3D isométrica (por defecto)

#### Opciones de Visualización
- ✓ Mostrar workspace - Muestra/oculta el cilindro del workspace
- ✓ Mostrar grid - Muestra/oculta la cuadrícula del suelo
- ✓ Mostrar ejes - Muestra/oculta los ejes de coordenadas
- ✓ Mostrar trayectoria - Muestra la trayectoria de todos los puntos del mosaico

#### Controles de Cámara (OrbitControls)
- **Rotación**: Click izquierdo + arrastrar
- **Zoom**: Rueda del mouse
- **Pan**: Click derecho + arrastrar (o Shift + Click izquierdo + arrastrar)
- **Reset**: Doble click en cualquier vista predefinida

### Panel de Información
Muestra en tiempo real:
- **Posición TCP** (X, Y, Z) en milímetros
- **Orientación** (RX, RY, RZ) en grados
- **Estado de validación**: Indica si la posición está dentro de los límites del robot
  - ✓ Verde: Dentro de límites
  - ⚠ Rojo: Fuera de límites

## Especificaciones Técnicas

### Robot UR16e
```javascript
Dimensiones:
- Base: Ø95mm x 181mm altura
- Brazo superior: 478mm
- Brazo inferior: 478mm
- Muñeca 1: 117mm offset
- Muñeca 2: 117mm offset
- Muñeca 3 a flange: 115.5mm

Workspace:
- Alcance máximo: 900mm
- Altura mínima: -100mm
- Altura máxima: 1200mm
- Payload: 16kg
```

### Plano Aspirante
```javascript
Dimensiones:
- Ancho: 400mm
- Largo: 600mm
- Grosor placa: 20mm
- Altura al flange: 50mm

Ventosas:
- Cantidad: 6 (2 filas x 3 columnas)
- Diámetro: 50mm
- Espaciado X: 150mm
- Espaciado Y: 200mm
```

### Producto (Configurable)
```javascript
Dimensiones por defecto:
- Ancho: 400mm
- Largo: 600mm
- Alto: 150mm
- Peso: 8kg (típico)
```

## Implementación Técnica

### Tecnologías Utilizadas
- **Three.js**: Renderizado 3D WebGL
- **OrbitControls**: Controles de cámara interactivos
- **Vue 3 Composition API**: Integración reactiva
- **WebGL**: Aceleración por hardware

### Arquitectura de Componentes

```
src/
├── components/
│   └── Robot3DViewer.vue          # Componente principal de visualización 3D
├── utils/
│   └── ur16e-specs.js             # Especificaciones y constantes del robot
└── App.vue                         # Integración con la aplicación
```

### Flujo de Datos

```
Datos del Mosaico (API)
         ↓
   currentPose (computed)  ←  Punto seleccionado
         ↓
   Robot3DViewer Component
         ↓
   ├─ updateRobotPose()    # Calcula IK y actualiza posición
   ├─ createRobot()        # Construye geometría del robot
   ├─ createEndEffector()  # Construye plano aspirante
   ├─ createProduct()      # Construye modelo del producto
   └─ render loop          # Renderiza escena Three.js
```

### Cinemática Inversa (Simplificada)

El sistema utiliza una implementación simplificada de cinemática inversa basada en:
1. Ángulo de base (J1) calculado con atan2(y, x)
2. Posicionamiento 2D del brazo usando ley de cosenos
3. Orientación de muñecas basada en ángulos de Euler

**Nota**: Para producción se recomienda una implementación completa de IK con algoritmos como:
- DH (Denavit-Hartenberg) parameters
- Jacobian-based IK
- Numerical optimization (CCD, FABRIK)

## Integración con la Aplicación

### En App.vue

```vue
<script setup>
import Robot3DViewer from './components/Robot3DViewer.vue'

// Computed properties para el viewer 3D
const currentPose = computed(() => {
  // Retorna la pose actual del punto seleccionado
})

const productDimensions = computed(() => {
  // Retorna las dimensiones del producto desde el programa
})

const allPoses = computed(() => {
  // Retorna todos los puntos del mosaico para trayectoria
})
</script>

<template>
  <Robot3DViewer
    :pose="currentPose"
    :product-dimensions="productDimensions"
    :all-poses="allPoses"
  />
</template>
```

### Props del Componente

| Prop | Tipo | Descripción | Default |
|------|------|-------------|---------|
| `pose` | `Object` | Pose actual del TCP {x, y, z, rx, ry, rz} | `{x:0, y:-500, z:400, rx:0, ry:0, rz:0}` |
| `productDimensions` | `Object` | Dimensiones del producto {width, length, height} | `{width:400, length:600, height:150}` |
| `allPoses` | `Array` | Array de todas las poses del mosaico | `[]` |

## Uso

### Cambiar entre Vista 2D y 3D

1. En la interfaz principal, selecciona un mosaico
2. Usa los botones "Vista 2D" / "Vista 3D" en la parte superior
3. La vista 3D muestra el robot en la posición del primer punto válido del mosaico

### Visualizar un Punto Específico

1. En el editor de puntos, selecciona un punto específico
2. La vista 3D se actualizará automáticamente para mostrar el robot en esa posición
3. El panel de información muestra las coordenadas exactas

### Validar Posiciones

1. La visualización 3D muestra el workspace del robot
2. El indicador de estado muestra si la posición actual está dentro de límites
3. Usa el botón "Validar Configuración" para una validación completa

## Mejoras Futuras

### Fase 4 - Mejoras Actuales
- [x] Visualización 3D básica del robot
- [x] Modelo del efector final con ventosas
- [x] Visualización del producto
- [x] Workspace y límites
- [x] Controles de cámara interactivos
- [ ] Animación de trayectorias
- [ ] Simulación de movimiento entre puntos
- [ ] Detección de colisiones

### Fase 5 - Funcionalidades Avanzadas (Futuras)
- [ ] Cinemática inversa completa con múltiples soluciones
- [ ] Simulación de tiempo real del programa completo
- [ ] Visualización de velocidades y aceleraciones
- [ ] Gráficas de trayectorias en espacio de articulaciones
- [ ] Exportar animaciones como video
- [ ] Modelos 3D de otros modelos UR (UR3e, UR5e, UR10e, UR20e)
- [ ] Carga de modelos STL/OBJ personalizados para efectores finales
- [ ] Simulación de sensores de fuerza y visión
- [ ] Modo VR/AR para visualización inmersiva

## Notas de Rendimiento

- El renderizado usa WebGL con aceleración por hardware
- Antialiasing activado para mejor calidad visual
- Sombras soft con PCF shadow mapping
- Target: 60 FPS en hardware moderno
- Materiales PBR para realismo sin comprometer rendimiento

## Troubleshooting

### La escena 3D no se muestra
- Verificar que el navegador soporte WebGL
- Abrir consola del navegador y buscar errores de Three.js
- Verificar que el canvas tenga dimensiones válidas

### El robot no se mueve al cambiar de punto
- Verificar que el punto tenga coordenadas válidas (no todo en cero)
- Verificar que la prop `pose` esté cambiando correctamente
- Ver consola para errores de cinemática

### Rendimiento lento
- Reducir la calidad de sombras (shadowMap.mapSize)
- Desactivar antialiasing en renderer
- Reducir geometría del robot (menos segmentos en cilindros/esferas)

## Referencias

- [Universal Robots UR16e Specs](https://www.universal-robots.com/products/ur16-robot/)
- [Three.js Documentation](https://threejs.org/docs/)
- [OrbitControls](https://threejs.org/docs/#examples/en/controls/OrbitControls)
- [Denavit-Hartenberg Parameters](https://en.wikipedia.org/wiki/Denavit%E2%80%93Hartenberg_parameters)

---

**Versión**: 1.0.0
**Fecha**: 2025-01-27
**Autor**: Sistema de Configuración de Mosaicos L16
