<template>
  <div class="program-player">
    <!-- Header -->
    <div class="player-header">
      <h3 class="player-title">Simulación de Programa</h3>
      <div class="program-info">
        <span class="program-name">{{ programName }}</span>
        <span class="point-counter">{{ currentPointIndex + 1 }} / {{ totalPoints }}</span>
      </div>
    </div>

    <!-- Timeline Visualization -->
    <div class="timeline-container">
      <div class="timeline">
        <div
          v-for="(point, index) in points"
          :key="index"
          :class="['timeline-point', {
            'active': index === currentPointIndex,
            'completed': index < currentPointIndex,
            'upcoming': index > currentPointIndex
          }]"
          @click="jumpToPoint(index)"
          :style="{ left: `${(index / (totalPoints - 1)) * 100}%` }"
        >
          <div class="point-marker"></div>
          <div class="point-label">{{ index + 1 }}</div>
        </div>
        <div
          class="progress-line"
          :style="{ width: `${(currentPointIndex / (totalPoints - 1)) * 100}%` }"
        ></div>
      </div>
    </div>

    <!-- Playback Controls -->
    <div class="playback-controls">
      <!-- Main Controls -->
      <div class="main-controls">
        <button
          @click="skipToStart"
          class="control-btn"
          :disabled="isPlaying"
          title="Ir al inicio"
        >
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
          </svg>
        </button>

        <button
          @click="stepBackward"
          class="control-btn"
          :disabled="isPlaying || currentPointIndex === 0"
          title="Paso atrás"
        >
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6 1.41-1.41z"/>
          </svg>
        </button>

        <button
          @click="togglePlayPause"
          :class="['control-btn', 'play-pause-btn', { playing: isPlaying }]"
          title="Play/Pause"
        >
          <svg v-if="!isPlaying" class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z"/>
          </svg>
          <svg v-else class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
            <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
          </svg>
        </button>

        <button
          @click="stepForward"
          class="control-btn"
          :disabled="isPlaying || currentPointIndex === totalPoints - 1"
          title="Paso adelante"
        >
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
          </svg>
        </button>

        <button
          @click="skipToEnd"
          class="control-btn"
          :disabled="isPlaying"
          title="Ir al final"
        >
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
          </svg>
        </button>

        <button
          @click="stop"
          class="control-btn stop-btn"
          :disabled="!isPlaying && currentPointIndex === 0"
          title="Detener"
        >
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M6 6h12v12H6z"/>
          </svg>
        </button>
      </div>

      <!-- Loop and Mode -->
      <div class="playback-options">
        <button
          @click="toggleLoop"
          :class="['option-btn', { active: loopEnabled }]"
          title="Loop"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Loop
        </button>

        <button
          @click="toggleInterpolation"
          :class="['option-btn', { active: interpolationEnabled }]"
          title="Interpolación suave"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          Smooth
        </button>
      </div>
    </div>

    <!-- Speed Control -->
    <div class="speed-control">
      <label class="speed-label">
        Velocidad de Simulación: {{ simulationSpeed }}x
      </label>
      <input
        type="range"
        v-model.number="simulationSpeed"
        min="0.1"
        max="5"
        step="0.1"
        class="speed-slider"
      />
      <div class="speed-presets">
        <button @click="simulationSpeed = 0.25" class="speed-preset-btn">0.25x</button>
        <button @click="simulationSpeed = 0.5" class="speed-preset-btn">0.5x</button>
        <button @click="simulationSpeed = 1" class="speed-preset-btn">1x</button>
        <button @click="simulationSpeed = 2" class="speed-preset-btn">2x</button>
        <button @click="simulationSpeed = 5" class="speed-preset-btn">5x</button>
      </div>
    </div>

    <!-- Current Point Info -->
    <div class="current-point-info" v-if="currentPoint">
      <div class="info-row">
        <span class="info-label">Tipo:</span>
        <span class="info-value">{{ currentPoint.type || 'Punto de mosaico' }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Posición:</span>
        <span class="info-value">
          X: {{ currentPoint.x?.toFixed(1) }}
          Y: {{ currentPoint.y?.toFixed(1) }}
          Z: {{ currentPoint.z?.toFixed(1) }}
        </span>
      </div>
      <div class="info-row">
        <span class="info-label">Tiempo:</span>
        <span class="info-value">{{ elapsedTime.toFixed(1) }}s / {{ totalTime.toFixed(1) }}s</span>
      </div>
    </div>

    <!-- Progress Bar -->
    <div class="progress-bar-container">
      <div class="progress-bar" :style="{ width: `${progress}%` }"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'

const props = defineProps({
  points: {
    type: Array,
    default: () => []
  },
  programName: {
    type: String,
    default: 'Programa de Mosaico'
  }
})

const emit = defineEmits(['point-changed', 'simulation-complete'])

// Estado de reproducción
const isPlaying = ref(false)
const currentPointIndex = ref(0)
const loopEnabled = ref(false)
const interpolationEnabled = ref(true)
const simulationSpeed = ref(1)

// Tiempos
const elapsedTime = ref(0)
const baseTimePerPoint = 2 // segundos base por punto

// Animation frame
let animationFrameId = null
let lastFrameTime = 0

// Computed
const totalPoints = computed(() => props.points.length)
const currentPoint = computed(() => props.points[currentPointIndex.value])

const totalTime = computed(() => {
  return totalPoints.value * baseTimePerPoint / simulationSpeed.value
})

const progress = computed(() => {
  if (totalPoints.value === 0) return 0
  return (currentPointIndex.value / (totalPoints.value - 1)) * 100
})

// Funciones de control
function togglePlayPause() {
  if (isPlaying.value) {
    pause()
  } else {
    play()
  }
}

function play() {
  if (currentPointIndex.value >= totalPoints.value - 1) {
    currentPointIndex.value = 0
  }
  isPlaying.value = true
  lastFrameTime = performance.now()
  animate()
}

function pause() {
  isPlaying.value = false
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
}

function stop() {
  pause()
  currentPointIndex.value = 0
  elapsedTime.value = 0
  emitPointChanged()
}

function stepForward() {
  if (currentPointIndex.value < totalPoints.value - 1) {
    currentPointIndex.value++
    emitPointChanged()
  }
}

function stepBackward() {
  if (currentPointIndex.value > 0) {
    currentPointIndex.value--
    emitPointChanged()
  }
}

function skipToStart() {
  currentPointIndex.value = 0
  elapsedTime.value = 0
  emitPointChanged()
}

function skipToEnd() {
  currentPointIndex.value = totalPoints.value - 1
  elapsedTime.value = totalTime.value
  emitPointChanged()
}

function jumpToPoint(index) {
  if (!isPlaying.value) {
    currentPointIndex.value = index
    emitPointChanged()
  }
}

function toggleLoop() {
  loopEnabled.value = !loopEnabled.value
}

function toggleInterpolation() {
  interpolationEnabled.value = !interpolationEnabled.value
}

// Animación
function animate(currentTime = 0) {
  if (!isPlaying.value) return

  const deltaTime = (currentTime - lastFrameTime) / 1000 // convertir a segundos
  lastFrameTime = currentTime

  // Actualizar tiempo transcurrido
  elapsedTime.value += deltaTime * simulationSpeed.value

  // Calcular punto actual basado en tiempo
  const timePerPoint = baseTimePerPoint / simulationSpeed.value
  const newPointIndex = Math.floor(elapsedTime.value / timePerPoint)

  if (newPointIndex !== currentPointIndex.value) {
    if (newPointIndex >= totalPoints.value) {
      // Fin del programa
      if (loopEnabled.value) {
        currentPointIndex.value = 0
        elapsedTime.value = 0
      } else {
        currentPointIndex.value = totalPoints.value - 1
        pause()
        emit('simulation-complete')
        return
      }
    } else {
      currentPointIndex.value = newPointIndex
    }
    emitPointChanged()
  }

  animationFrameId = requestAnimationFrame(animate)
}

// Emitir cambio de punto
function emitPointChanged() {
  if (currentPoint.value) {
    emit('point-changed', {
      point: currentPoint.value,
      index: currentPointIndex.value,
      interpolate: interpolationEnabled.value
    })
  }
}

// Watch para cambios en el índice del punto
watch(currentPointIndex, () => {
  emitPointChanged()
})

// Cleanup
onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
})
</script>

