# Funcionalidades Tipo URSim

Sistema de control y simulación inspirado en URSim (Universal Robots Simulator) para la interfaz de configuración de mosaicos L16.

## Descripción General

Este sistema replica las funcionalidades principales de URSim, permitiendo controlar manualmente el robot UR16e y simular la ejecución de programas de paletizado con visualización 3D en tiempo real.

---

## 🎮 Panel de Control del Robot

### Modos de Control

El panel ofrece 3 modos de control, similares a URSim:

#### 1. **Position (Control Cartesiano)**
Control directo del TCP (Tool Center Point) en coordenadas cartesianas.

**Ejes de traslación:**
- **X, Y, Z**: Posición en el espacio (milímetros)
- Botones +/- para jog incremental
- Input numérico para valor exacto

**Ejes de rotación:**
- **RX, RY, RZ**: Orientación del TCP (grados)
- Control fino con pasos de 5°
- Visualización en tiempo real

**Características:**
- Movimiento suave con interpolación
- Verificación de límites del workspace
- Indicador visual de posición válida/inválida

#### 2. **Joints (Control de Articulaciones)**
Control individual de cada articulación del robot.

**6 Articulaciones:**
- **Base (J1)**: Rotación de la base
- **Shoulder (J2)**: Articulación del hombro
- **Elbow (J3)**: Articulación del codo
- **Wrist 1 (J4)**: Primera muñeca
- **Wrist 2 (J5)**: Segunda muñeca
- **Wrist 3 (J6)**: Tercera muñeca

**Rangos:**
- Cada articulación: ±360°
- Indicador de rango mínimo/máximo
- Limitación automática de ángulos

#### 3. **Freedrive**
Modo para mover el robot manualmente arrastrando el TCP en la vista 3D.

**Características:**
- Activación/desactivación con botón toggle
- Control directo con mouse en vista 3D
- Útil para teaching de puntos

### Control de Velocidad

**Slider de velocidad:**
- Rango: 1% - 100%
- Conversión a mm/s mostrada en tiempo real
- Presets rápidos: 10%, 25%, 50%, 100%

**Aplicación:**
- Afecta velocidad de jog
- Determina tamaño de paso en movimientos incrementales
- Control fino para posicionamiento preciso

### Acciones Rápidas

**Botones de acción:**
- **Home**: Lleva el robot a posición de referencia (0, -500, 400)
- **Guardar**: Almacena la posición actual
- **Reset**: Vuelve a la posición original del punto seleccionado

### Estado del Robot

**Indicadores visuales:**
- 🟢 **Detenido (Idle)**: Robot en reposo
- 🟡 **En movimiento (Moving)**: Robot ejecutando movimiento
- 🔴 **Error**: Posición fuera de límites o error de sistema

---

## 🎬 Simulador de Programa (Program Player)

### Timeline Interactivo

**Visualización de trayectoria:**
- Línea de tiempo con todos los puntos del mosaico
- Puntos numerados secuencialmente
- Estados visuales:
  - ⚪ Completados (verde)
  - 🔵 Actual (azul con halo)
  - ⚫ Pendientes (gris)
- Click en cualquier punto para saltar directamente

**Barra de progreso:**
- Indicador visual del avance
- Gradiente de color (azul → verde)
- Actualización en tiempo real

### Controles de Reproducción

**Controles principales:**
```
[⏮] [◀] [▶/⏸] [▶] [⏭] [⏹]
```

- **⏮ Inicio**: Salta al primer punto
- **◀ Paso atrás**: Retrocede un punto
- **▶/⏸ Play/Pause**: Reproduce o pausa (botón principal)
- **▶ Paso adelante**: Avanza un punto
- **⏭ Final**: Salta al último punto
- **⏹ Stop**: Detiene y resetea a inicio

**Estados del botón Play:**
- 🔵 Azul: Listo para reproducir
- 🟠 Naranja: Reproduciendo (cambia a Pause)
- Tamaño aumentado para fácil acceso

### Opciones de Reproducción

**Loop (Repetir):**
- Activar/desactivar repetición continua
- Al finalizar, vuelve automáticamente al inicio
- Útil para análisis de ciclo completo

**Smooth (Interpolación):**
- Activar/desactivar interpolación suave
- Con interpolación: movimientos fluidos entre puntos
- Sin interpolación: saltos directos punto a punto

