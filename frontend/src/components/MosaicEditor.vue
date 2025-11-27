<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  mosaic: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update-point'])

// Estado del editor
const selectedLayerType = ref('type1')
const selectedPointIndex = ref(null)
const editingPoint = ref(null)

// Capa seleccionada actualmente
const selectedLayer = computed(() => {
  return selectedLayerType.value === 'type1' ? props.mosaic.type1 : props.mosaic.type2
})

// Puntos válidos de la capa seleccionada
const validPoints = computed(() => {
  return selectedLayer.value.points
    .map((point, index) => ({ ...point, index }))
    .filter(point => point.is_valid)
})

// Seleccionar un punto para editar
function selectPoint(index) {
  selectedPointIndex.value = index
  const point = selectedLayer.value.points[index]
  editingPoint.value = {
    x: (point.x * 1000).toFixed(2), // Convertir a mm y formatear
    y: (point.y * 1000).toFixed(2),
    z: (point.z * 1000).toFixed(2),
    rx: point.rx.toFixed(4),
    ry: point.ry.toFixed(4),
    rz: point.rz.toFixed(4)
  }
}

// Guardar cambios del punto
function savePoint() {
  if (!editingPoint.value || selectedPointIndex.value === null) return

  const pointData = {
    layer_type: selectedLayerType.value,
    point_index: selectedPointIndex.value,
    pose: {
      x: parseFloat(editingPoint.value.x) / 1000, // Convertir de mm a m
      y: parseFloat(editingPoint.value.y) / 1000,
      z: parseFloat(editingPoint.value.z) / 1000,
      rx: parseFloat(editingPoint.value.rx),
      ry: parseFloat(editingPoint.value.ry),
      rz: parseFloat(editingPoint.value.rz),
      is_valid: true
    }
  }

  emit('update-point', pointData)
  cancelEdit()
}

// Cancelar edición
function cancelEdit() {
  selectedPointIndex.value = null
  editingPoint.value = null
}

// Aplicar desplazamiento a todos los puntos válidos
const offsetMode = ref(false)
const offsetValues = ref({ x: 0, y: 0, z: 0 })

function toggleOffsetMode() {
  offsetMode.value = !offsetMode.value
  if (!offsetMode.value) {
    offsetValues.value = { x: 0, y: 0, z: 0 }
  }
}

function applyOffset() {
  if (confirm(`¿Aplicar desplazamiento de X:${offsetValues.value.x}mm, Y:${offsetValues.value.y}mm, Z:${offsetValues.value.z}mm a todos los puntos válidos de ${selectedLayerType.value.toUpperCase()}?`)) {
    // Aquí se podría implementar un endpoint para aplicar offset a múltiples puntos
    alert('Función de desplazamiento masivo en desarrollo. Por ahora, edita los puntos individualmente.')
  }
}
</script>

