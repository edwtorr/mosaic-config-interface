/**
 * trajectory-animator.js
 * 
 * Sistema de animación de trayectorias para el robot UR16e
 * Maneja la interpolación entre poses, control de reproducción y generación de líneas
 */

import * as THREE from 'three'
import * as TWEEN from '@tweenjs/tween.js'

/**
 * Clase principal para gestionar animación de trayectorias del robot
 */
export class TrajectoryAnimator {
  constructor(poses, options = {}) {
    this.poses = poses || []
    this.options = {
      speed: options.speed || 1.0,           // Multiplicador de velocidad
      resolution: options.resolution || 50,   // Puntos de interpolación por segmento
      loop: options.loop || false,            // Repetir animación
      pauseAtPoints: options.pauseAtPoints || false, // Pausar en cada punto
      pauseDuration: options.pauseDuration || 500,   // ms de pausa en cada punto
      moveSpeed: options.moveSpeed || 500     // mm/s velocidad del robot
    }

    this.currentSegment = 0
    this.progress = 0
    this.isPlaying = false
    this.isPaused = false
    this.currentTween = null

    // Callbacks
    this.updateCallback = null
    this.completeCallback = null
    this.segmentChangeCallback = null
  }

  /**
   * Iniciar o reanudar la animación
   */
  play() {
    if (this.poses.length < 2) {
      console.warn('Se necesitan al menos 2 poses para animar')
      return
    }

    if (this.isPaused) {
      this.isPaused = false
      this.isPlaying = true
      return
    }

    this.isPlaying = true
    this.isPaused = false
    this.animateSegment(this.currentSegment)
  }

  /**
   * Pausar la animación
   */
  pause() {
    this.isPaused = true
    this.isPlaying = false
    if (this.currentTween) {
      this.currentTween.pause()
    }
  }

  /**
   * Detener la animación y resetear
   */
  stop() {
    this.isPlaying = false
    this.isPaused = false
    this.currentSegment = 0
    this.progress = 0

    if (this.currentTween) {
      this.currentTween.stop()
      this.currentTween = null
    }

    // Volver a la primera pose
    if (this.updateCallback && this.poses[0]) {
      this.updateCallback(this.poses[0], 0, 0)
    }
  }

  /**
   * Resetear a inicio sin detener
   */
  reset() {
    this.stop()
  }

  /**
   * Establecer velocidad de animación
   */
  setSpeed(speed) {
    this.options.speed = Math.max(0.1, Math.min(5.0, speed))
  }

  /**
   * Obtener velocidad actual
   */
  getSpeed() {
    return this.options.speed
  }

  /**
   * Animar un segmento específico (de una pose a la siguiente)
   */
  animateSegment(segmentIndex) {
    if (segmentIndex >= this.poses.length - 1) {
      // Fin de la animación
      if (this.options.loop) {
        this.currentSegment = 0
        this.animateSegment(0)
      } else {
        this.isPlaying = false
        if (this.completeCallback) {
          this.completeCallback()
        }
      }
      return
    }

    const startPose = this.poses[segmentIndex]
    const endPose = this.poses[segmentIndex + 1]

    if (this.segmentChangeCallback) {
      this.segmentChangeCallback(segmentIndex, startPose)
    }

    // Calcular duración basada en distancia y velocidad
    const duration = this.calculateSegmentDuration(startPose, endPose)

    // Crear objeto para interpolar
    const interpolated = { t: 0 }

    this.currentTween = new TWEEN.Tween(interpolated)
      .to({ t: 1 }, duration)
      .easing(TWEEN.Easing.Linear.None)
      .onUpdate(() => {
        const pose = this.interpolateLinear(startPose, endPose, interpolated.t)
        this.progress = (segmentIndex + interpolated.t) / (this.poses.length - 1)

        if (this.updateCallback) {
          this.updateCallback(pose, this.progress, segmentIndex)
        }
      })
      .onComplete(() => {
        this.currentSegment = segmentIndex + 1

        if (this.options.pauseAtPoints && this.currentSegment < this.poses.length - 1) {
          // Pausar en el punto
          setTimeout(() => {
            if (this.isPlaying) {
              this.animateSegment(this.currentSegment)
            }
          }, this.options.pauseDuration)
        } else {
          // Continuar al siguiente segmento
          if (this.isPlaying) {
            this.animateSegment(this.currentSegment)
          }
        }
      })
      .start()
  }