<style scoped>
.program-player {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.player-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e5e7eb;
}

.player-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.program-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.program-name {
  font-size: 0.875rem;
  color: #6b7280;
}

.point-counter {
  font-size: 0.875rem;
  font-weight: 600;
  color: #3b82f6;
}

/* Timeline */
.timeline-container {
  margin-bottom: 20px;
  padding: 0 10px;
}

.timeline {
  position: relative;
  height: 60px;
  background: #f3f4f6;
  border-radius: 8px;
  padding: 25px 0;
}

.timeline-point {
  position: absolute;
  transform: translateX(-50%);
  cursor: pointer;
  z-index: 2;
}

.point-marker {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: white;
  border: 3px solid #d1d5db;
  transition: all 0.3s;
}

.timeline-point.completed .point-marker {
  background: #10b981;
  border-color: #10b981;
}

.timeline-point.active .point-marker {
  background: #3b82f6;
  border-color: #3b82f6;
  width: 20px;
  height: 20px;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
}

.timeline-point.upcoming .point-marker {
  background: white;
  border-color: #d1d5db;
}

.point-label {
  position: absolute;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.75rem;
  color: #6b7280;
  white-space: nowrap;
}

.progress-line {
  position: absolute;
  top: 50%;
  left: 0;
  height: 4px;
  background: #3b82f6;
  transform: translateY(-50%);
  transition: width 0.3s;
  z-index: 1;
  border-radius: 4px;
}

