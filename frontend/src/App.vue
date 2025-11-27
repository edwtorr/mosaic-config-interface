<script setup>
import { ref, onMounted } from 'vue'
import MosaicSelector from './components/MosaicSelector.vue'
import MosaicCanvas from './components/MosaicCanvas.vue'
import MosaicEditor from './components/MosaicEditor.vue'
import { mosaicsAPI, healthAPI } from './services/api'

// Estado de la aplicación
const scriptPath = ref('C:\\Users\\V13_Sp2\\Desktop\\L16 - BACKUP\\20205000045_0\\002_008_L16_REC_AMB_MF.script')
const mosaics = ref([])
const selectedMosaic = ref(null)
const loading = ref(false)
const error = ref(null)
const apiConnected = ref(false)

// Verificar conexión con API al iniciar
onMounted(async () => {
  try {
    await healthAPI.checkHealth()
    apiConnected.value = true
    await loadMosaics()
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
          <!-- Visualización 2D del mosaico -->
          <div class="card">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-2xl font-bold text-gray-800">{{ selectedMosaic.name }}</h2>
              <button
                @click="validateMosaic"
                class="btn-secondary"
              >
                Validar Configuración
              </button>
            </div>
            <MosaicCanvas :mosaic="selectedMosaic" />
          </div>

          <!-- Editor de puntos -->
          <MosaicEditor
            :mosaic="selectedMosaic"
            @update-point="updatePoint"
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
/* Estilos adicionales si son necesarios */
</style>
