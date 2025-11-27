<template>
  <div class="robot-control-panel">
    <!-- Header -->
    <div class="panel-header">
      <h3 class="panel-title">Control del Robot</h3>
      <div class="robot-status">
        <span :class="['status-indicator', robotState]"></span>
        <span class="status-text">{{ robotStateText }}</span>
      </div>
    </div>

    <!-- Mode Selector -->
    <div class="mode-selector">
      <button
        @click="controlMode = 'position'"
        :class="['mode-btn', { active: controlMode === 'position' }]"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        Position
      </button>
      <button
        @click="controlMode = 'joints'"
        :class="['mode-btn', { active: controlMode === 'joints' }]"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
        </svg>
        Joints
      </button>
      <button
        @click="controlMode = 'freedrive'"
        :class="['mode-btn', { active: controlMode === 'freedrive' }]"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11.5V14m0-2.5v-6a1.5 1.5 0 113 0m-3 6a1.5 1.5 0 00-3 0v2a7.5 7.5 0 0015 0v-5a1.5 1.5 0 00-3 0m-6-3V11m0-5.5v-1a1.5 1.5 0 013 0v1m0 0V11m0-5.5a1.5 1.5 0 013 0v3m0 0V11" />
        </svg>
        Freedrive
      </button>
    </div>

    <!-- Position Control (Cartesian) -->
    <div v-if="controlMode === 'position'" class="control-section">
      <h4 class="section-title">Movimiento Cartesiano (TCP)</h4>

      <!-- XYZ Controls -->
      <div class="axis-controls">
        <div class="axis-group">
          <label class="axis-label">X (mm)</label>
          <div class="axis-buttons">
            <button @click="jogTCP('x', -1)" class="jog-btn jog-minus">-</button>
            <input
              type="number"
              v-model.number="tcpPosition.x"
              @change="updateTCPPosition"
              class="axis-input"
            />
            <button @click="jogTCP('x', 1)" class="jog-btn jog-plus">+</button>
          </div>
        </div>

        <div class="axis-group">
          <label class="axis-label">Y (mm)</label>
          <div class="axis-buttons">
            <button @click="jogTCP('y', -1)" class="jog-btn jog-minus">-</button>
            <input
              type="number"
              v-model.number="tcpPosition.y"
              @change="updateTCPPosition"
              class="axis-input"
            />
            <button @click="jogTCP('y', 1)" class="jog-btn jog-plus">+</button>
          </div>
        </div>

        <div class="axis-group">
          <label class="axis-label">Z (mm)</label>
          <div class="axis-buttons">
            <button @click="jogTCP('z', -1)" class="jog-btn jog-minus">-</button>
            <input
              type="number"
              v-model.number="tcpPosition.z"
              @change="updateTCPPosition"
              class="axis-input"
            />
            <button @click="jogTCP('z', 1)" class="jog-btn jog-plus">+</button>
          </div>
        </div>

        <!-- Rotation Controls -->
        <div class="axis-group">
          <label class="axis-label">RX (°)</label>
          <div class="axis-buttons">
            <button @click="jogTCP('rx', -1)" class="jog-btn jog-minus">-</button>
            <input
              type="number"
              v-model.number="tcpRotation.rx"
              @change="updateTCPPosition"
              class="axis-input"
              step="5"
            />
            <button @click="jogTCP('rx', 1)" class="jog-btn jog-plus">+</button>
          </div>
        </div>

        <div class="axis-group">
          <label class="axis-label">RY (°)</label>
          <div class="axis-buttons">
            <button @click="jogTCP('ry', -1)" class="jog-btn jog-minus">-</button>
            <input
              type="number"
              v-model.number="tcpRotation.ry"
              @change="updateTCPPosition"
              class="axis-input"
              step="5"
            />
            <button @click="jogTCP('ry', 1)" class="jog-btn jog-plus">+</button>
          </div>
        </div>

        <div class="axis-group">
          <label class="axis-label">RZ (°)</label>
          <div class="axis-buttons">
            <button @click="jogTCP('rz', -1)" class="jog-btn jog-minus">-</button>
            <input
              type="number"
              v-model.number="tcpRotation.rz"
              @change="updateTCPPosition"
              class="axis-input"
              step="5"
            />
            <button @click="jogTCP('rz', 1)" class="jog-btn jog-plus">+</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Joint Control -->
    <div v-if="controlMode === 'joints'" class="control-section">
      <h4 class="section-title">Control de Articulaciones</h4>

      <div class="axis-controls">
        <div v-for="(joint, index) in joints" :key="index" class="axis-group">
          <label class="axis-label">{{ joint.name }}</label>
          <div class="axis-buttons">
            <button @click="jogJoint(index, -1)" class="jog-btn jog-minus">-</button>
            <input
              type="number"
              v-model.number="joint.angle"
              @change="updateJointAngles"
              class="axis-input"
              step="5"
            />
            <button @click="jogJoint(index, 1)" class="jog-btn jog-plus">+</button>
          </div>
          <div class="joint-range">{{ joint.min }}° / {{ joint.max }}°</div>
        </div>
      </div>
    </div>

    <!-- Freedrive Mode -->
    <div v-if="controlMode === 'freedrive'" class="control-section freedrive-section">
      <h4 class="section-title">Modo Freedrive</h4>
      <p class="freedrive-info">
        <svg class="w-5 h-5 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        En modo Freedrive, puedes mover el robot manualmente arrastrando el TCP en la vista 3D.
      </p>
      <button
        @click="toggleFreedrive"
        :class="['freedrive-btn', { active: freedriveActive }]"
      >
        {{ freedriveActive ? 'Desactivar Freedrive' : 'Activar Freedrive' }}
      </button>
    </div>

    <!-- Velocity Control -->
    <div class="velocity-control">
      <label class="velocity-label">
        Velocidad: {{ velocity }}%
        <span class="velocity-value">{{ Math.round(velocity * 10) }}mm/s</span>
      </label>
      <input
        type="range"
        v-model.number="velocity"
        min="1"
        max="100"
        class="velocity-slider"
      />
      <div class="velocity-presets">
        <button @click="velocity = 10" class="preset-btn">10%</button>
        <button @click="velocity = 25" class="preset-btn">25%</button>
        <button @click="velocity = 50" class="preset-btn">50%</button>
        <button @click="velocity = 100" class="preset-btn">100%</button>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <button @click="moveToHome" class="action-btn primary">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        Home
      </button>
      <button @click="saveCurrentPosition" class="action-btn">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        Guardar
      </button>
      <button @click="resetToOriginal" class="action-btn">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Reset
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  currentPose: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update-pose', 'save-position'])

