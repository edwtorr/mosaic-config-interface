<script setup>
import { ref, onMounted, computed } from 'vue'
import MosaicSelector from './components/MosaicSelector.vue'
import MosaicCanvas from './components/MosaicCanvas.vue'
import MosaicEditor from './components/MosaicEditor.vue'
import Robot3DViewer from './components/Robot3DViewer.vue'
import RobotControlPanel from './components/RobotControlPanel.vue'
import ProgramPlayer from './components/ProgramPlayer.vue'
import { mosaicsAPI, healthAPI, programsAPI } from './services/api'

// Estado de la aplicación
const scriptPath = ref('C:\\Users\\V13_Sp2\\Desktop\\L16 - BACKUP\\20205000045_0\\002_008_L16_REC_AMB_MF.script')
const mosaics = ref([])
const selectedMosaic = ref(null)
const programs = ref([])
const selectedProgram = ref(null)
const loading = ref(false)
const error = ref(null)
const apiConnected = ref(false)
const viewMode = ref('3d') // '2d' o '3d'
const selectedPoint = ref(null)
const manualControlledPose = ref(null) // Pose controlada manualmente
const showSimulation = ref(false)

// Verificar conexión con API al iniciar
onMounted(async () => {
  try {
    await healthAPI.checkHealth()
    apiConnected.value = true
    await loadMosaics()
    await loadPrograms()
  } catch (err) {
    apiConnected.value = false
    error.value = 'No se pudo conectar con el servidor API. Asegúrate de que el backend esté corriendo en http://localhost:8000'
  }
})

// Cargar lista de mosaicos
async function loadMosaics() {
  loading.value = true
  error.value = null
  try {
    mosaics.value = await mosaicsAPI.getMosaics(scriptPath.value)
  } catch (err) {
    error.value = 'Error al cargar los mosaicos: ' + (err.response?.data?.detail || err.message)
  } finally {
    loading.value = false
  }
}

// Cargar lista de programas
async function loadPrograms() {
  try {
    programs.value = await programsAPI.getPrograms(scriptPath.value)
    if (programs.value && programs.value.length > 0) {
      selectedProgram.value = programs.value[0]
    }
  } catch (err) {
    console.error('Error al cargar programas:', err)
  }
}

// Seleccionar un mosaico
async function selectMosaic(mosaicId) {
  loading.value = true
  error.value = null
  try {
    selectedMosaic.value = await mosaicsAPI.getMosaic(mosaicId, scriptPath.value)
  } catch (err) {
    error.value = 'Error al cargar el mosaico: ' + (err.response?.data?.detail || err.message)
  } finally {
    loading.value = false
  }
}

// Actualizar un punto del mosaico
async function updatePoint(pointData) {
  loading.value = true
  error.value = null
  try {
    await mosaicsAPI.updatePoint(selectedMosaic.value.mosaic_id, pointData, scriptPath.value)
    // Recargar el mosaico actualizado
    await selectMosaic(selectedMosaic.value.mosaic_id)
  } catch (err) {
    error.value = 'Error al actualizar el punto: ' + (err.response?.data?.detail || err.message)
  } finally {
    loading.value = false
  }
}

// Validar configuración del mosaico
async function validateMosaic() {
  if (!selectedMosaic.value) return

  loading.value = true
  error.value = null
  try {
    const result = await mosaicsAPI.validateMosaic(
      selectedMosaic.value.mosaic_id,
      selectedMosaic.value,
      scriptPath.value
    )

    if (result.is_valid) {
      alert('Validación exitosa: El mosaico cumple con todos los límites del robot.')
    } else {
      alert(`Se encontraron ${result.errors.length} errores:\n\n` +
            result.errors.map(e => `- ${e.error}`).join('\n'))
    }
  } catch (err) {
    error.value = 'Error al validar el mosaico: ' + (err.response?.data?.detail || err.message)
  } finally {
    loading.value = false
  }
}

// Cambiar modo de visualización
function toggleViewMode() {
  viewMode.value = viewMode.value === '2d' ? '3d' : '2d'
}

// Seleccionar un punto específico para visualizar en 3D
function selectPointForVisualization(point) {
  selectedPoint.value = point
}