<template>
  <div class="card">
    <h2 class="text-xl font-bold text-gray-800 mb-4">Editor de Puntos</h2>

    <!-- Selector de capa -->
    <div class="mb-6">
      <label class="block text-sm font-medium text-gray-700 mb-2">Seleccionar Capa:</label>
      <div class="flex gap-2">
        <button
          @click="selectedLayerType = 'type1'; cancelEdit()"
          :class="[
            'flex-1 px-4 py-2 rounded-lg font-medium transition-colors',
            selectedLayerType === 'type1'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          ]"
        >
          Tipo 1
        </button>
        <button
          @click="selectedLayerType = 'type2'; cancelEdit()"
          :class="[
            'flex-1 px-4 py-2 rounded-lg font-medium transition-colors',
            selectedLayerType === 'type2'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          ]"
        >
          Tipo 2
        </button>
      </div>
    </div>

    <!-- Lista de puntos -->
    <div v-if="!editingPoint" class="space-y-4">
      <div class="flex justify-between items-center mb-3">
        <h3 class="font-semibold text-gray-700">Puntos Válidos ({{ validPoints.length }})</h3>
        <button
          @click="toggleOffsetMode"
          class="text-sm px-3 py-1 rounded bg-purple-100 text-purple-700 hover:bg-purple-200 transition-colors"
        >
          {{ offsetMode ? 'Modo Normal' : 'Modo Desplazamiento' }}
        </button>
      </div>

      <!-- Modo de desplazamiento masivo -->
      <div v-if="offsetMode" class="p-4 bg-purple-50 border border-purple-200 rounded-lg mb-4">
        <h4 class="font-medium text-purple-900 mb-3">Desplazar todos los puntos</h4>
        <div class="grid grid-cols-3 gap-3 mb-3">
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">X (mm)</label>
            <input
              v-model.number="offsetValues.x"
              type="number"
              step="0.1"
              class="input-field text-sm"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Y (mm)</label>
            <input
              v-model.number="offsetValues.y"
              type="number"
              step="0.1"
              class="input-field text-sm"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-700 mb-1">Z (mm)</label>
            <input
              v-model.number="offsetValues.z"
              type="number"
              step="0.1"
              class="input-field text-sm"
            />
          </div>
        </div>
        <button
          @click="applyOffset"
          class="btn-primary w-full text-sm"
        >
          Aplicar Desplazamiento
        </button>
      </div>

      <!-- Lista de puntos para editar -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
        <button
          v-for="point in validPoints"
          :key="point.index"
          @click="selectPoint(point.index)"
          class="p-3 text-left border-2 border-gray-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-all"
        >
          <div class="font-medium text-gray-800 mb-1">Punto {{ point.index + 1 }}</div>
          <div class="text-xs text-gray-600 space-y-0.5">
            <div>X: {{ (point.x * 1000).toFixed(1) }}mm</div>
            <div>Y: {{ (point.y * 1000).toFixed(1) }}mm</div>
            <div>Z: {{ (point.z * 1000).toFixed(1) }}mm</div>
          </div>
        </button>
      </div>
    </div>

    <!-- Formulario de edición -->
    <div v-else class="space-y-4">
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-semibold text-gray-700">
          Editando Punto {{ selectedPointIndex + 1 }} ({{ selectedLayerType.toUpperCase() }})
        </h3>
        <button
          @click="cancelEdit"
          class="text-sm text-gray-600 hover:text-gray-800"
        >
          ← Volver
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Posición -->
        <div class="space-y-3">
          <h4 class="font-medium text-gray-700 text-sm">Posición (mm)</h4>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">X</label>
            <input
              v-model="editingPoint.x"
              type="number"
              step="0.1"
              class="input-field"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Y</label>
            <input
              v-model="editingPoint.y"
              type="number"
              step="0.1"
              class="input-field"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Z</label>
            <input
              v-model="editingPoint.z"
              type="number"
              step="0.1"
              class="input-field"
            />
          </div>
        </div>

        <!-- Orientación -->
        <div class="space-y-3">
          <h4 class="font-medium text-gray-700 text-sm">Orientación (rad)</h4>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">RX</label>
            <input
              v-model="editingPoint.rx"
              type="number"
              step="0.0001"
              class="input-field"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">RY</label>
            <input
              v-model="editingPoint.ry"
              type="number"
              step="0.0001"
              class="input-field"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">RZ</label>
            <input
              v-model="editingPoint.rz"
              type="number"
              step="0.0001"
              class="input-field"
            />
          </div>
        </div>
      </div>

      <!-- Botones de acción -->
      <div class="flex gap-3 pt-4">
        <button
          @click="savePoint"
          class="btn-primary flex-1"
        >
          Guardar Cambios
        </button>
        <button
          @click="cancelEdit"
          class="btn-secondary flex-1"
        >
          Cancelar
        </button>
      </div>

      <!-- Información -->
      <div class="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
        <p class="text-blue-800">
          <span class="font-medium">Nota:</span> Las coordenadas están en milímetros para facilitar la edición.
          Los cambios se guardarán automáticamente en el archivo .script.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Personalización de scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