// Estado del robot
const robotState = ref('idle') // idle, moving, error
const robotStateText = computed(() => {
  const states = {
    idle: 'Detenido',
    moving: 'En movimiento',
    error: 'Error'
  }
  return states[robotState.value] || 'Desconocido'
})

// Modo de control
const controlMode = ref('position') // position, joints, freedrive
const freedriveActive = ref(false)

// Posición TCP
const tcpPosition = ref({
  x: props.currentPose.x || 0,
  y: props.currentPose.y || -500,
  z: props.currentPose.z || 400
})

const tcpRotation = ref({
  rx: (props.currentPose.rx || 0) * 180 / Math.PI,
  ry: (props.currentPose.ry || 0) * 180 / Math.PI,
  rz: (props.currentPose.rz || 0) * 180 / Math.PI
})

// Articulaciones
const joints = ref([
  { name: 'Base (J1)', angle: 0, min: -360, max: 360 },
  { name: 'Shoulder (J2)', angle: 0, min: -360, max: 360 },
  { name: 'Elbow (J3)', angle: 0, min: -360, max: 360 },
  { name: 'Wrist 1 (J4)', angle: 0, min: -360, max: 360 },
  { name: 'Wrist 2 (J5)', angle: 0, min: -360, max: 360 },
  { name: 'Wrist 3 (J6)', angle: 0, min: -360, max: 360 }
])

// Velocidad
const velocity = ref(50)

// Step size basado en velocidad
const getStepSize = () => {
  return velocity.value / 10
}

// Jog TCP
function jogTCP(axis, direction) {
  const step = getStepSize()

  if (['x', 'y', 'z'].includes(axis)) {
    tcpPosition.value[axis] += direction * step
  } else {
    const rotAxis = axis.substring(1) // 'rx' -> 'x'
    tcpRotation.value[axis] += direction * (step / 2) // Rotación más lenta
  }

  updateTCPPosition()
}

// Jog Joint
function jogJoint(jointIndex, direction) {
  const step = getStepSize()
  joints.value[jointIndex].angle += direction * step

  // Limitar a rango
  const joint = joints.value[jointIndex]
  joint.angle = Math.max(joint.min, Math.min(joint.max, joint.angle))

  updateJointAngles()
}

// Actualizar posición TCP
function updateTCPPosition() {
  robotState.value = 'moving'

  const newPose = {
    x: tcpPosition.value.x,
    y: tcpPosition.value.y,
    z: tcpPosition.value.z,
    rx: tcpRotation.value.rx * Math.PI / 180,
    ry: tcpRotation.value.ry * Math.PI / 180,
    rz: tcpRotation.value.rz * Math.PI / 180
  }

  emit('update-pose', newPose)

  setTimeout(() => {
    robotState.value = 'idle'
  }, 500)
}