// Computed: Pose actual para visualización 3D
const currentPose = computed(() => {
  // Prioridad: control manual > punto seleccionado > primer punto del mosaico
  if (manualControlledPose.value) {
    return manualControlledPose.value
  }

  if (selectedPoint.value) {
    return selectedPoint.value
  }

  if (selectedMosaic.value && selectedMosaic.value.tipo1 && selectedMosaic.value.tipo1.points) {
    // Retornar el primer punto válido
    const firstPoint = selectedMosaic.value.tipo1.points.find(p => p && p.x !== 0)
    if (firstPoint) return firstPoint
  }

  // Pose por defecto
  return { x: 0, y: -500, z: 400, rx: 0, ry: 0, rz: 0 }
})

// Handler para actualización de pose desde el control panel
function handlePoseUpdate(newPose) {
  manualControlledPose.value = newPose
}

// Handler para guardar posición desde el control panel
function handleSavePosition(pose) {
  // Aquí podrías guardar la posición en el mosaico
  console.log('Guardar posición:', pose)
  // TODO: Implementar guardado en el mosaico actual
}

// Handler para toggle freedrive
function handleToggleFreedrive(enabled) {
  console.log('Freedrive:', enabled)
  // TODO: Implementar lógica de freedrive en el visualizador 3D
}

// Handler para cambio de punto en la simulación
function handleSimulationPointChange(data) {
  selectedPoint.value = data.point
}

// Handler para simulación completada
function handleSimulationComplete() {
  console.log('Simulación completada')
  showSimulation.value = false
}

// Toggle simulación
function toggleSimulation() {
  showSimulation.value = !showSimulation.value
  if (!showSimulation.value) {
    // Resetear a pose manual o primer punto
    manualControlledPose.value = null
  }
}

// Computed: Dimensiones del producto desde el programa seleccionado
const productDimensions = computed(() => {
  if (selectedProgram.value && selectedProgram.value.config) {
    return {
      width: selectedProgram.value.config.product_width || 400,
      length: selectedProgram.value.config.product_length || 600,
      height: selectedProgram.value.config.product_height || 150
    }
  }
  return { width: 400, length: 600, height: 150 }
})