/* Playback Controls */
.playback-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
}

.main-controls {
  display: flex;
  gap: 8px;
  flex: 1;
  justify-content: center;
}

.control-btn {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: #4b5563;
}

.control-btn:hover:not(:disabled) {
  background: #f3f4f6;
  border-color: #3b82f6;
  color: #3b82f6;
}

.control-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.play-pause-btn {
  width: 64px;
  height: 64px;
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.play-pause-btn:hover:not(:disabled) {
  background: #2563eb;
  border-color: #2563eb;
  transform: scale(1.05);
}

.play-pause-btn.playing {
  background: #f59e0b;
  border-color: #f59e0b;
}

.play-pause-btn.playing:hover {
  background: #d97706;
  border-color: #d97706;
}

.stop-btn {
  background: #ef4444;
  border-color: #ef4444;
  color: white;
}

.stop-btn:hover:not(:disabled) {
  background: #dc2626;
  border-color: #dc2626;
}

.playback-options {
  display: flex;
  gap: 8px;
}

.option-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s;
}

.option-btn:hover {
  background: #f3f4f6;
  border-color: #3b82f6;
}

.option-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

/* Speed Control */
.speed-control {
  padding: 15px;
  background: #f9fafb;
  border-radius: 6px;
  margin-bottom: 15px;
}

.speed-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 10px;
}

.speed-slider {
  width: 100%;
  height: 6px;
  margin-bottom: 10px;
}

.speed-presets {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
}

.speed-preset-btn {
  padding: 6px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.speed-preset-btn:hover {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

/* Current Point Info */
.current-point-info {
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
  margin-bottom: 15px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.875rem;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-weight: 500;
  color: #6b7280;
}

.info-value {
  font-weight: 500;
  color: #1f2937;
}

/* Progress Bar */
.progress-bar-container {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #10b981);
  transition: width 0.3s;
  border-radius: 4px;
}
</style>
