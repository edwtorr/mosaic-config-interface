/**
 * Especificaciones técnicas del robot Universal Robots UR16e
 * Basado en documentación oficial de UR
 */

export const UR16E_SPECS = {
  // Dimensiones del robot (en mm)
  dimensions: {
    // Base del robot
    baseRadius: 95,
    baseHeight: 181,

    // Segmentos del brazo (D-H parameters)
    shoulderToElbow: 478,      // a2 - Longitud del brazo superior
    elbowToWrist1: 478,        // a3 - Longitud del brazo inferior
    wrist1ToWrist2: 117,       // d4 - Offset de muñeca 1
    wrist2ToWrist3: 117,       // d5 - Offset de muñeca 2
    wrist3ToFlange: 115.5,     // d6 - Distancia al flange/TCP

    // Diámetros de las articulaciones
    shoulderRadius: 75,
    elbowRadius: 65,
    wristRadius: 50,

    // Offsets adicionales (Denavit-Hartenberg)
    d1: 181,  // Base height
    a2: 478,  // Upper arm
    a3: 478,  // Forearm
    d4: 117,  // Wrist 1
    d5: 117,  // Wrist 2
    d6: 115.5 // Flange
  },

  // Límites del workspace
  workspace: {
    maxReach: 900,           // Alcance máximo en mm
    minHeight: -100,         // Altura mínima desde la base
    maxHeight: 1200,         // Altura máxima desde la base
  },

  // Límites de las articulaciones (en radianes)
  jointLimits: {
    base: { min: -2 * Math.PI, max: 2 * Math.PI },       // ±360°
    shoulder: { min: -2 * Math.PI, max: 2 * Math.PI },   // ±360°
    elbow: { min: -2 * Math.PI, max: 2 * Math.PI },      // ±360°
    wrist1: { min: -2 * Math.PI, max: 2 * Math.PI },     // ±360°
    wrist2: { min: -2 * Math.PI, max: 2 * Math.PI },     // ±360°
    wrist3: { min: -2 * Math.PI, max: 2 * Math.PI }      // ±360°
  },

  // Velocidades máximas (en rad/s)
  maxVelocities: {
    joints: 3.14,  // ~180°/s para todas las articulaciones
    tcp: 1000      // mm/s velocidad TCP
  },

  // Capacidades
  payload: {
    max: 16,      // kg - Payload máximo
    typical: 10   // kg - Payload típico recomendado
  },

  // Colores del robot (tema UR)
  colors: {
    base: 0x2C3E50,           // Gris oscuro
    links: 0x34495E,          // Gris azulado
    joints: 0x95A5A6,         // Gris claro
    flange: 0x7F8C8D,         // Gris metálico
    highlight: 0x3498DB       // Azul UR
  }
}

/**
 * Especificaciones del efector final - Plano aspirante con ventosas
 */
export const END_EFFECTOR_SPECS = {
  // Dimensiones del plano aspirante
  dimensions: {
    width: 400,        // Ancho del plano en mm
    length: 600,       // Largo del plano en mm
    thickness: 20,     // Grosor de la placa
    height: 50         // Altura desde flange a superficie de ventosas
  },

  // Configuración de ventosas
  suction_cups: {
    diameter: 50,      // Diámetro de cada ventosa en mm
    rows: 2,           // Número de filas de ventosas
    cols: 3,           // Número de columnas de ventosas
    spacing: {
      x: 150,          // Separación en X entre ventosas
      y: 200           // Separación en Y entre ventosas
    }
  },

  // Colores
  colors: {
    plate: 0x95A5A6,           // Gris metálico para la placa
    suction_cup: 0x2C3E50,     // Gris oscuro para ventosas
    active: 0x27AE60,          // Verde cuando está activo
    inactive: 0xE74C3C         // Rojo cuando está inactivo
  }
}

/**
 * Especificaciones del producto/caja
 */
export const PRODUCT_SPECS = {
  // Dimensiones por defecto (pueden ser configuradas)
  defaultDimensions: {
    width: 400,       // Ancho en mm
    length: 600,      // Largo en mm
    height: 150       // Alto en mm
  },

  // Peso
  weight: {
    min: 1,           // kg
    max: 15,          // kg (dentro del payload del robot)
    typical: 8        // kg
  },

  // Colores
  colors: {
    box: 0xD35400,           // Naranja/marrón para cajas
    pallet: 0x8E44AD,        // Morado para pallets
    transparent: 0x3498DB    // Azul translúcido para preview
  },

  // Material visual
  opacity: {
    solid: 1.0,
    transparent: 0.3,
    ghost: 0.1
  }
}

/**
 * Función helper para convertir pose URScript a configuración Three.js
 * @param {Object} pose - Pose en formato {x, y, z, rx, ry, rz}
 * @returns {Object} - Configuración para Three.js {position, rotation}
 */
export function urPoseToThreeJS(pose) {
  return {
    position: {
      x: pose.x,
      y: pose.z,   // En Three.js, Y es vertical
      z: -pose.y   // Invertir Y de UR a Z de Three.js
    },
    rotation: {
      x: pose.rx,
      y: pose.rz,
      z: -pose.ry
    }
  }
}

/**
 * Función para calcular la cinemática inversa (simplificada)
 * Esta es una aproximación - para producción se necesitaría implementación completa
 * @param {Object} pose - Pose objetivo {x, y, z, rx, ry, rz}
 * @returns {Object} - Ángulos de las articulaciones {j1, j2, j3, j4, j5, j6}
 */
export function calculateInverseKinematics(pose) {
  // Esta es una implementación simplificada
  // Para producción se necesitaría una implementación completa de IK

  const { x, y, z } = pose

  // Calcular ángulo de la base (rotación alrededor de Z)
  const j1 = Math.atan2(y, x)

  // Distancia horizontal desde la base
  const r = Math.sqrt(x * x + y * y)

  // Altura desde la base
  const h = z - UR16E_SPECS.dimensions.d1

  // Simplificación: posicionar brazo usando geometría 2D
  const l1 = UR16E_SPECS.dimensions.a2
  const l2 = UR16E_SPECS.dimensions.a3

  const d = Math.sqrt(r * r + h * h)

  // Ángulo del codo (ley de cosenos)
  const cosElbow = (d * d - l1 * l1 - l2 * l2) / (2 * l1 * l2)
  const j3 = Math.acos(Math.max(-1, Math.min(1, cosElbow)))

  // Ángulo del hombro
  const alpha = Math.atan2(h, r)
  const beta = Math.acos(Math.max(-1, Math.min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
  const j2 = alpha + beta - Math.PI / 2

  // Muñecas - simplificadas basadas en orientación
  const j4 = pose.rx || 0
  const j5 = pose.ry || 0
  const j6 = pose.rz || 0

  return { j1, j2, j3, j4, j5, j6 }
}

export default {
  UR16E_SPECS,
  END_EFFECTOR_SPECS,
  PRODUCT_SPECS,
  urPoseToThreeJS,
  calculateInverseKinematics
}