### Control de Velocidad de Simulación

**Slider de velocidad:**
- Rango: 0.1x (muy lento) hasta 5x (muy rápido)
- Velocidad normal: 1x
- Presets: 0.25x, 0.5x, 1x, 2x, 5x

**Aplicaciones:**
- 0.25x - 0.5x: Análisis detallado de movimientos
- 1x: Velocidad real estimada
- 2x - 5x: Vista rápida del ciclo completo

### Información en Tiempo Real

**Panel de información:**
- **Tipo de punto**: Identificación del punto actual
- **Posición**: Coordenadas X, Y, Z en mm
- **Tiempo**: Transcurrido / Total
- **Contador**: Punto actual / Total de puntos

---

## 📐 Especificaciones Técnicas

### Robot UR16e

**Dimensiones (según especificaciones UR):**
```
Base:           Ø95mm × 181mm altura
Brazo superior: 478mm (shoulder to elbow)
Brazo inferior: 478mm (elbow to wrist)
Wrist 1:        117mm offset
Wrist 2:        117mm offset
Wrist 3:        115.5mm (al flange)
```

**Workspace:**
```
Alcance máximo: 900mm
Altura mínima:  -100mm (desde base)
Altura máxima:  1200mm (desde base)
Payload:        16kg
```

**Articulaciones:**
```
6 DOF (grados de libertad)
Rango: ±360° por articulación
Velocidad máx: ~180°/s
```

### Efector Final - Plano Aspirante

**Dimensiones:**
```
Placa:     400mm × 600mm × 20mm grosor
Altura:    50mm desde flange a ventosas
Material:  Aluminio (representación)
```

**Ventosas:**
```
Cantidad:   6 unidades
Disposición: 2 filas × 3 columnas
Diámetro:   50mm cada una
Espaciado:
  - Horizontal (X): 150mm
  - Vertical (Y):   200mm
Tipo:       Ventosa de vacío industrial
```

### Producto/Caja

**Dimensiones configurables:**
```
Por defecto:
  - Ancho:  400mm
  - Largo:  600mm
  - Alto:   150mm
  - Peso:   8kg (típico)
```

---

## 🔧 Uso del Sistema

### Flujo de Trabajo Básico

1. **Seleccionar mosaico** del panel izquierdo
2. **Activar vista 3D** con el botón de vista
3. **Explorar el programa:**
   - Usar controles de cámara (rotar, zoom, pan)
   - Navegar puntos con el timeline
4. **Modificar posiciones:**
   - Modo Position: ajustar TCP
   - Modo Joints: ajustar articulaciones
   - Guardar cambios con botón "Guardar"
5. **Simular ejecución:**
   - Click en "Mostrar Simulación"
   - Ajustar velocidad según necesidad
   - Play para ver animación completa

### Caso de Uso: Teaching Manual

```
1. Seleccionar punto a enseñar
2. Activar modo Freedrive o Position
3. Mover robot a posición deseada
4. Verificar en vista 3D
5. Click en "Guardar"
6. Repetir para siguientes puntos
```

### Caso de Uso: Validación de Programa

```
1. Cargar programa completo
2. Activar simulación con Loop
3. Observar ciclo completo a 1x
4. Si hay dudas, reducir a 0.25x
5. Verificar:
   - Alcances correctos
   - Orientaciones apropiadas
   - Sin colisiones
   - Tiempos razonables
```

---

## ⚙️ Controles de Cámara (Vista 3D)

### Navegación Básica

**Mouse:**
- **Click izquierdo + arrastrar**: Rotar cámara
- **Rueda**: Zoom in/out
- **Click derecho + arrastrar**: Pan (desplazar vista)
- **Doble click**: Reset a vista predefinida

**Teclado (futuro):**
- Flechas: Pan
- +/-: Zoom
- Inicio: Vista home

### Vistas Predefinidas