  /**
   * Calcular duración del segmento basada en distancia
   */
  calculateSegmentDuration(startPose, endPose) {
    const distance = Math.sqrt(
      Math.pow(endPose.x - startPose.x, 2) +
      Math.pow(endPose.y - startPose.y, 2) +
      Math.pow(endPose.z - startPose.z, 2)
    )

    // Duración en ms = distancia / velocidad / multiplicador de velocidad
    const duration = (distance / this.options.moveSpeed) * 1000 / this.options.speed

    // Duración mínima y máxima
    return Math.max(500, Math.min(5000, duration))
  }

  /**
   * Interpolación lineal entre dos poses (MoveL)
   */
  interpolateLinear(start, end, t) {
    return {
      x: start.x + (end.x - start.x) * t,
      y: start.y + (end.y - start.y) * t,
      z: start.z + (end.z - start.z) * t,
      rx: start.rx + (end.rx - start.rx) * t,
      ry: start.ry + (end.ry - start.ry) * t,
      rz: start.rz + (end.rz - start.rz) * t
    }
  }

  /**
   * Calcular puntos de la trayectoria completa
   */
  calculateTrajectoryPoints() {
    const points = []

    for (let i = 0; i < this.poses.length - 1; i++) {
      const startPose = this.poses[i]
      const endPose = this.poses[i + 1]

      // Generar puntos interpolados
      for (let j = 0; j <= this.options.resolution; j++) {
        const t = j / this.options.resolution
        const interpolated = this.interpolateLinear(startPose, endPose, t)
        points.push(new THREE.Vector3(interpolated.x, interpolated.y, interpolated.z))
      }
    }

    return points
  }

  /**
   * Estimar duración total de la animación
   */
  estimateTotalDuration() {
    let total = 0

    for (let i = 0; i < this.poses.length - 1; i++) {
      total += this.calculateSegmentDuration(this.poses[i], this.poses[i + 1])
    }

    if (this.options.pauseAtPoints) {
      total += this.options.pauseDuration * (this.poses.length - 2)
    }

    return total / this.options.speed
  }

  /**
   * Registrar callback de actualización
   * @param {Function} callback - (pose, progress, segmentIndex) => void
   */
  onUpdate(callback) {
    this.updateCallback = callback
  }

  /**
   * Registrar callback de completado
   * @param {Function} callback - () => void
   */
  onComplete(callback) {
    this.completeCallback = callback
  }

  /**
   * Registrar callback de cambio de segmento
   * @param {Function} callback - (segmentIndex, pose) => void
   */
  onSegmentChange(callback) {
    this.segmentChangeCallback = callback
  }

  /**
   * Actualizar la animación (debe llamarse en el loop de render)
   */
  update() {
    TWEEN.update()
  }

  /**
   * Obtener estado actual
   */
  getState() {
    return {
      isPlaying: this.isPlaying,
      isPaused: this.isPaused,
      progress: this.progress,
      currentSegment: this.currentSegment,
      totalSegments: this.poses.length - 1,
      speed: this.options.speed
    }
  }
}

/**
 * Crear geometría de línea de trayectoria para Three.js
 */
export function createTrajectoryLine(points, color = 0x3498db, lineWidth = 2) {
  const geometry = new THREE.BufferGeometry().setFromPoints(points)
  const material = new THREE.LineBasicMaterial({
    color: color,
    linewidth: lineWidth,
    opacity: 0.8,
    transparent: true
  })

  return new THREE.Line(geometry, material)
}

/**
 * Crear marcadores para puntos clave de la trayectoria
 */
export function createTrajectoryMarkers(poses, color = 0xe74c3c, size = 10) {
  const markers = []

  poses.forEach((pose, index) => {
    const geometry = new THREE.SphereGeometry(size, 16, 16)
    const material = new THREE.MeshBasicMaterial({
      color: color,
      opacity: 0.7,
      transparent: true
    })

    const marker = new THREE.Mesh(geometry, material)
    // Mapeo de coordenadas: Robot(X, Y, Z) -> Three(X, Z, Y)
    // Robot Z es altura -> Three Y es altura
    // Robot Y es profundidad -> Three Z es profundidad (invertido)
    marker.position.set(pose.x, pose.z, -pose.y)
    marker.userData = { index, pose }

    markers.push(marker)
  })

  return markers
}

/**
 * Formatear tiempo en mm:ss
 */
export function formatTime(milliseconds) {
  const seconds = Math.floor(milliseconds / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60

  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}
