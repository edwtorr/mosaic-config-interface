<template>
  <div class="animation-controls card">
    <h3 class="text-lg font-semibold text-gray-800 mb-4">
      <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
      </svg>
      Animación de Trayectoria
    </h3>

    <!-- Controles principales -->
    <div class="controls-row mb-4">
      <div class="button-group">
        <button
          @click="$emit('play')"
          :disabled="isPlaying && !isPaused"
          class="btn-control btn-play"
          title="Play"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
          </svg>
        </button>

        <button
          @click="$emit('pause')"
          :disabled="!isPlaying || isPaused"
          class="btn-control btn-pause"
          title="Pause"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M5.75 3a.75.75 0 00-.75.75v12.5c0 .414.336.75.75.75h1.5a.75.75 0 00.75-.75V3.75A.75.75 0 007.25 3h-1.5zM12.75 3a.75.75 0 00-.75.75v12.5c0 .414.336.75.75.75h1.5a.75.75 0 00.75-.75V3.75a.75.75 0 00-.75-.75h-1.5z" />
          </svg>
        </button>

        <button
          @click="$emit('stop')"
          :disabled="!isPlaying && !isPaused"
          class="btn-control btn-stop"
          title="Stop"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M5.75 3a.75.75 0 00-.75.75v12.5c0 .414.336.75.75.75h8.5a.75.75 0 00.75-.75V3.75a.75.75 0 00-.75-.75h-8.5z" />
          </svg>
        </button>

        <button
          @click="$emit('reset')"
          class="btn-control btn-reset"
          title="Reset"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>

      <div class="status-indicator">
        <span v-if="isPlaying && !isPaused" class="status-badge playing">
          <span class="status-dot"></span>
          Reproduciendo
        </span>
        <span v-else-if="isPaused" class="status-badge paused">
          <span class="status-dot"></span>
          Pausado
        </span>
        <span v-else class="status-badge stopped">
          <span class="status-dot"></span>
          Detenido
        </span>
      </div>
    </div>

    <!-- Barra de progreso -->
    <div class="mb-4">
      <div class="flex justify-between text-sm text-gray-600 mb-1">
        <span>Progreso</span>
        <span>{{ Math.round(progress * 100) }}%</span>
      </div>
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: `${progress * 100}%` }"
        ></div>
      </div>
      <div class="flex justify-between text-xs text-gray-500 mt-1">
        <span>Punto {{ currentSegment + 1 }} de {{ totalPoints }}</span>
        <span v-if="estimatedTime">{{ formatTime(estimatedTime) }}</span>
      </div>
    </div>

    <!-- Control de velocidad -->
    <div class="mb-4">
      <div class="flex justify-between text-sm text-gray-600 mb-2">
        <label>Velocidad</label>
        <span class="font-semibold">{{ speed.toFixed(1) }}x</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-xs text-gray-500">0.5x</span>
        <input
          type="range"
          min="0.5"
          max="3.0"
          step="0.1"
          :value="speed"
          @input="$emit('speed-change', parseFloat($event.target.value))"
          class="speed-slider flex-1"
        />
        <span class="text-xs text-gray-500">3.0x</span>
      </div>
    </div>

    <!-- Opciones adicionales -->
    <div class="options-grid">
      <label class="option-label">
        <input 
          type="checkbox" 
          :checked="loop"
          @change="$emit('toggle-loop')"
        />
        <span>Repetir continuamente</span>
      </label>

      <label class="option-label">
        <input 
          type="checkbox"
          :checked="pauseAtPoints"
          @change="$emit('toggle-pause-at-points')"
        />
        <span>Pausar en cada punto</span>
      </label>
    </div>

    <!-- Información adicional -->
    <div v-if="showInfo" class="info-box mt-4">
      <div class="info-row">
        <span class="info-label">Puntos totales:</span>
        <span class="info-value">{{ totalPoints }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Distancia total:</span>
        <span class="info-value">{{ totalDistance.toFixed(0) }} mm</span>
      </div>
      <div class="info-row">
        <span class="info-label">Tiempo estimado:</span>
        <span class="info-value">{{ formatTime(estimatedTime) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  isPlaying: {
    type: Boolean,
    default: false
  },
  isPaused: {
    type: Boolean,
    default: false
  },
  progress: {
    type: Number,
    default: 0
  },
  currentSegment: {
    type: Number,
    default: 0
  },
  totalPoints: {
    type: Number,
    default: 0
  },
  speed: {
    type: Number,
    default: 1.0
  },
  loop: {
    type: Boolean,
    default: false
  },
  pauseAtPoints: {
    type: Boolean,
    default: false
  },
  estimatedTime: {
    type: Number,
    default: 0
  },
  totalDistance: {
    type: Number,
    default: 0
  },
  showInfo: {
    type: Boolean,
    default: true
  }
})

defineEmits(['play', 'pause', 'stop', 'reset', 'speed-change', 'toggle-loop', 'toggle-pause-at-points'])

/**
 * Formatear tiempo en mm:ss
 */
function formatTime(milliseconds) {
  const seconds = Math.floor(milliseconds / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}
</script>

<style scoped>
.animation-controls {
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.controls-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.button-group {
  display: flex;
  gap: 0.5rem;
}

.btn-control {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-control:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #3b82f6;
  color: #3b82f6;
}

.btn-control:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-play:hover:not(:disabled) {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

.btn-pause:hover:not(:disabled) {
  background: #f59e0b;
  border-color: #f59e0b;
  color: white;
}

.btn-stop:hover:not(:disabled) {
  background: #ef4444;
  border-color: #ef4444;
  color: white;
}

.btn-reset:hover:not(:disabled) {
  background: #6366f1;
  border-color: #6366f1;
  color: white;
}

.status-indicator {
  display: flex;
  align-items: center;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-badge.playing {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.paused {
  background: #fed7aa;
  color: #92400e;
}

.status-badge.stopped {
  background: #e5e7eb;
  color: #374151;
}

.status-dot {
  display: inline-block;
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  background: currentColor;
}

.status-badge.playing .status-dot {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.progress-bar {
  width: 100%;
  height: 0.5rem;
  background: #e5e7eb;
  border-radius: 0.25rem;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #10b981);
  transition: width 0.3s ease;
  border-radius: 0.25rem;
}

.speed-slider {
  -webkit-appearance: none;
  appearance: none;
  height: 0.375rem;
  background: #e5e7eb;
  border-radius: 0.25rem;
  outline: none;
}

.speed-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 1rem;
  height: 1rem;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
}

.speed-slider::-webkit-slider-thumb:hover {
  background: #2563eb;
  transform: scale(1.2);
}

.speed-slider::-moz-range-thumb {
  width: 1rem;
  height: 1rem;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.speed-slider::-moz-range-thumb:hover {
  background: #2563eb;
  transform: scale(1.2);
}

.options-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.option-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #374151;
  cursor: pointer;
}

.option-label input[type="checkbox"] {
  width: 1rem;
  height: 1rem;
  accent-color: #3b82f6;
  cursor: pointer;
}

.info-box {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.375rem;
  padding: 0.75rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 0.25rem 0;
  font-size: 0.875rem;
}

.info-label {
  color: #6b7280;
}

.info-value {
  font-weight: 600;
  color: #111827;
}
</style>