// Actualizar ángulos de articulaciones
function updateJointAngles() {
  robotState.value = 'moving'

  // Por ahora emitimos los ángulos, más adelante calcularemos cinemática directa
  emit('update-joints', joints.value.map(j => j.angle * Math.PI / 180))

  setTimeout(() => {
    robotState.value = 'idle'
  }, 500)
}

// Toggle Freedrive
function toggleFreedrive() {
  freedriveActive.value = !freedriveActive.value
  // Emitir evento para activar/desactivar controles de freedrive en el viewer 3D
  emit('toggle-freedrive', freedriveActive.value)
}

// Ir a home
function moveToHome() {
  tcpPosition.value = { x: 0, y: -500, z: 400 }
  tcpRotation.value = { rx: 0, ry: 0, rz: 0 }
  joints.value.forEach(joint => joint.angle = 0)
  updateTCPPosition()
}

// Guardar posición actual
function saveCurrentPosition() {
  const pose = {
    x: tcpPosition.value.x,
    y: tcpPosition.value.y,
    z: tcpPosition.value.z,
    rx: tcpRotation.value.rx * Math.PI / 180,
    ry: tcpRotation.value.ry * Math.PI / 180,
    rz: tcpRotation.value.rz * Math.PI / 180
  }
  emit('save-position', pose)
}

// Reset a posición original
function resetToOriginal() {
  tcpPosition.value = {
    x: props.currentPose.x || 0,
    y: props.currentPose.y || -500,
    z: props.currentPose.z || 400
  }
  tcpRotation.value = {
    rx: (props.currentPose.rx || 0) * 180 / Math.PI,
    ry: (props.currentPose.ry || 0) * 180 / Math.PI,
    rz: (props.currentPose.rz || 0) * 180 / Math.PI
  }
  updateTCPPosition()
}

// Watch para actualizar cuando cambia la pose externa
watch(() => props.currentPose, (newPose) => {
  tcpPosition.value = {
    x: newPose.x || 0,
    y: newPose.y || -500,
    z: newPose.z || 400
  }
  tcpRotation.value = {
    rx: (newPose.rx || 0) * 180 / Math.PI,
    ry: (newPose.ry || 0) * 180 / Math.PI,
    rz: (newPose.rz || 0) * 180 / Math.PI
  }
}, { deep: true })
</script>

<style scoped>
.robot-control-panel {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e5e7eb;
}

.panel-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.robot-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-indicator.idle {
  background: #10b981;
}

.status-indicator.moving {
  background: #f59e0b;
}

.status-indicator.error {
  background: #ef4444;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

/* Mode Selector */
.mode-selector {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 20px;
}

.mode-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: #f3f4f6;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-btn:hover {
  background: #e5e7eb;
  border-color: #d1d5db;
}

.mode-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

/* Control Section */
.control-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 15px;
}

/* Axis Controls */
.axis-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.axis-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.axis-label {
  min-width: 70px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4b5563;
}

.axis-buttons {
  display: flex;
  gap: 8px;
  flex: 1;
}

.jog-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  background: white;
  font-size: 1.25rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.jog-btn:hover {
  background: #f3f4f6;
  border-color: #3b82f6;
  color: #3b82f6;
}

.jog-btn:active {
  background: #3b82f6;
  color: white;
  transform: scale(0.95);
}

.jog-minus {
  color: #ef4444;
}

.jog-plus {
  color: #10b981;
}

.axis-input {
  flex: 1;
  padding: 8px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  text-align: center;
  font-weight: 500;
}

.axis-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.joint-range {
  font-size: 0.75rem;
  color: #9ca3af;
  min-width: 80px;
  text-align: right;
}

/* Freedrive Section */
.freedrive-section {
  text-align: center;
}

.freedrive-info {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.freedrive-btn {
  padding: 12px 24px;
  background: #f3f4f6;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.freedrive-btn:hover {
  background: #e5e7eb;
}

.freedrive-btn.active {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

/* Velocity Control */
.velocity-control {
  padding: 15px;
  background: #f9fafb;
  border-radius: 6px;
  margin-bottom: 20px;
}

.velocity-label {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 10px;
}

.velocity-value {
  color: #3b82f6;
}

.velocity-slider {
  width: 100%;
  height: 6px;
  margin-bottom: 10px;
}

.velocity-presets {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
}

.preset-btn {
  padding: 6px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-btn:hover {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

/* Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f3f4f6;
  border-color: #3b82f6;
  color: #3b82f6;
}

.action-btn.primary {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.action-btn.primary:hover {
  background: #2563eb;
  border-color: #2563eb;
}
</style>