**4 opciones rápidas:**
- **Frontal**: Vista desde el frente del robot
- **Superior**: Vista aérea (bird's eye)
- **Lateral**: Vista de perfil
- **Isométrica**: Vista 3D diagonal (por defecto)

### Opciones de Visualización

**Toggles disponibles:**
- ☑ **Workspace**: Muestra cilindro del alcance
- ☑ **Grid**: Cuadrícula del suelo
- ☑ **Axes**: Ejes de coordenadas (X, Y, Z)
- ☐ **Trajectory**: Línea de trayectoria completa

---

## 🎯 Diferencias con URSim Original

### Similitudes Implementadas

✅ Modos de control (Position, Joints, Freedrive)
✅ Panel de jog con botones +/-
✅ Control de velocidad
✅ Timeline de programa
✅ Controles de reproducción (Play/Pause/Stop/Step)
✅ Loop y control de velocidad de simulación
✅ Visualización 3D del robot
✅ Información de estado en tiempo real

### Diferencias Principales

**Simplificaciones:**
- 🔶 Cinemática inversa simplificada (vs completa en URSim)
- 🔶 No incluye programación URScript en línea
- 🔶 No simula I/O digitales/analógicas
- 🔶 No incluye safety zones configurables
- 🔶 No simula sensores de fuerza/par

**Ventajas únicas:**
- ✨ Integración directa con archivos .script del proyecto
- ✨ Visualización específica de mosaicos de paletizado
- ✨ Editor de puntos integrado
- ✨ Backup automático de cambios
- ✨ Interfaz web (sin instalación)

---

## 🚀 Próximas Mejoras

### Corto Plazo (FASE 4 - Completar)
- [ ] Corregir cinemática del robot (jerarquía de articulaciones)
- [ ] Implementar cinemática directa completa
- [ ] Interpolación suave entre puntos (splines)
- [ ] Detección básica de colisiones
- [ ] Drag & drop en modo Freedrive

### Medio Plazo (FASE 5)
- [ ] Cinemática inversa completa con múltiples soluciones
- [ ] Gráficas de trayectorias en espacio de articulaciones
- [ ] Simulación de velocidades y aceleraciones
- [ ] Cálculo de tiempos de ciclo reales
- [ ] Safety zones configurables

### Largo Plazo (FASE 6+)
- [ ] Programación URScript visual
- [ ] Simulación de I/O
- [ ] Integración con PolyScope (si disponible)
- [ ] Modo VR/AR para visualización inmersiva
- [ ] Exportar simulaciones como video

---

## 🐛 Problemas Conocidos

### Activos

1. **Modelo 3D del robot**
   - Partes separadas no conectadas correctamente
   - Brazo y herramienta fijos en el suelo
   - No responde a controles de jog
   - **Estado**: En corrección
   - **Prioridad**: Alta

2. **Cinemática**
   - Implementación simplificada
   - No calcula todas las configuraciones posibles
   - **Estado**: Mejora planificada
   - **Prioridad**: Media

### Resoltos

_Ninguno todavía_

---

## 📚 Referencias

### URSim Original
- [Manual de URSim](https://www.universal-robots.com/download/)
- [PolyScope User Manual](https://www.universal-robots.com/download/)
- [CB-Series User Manual](https://www.universal-robots.com/download/)

### Cinemática de Robots
- [Denavit-Hartenberg Parameters](https://en.wikipedia.org/wiki/Denavit%E2%80%93Hartenberg_parameters)
- [Inverse Kinematics for UR Robots](https://www.universal-robots.com/articles/ur/application-installation/dh-parameters-for-calculations-of-kinematics-and-dynamics/)

### Three.js
- [Three.js Documentation](https://threejs.org/docs/)
- [OrbitControls](https://threejs.org/docs/#examples/en/controls/OrbitControls)

---

## 💡 Tips y Trucos

### Para Teaching Preciso
1. Usar velocidad baja (10-25%)
2. Modo Position para ajustes finos
3. Verificar siempre en vista 3D antes de guardar
4. Usar botón Home como referencia

### Para Análisis de Programa
1. Activar Loop para ver ciclo completo
2. Usar 0.5x para análisis detallado
3. Pausar en puntos críticos
4. Verificar orientaciones desde múltiples vistas

### Para Optimización
1. Simular a 1x para tiempos reales
2. Identificar movimientos lentos
3. Verificar alcances extremos
4. Evaluar colisiones potenciales

---

**Versión**: 2.0.0
**Fecha**: 2025-01-27
**Autor**: Sistema de Configuración de Mosaicos L16
**Inspirado en**: URSim by Universal Robots