// Computed: Todos los puntos del mosaico para visualizar trayectoria
const allPoses = computed(() => {
  if (!selectedMosaic.value) return []

  const poses = []

  // Agregar puntos Tipo 1
  if (selectedMosaic.value.tipo1 && selectedMosaic.value.tipo1.points) {
    selectedMosaic.value.tipo1.points.forEach(p => {
      if (p && p.x !== 0) poses.push(p)
    })
  }

  // Agregar puntos Tipo 2
  if (selectedMosaic.value.tipo2 && selectedMosaic.value.tipo2.points) {
    selectedMosaic.value.tipo2.points.forEach(p => {
      if (p && p.x !== 0) poses.push(p)
    })
  }

  return poses
})
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-blue-600 text-white shadow-lg">
      <div class="container mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold">Configuración de Mosaicos L16</h1>
        <p class="text-blue-100 mt-1">Sistema de configuración de patrones de paletizado</p>
      </div>
    </header>

    <!-- Contenido principal -->
    <main class="container mx-auto px-4 py-8">
      <!-- Estado de conexión con API -->
      <div v-if="!apiConnected" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
        <div class="flex items-center">
          <svg class="w-6 h-6 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="font-semibold text-red-800">API no conectada</h3>
            <p class="text-red-600 text-sm">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Mensaje de error -->
      <div v-if="error && apiConnected" class="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div class="flex items-center">
          <svg class="w-6 h-6 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="text-yellow-800">{{ error }}</p>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>

      <!-- Contenido principal -->
      <div v-else-if="apiConnected" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Panel izquierdo: Selector de mosaicos -->
        <div class="lg:col-span-1">
          <MosaicSelector
            :mosaics="mosaics"
            :selected-id="selectedMosaic?.mosaic_id"
            @select="selectMosaic"
          />
        </div>

        <!-- Panel central y derecho: Visualización y Editor -->
        <div v-if="selectedMosaic" class="lg:col-span-2 space-y-6">
          <!-- Visualización del mosaico (2D o 3D) -->
          <div class="card">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-2xl font-bold text-gray-800">{{ selectedMosaic.name }}</h2>
              <div class="flex gap-2">
                <!-- Botones de vista -->
                <div class="btn-group">
                  <button
                    @click="viewMode = '2d'"
                    :class="['btn-view-toggle', viewMode === '2d' ? 'active' : '']"
                  >
                    <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                    </svg>
                    Vista 2D
                  </button>
                  <button
                    @click="viewMode = '3d'"
                    :class="['btn-view-toggle', viewMode === '3d' ? 'active' : '']"
                  >
                    <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
                    </svg>
                    Vista 3D
                  </button>
                </div>
                <button
                  @click="validateMosaic"
                  class="btn-secondary"
                >
                  Validar Configuración
                </button>
              </div>
            </div>

            <!-- Vista 2D -->
            <div v-show="viewMode === '2d'">
              <MosaicCanvas :mosaic="selectedMosaic" />
            </div>

            <!-- Vista 3D -->
            <div v-show="viewMode === '3d'">
              <Robot3DViewer
                :pose="currentPose"
                :product-dimensions="productDimensions"
                :all-poses="allPoses"
              />
            </div>
          </div>

          <!-- Controles de Robot y Simulación (solo en vista 3D) -->
          <div v-if="viewMode === '3d'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Panel de Control del Robot -->
            <RobotControlPanel
              :current-pose="currentPose"
              @update-pose="handlePoseUpdate"
              @save-position="handleSavePosition"
              @toggle-freedrive="handleToggleFreedrive"
            />

            <!-- Player de Simulación -->
            <div>
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold text-gray-800">Simulación de Programa</h3>
                <button
                  @click="toggleSimulation"
                  :class="['btn-toggle-simulation', { active: showSimulation }]"
                >
                  {{ showSimulation ? 'Ocultar' : 'Mostrar' }} Simulación
                </button>
              </div>
              <ProgramPlayer
                v-if="showSimulation && allPoses.length > 0"
                :points="allPoses"
                :program-name="selectedMosaic.name"
                @point-changed="handleSimulationPointChange"
                @simulation-complete="handleSimulationComplete"
              />
              <div v-else-if="!showSimulation" class="card text-center py-8 text-gray-500">
                <svg class="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p>Click en "Mostrar Simulación" para ver la animación del programa</p>
              </div>
            </div>
          </div>

          <!-- Editor de puntos -->
          <MosaicEditor
            :mosaic="selectedMosaic"
            @update-point="updatePoint"
            @select-point="selectPointForVisualization"
          />
        </div>

        <!-- Mensaje cuando no hay mosaico seleccionado -->
        <div v-else class="lg:col-span-2 card text-center py-12">
          <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 class="text-xl font-semibold text-gray-700 mb-2">Selecciona un Mosaico</h3>
          <p class="text-gray-500">Elige un mosaico del panel izquierdo para comenzar a editar</p>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-gray-300 mt-12">
      <div class="container mx-auto px-4 py-6 text-center">
        <p class="text-sm">Sistema de Configuración de Mosaicos L16 - Universal Robots UR16e</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.btn-group {
  display: inline-flex;
  border-radius: 0.375rem;
  overflow: hidden;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.btn-view-toggle {
  display: inline-flex;
  align-items: center;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  background-color: white;
  border: 1px solid #e5e7eb;
  color: #374151;
  transition: all 0.2s;
  cursor: pointer;
}

.btn-view-toggle:first-child {
  border-right: none;
}

.btn-view-toggle:hover {
  background-color: #f9fafb;
  color: #111827;
}

.btn-view-toggle.active {
  background-color: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.btn-view-toggle.active:hover {
  background-color: #2563eb;
}

.btn-toggle-simulation {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  background-color: white;
  border: 2px solid #e5e7eb;
  border-radius: 0.375rem;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-toggle-simulation:hover {
  background-color: #f9fafb;
  border-color: #3b82f6;
  color: #3b82f6;
}

.btn-toggle-simulation.active {
  background-color: #3b82f6;
  border-color: #3b82f6;
  color: white;
}
</style>
