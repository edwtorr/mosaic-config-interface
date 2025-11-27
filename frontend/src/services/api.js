import axios from 'axios'

// Configuración base de la API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para manejar errores globalmente
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

/**
 * Servicio API para mosaicos L16
 */
export const mosaicsAPI = {
  /**
   * Obtener lista de todos los mosaicos
   * @param {string} scriptPath - Ruta al archivo .script
   * @returns {Promise}
   */
  async getMosaics(scriptPath) {
    const response = await apiClient.get('/mosaics', {
      params: { script_path: scriptPath }
    })
    return response.data
  },

  /**
   * Obtener un mosaico específico
   * @param {number} mosaicId - ID del mosaico (1-12)
   * @param {string} scriptPath - Ruta al archivo .script
   * @returns {Promise}
   */
  async getMosaic(mosaicId, scriptPath) {
    const response = await apiClient.get(`/mosaics/${mosaicId}`, {
      params: { script_path: scriptPath }
    })
    return response.data
  },

  /**
   * Actualizar configuración completa de un mosaico
   * @param {number} mosaicId - ID del mosaico
   * @param {object} mosaicData - Datos del mosaico
   * @param {string} scriptPath - Ruta al archivo .script
   * @returns {Promise}
   */
  async updateMosaic(mosaicId, mosaicData, scriptPath) {
    const response = await apiClient.put(`/mosaics/${mosaicId}`, mosaicData, {
      params: { script_path: scriptPath }
    })
    return response.data
  },

  /**
   * Actualizar un punto específico del mosaico
   * @param {number} mosaicId - ID del mosaico
   * @param {object} pointUpdate - Datos del punto a actualizar
   * @param {string} scriptPath - Ruta al archivo .script
   * @returns {Promise}
   */
  async updatePoint(mosaicId, pointUpdate, scriptPath) {
    const response = await apiClient.patch(`/mosaics/${mosaicId}/points`, pointUpdate, {
      params: { script_path: scriptPath }
    })
    return response.data
  },

  /**
   * Validar configuración de un mosaico
   * @param {number} mosaicId - ID del mosaico
   * @param {object} mosaicData - Datos del mosaico
   * @param {string} scriptPath - Ruta al archivo .script
   * @returns {Promise}
   */
  async validateMosaic(mosaicId, mosaicData, scriptPath) {
    const response = await apiClient.post(`/mosaics/${mosaicId}/validate`, mosaicData, {
      params: { script_path: scriptPath }
    })
    return response.data
  },
}

/**
 * Servicio API para programas
 */
export const programsAPI = {
  /**
   * Obtener lista de todos los programas
   * @param {string} scriptPath - Ruta al archivo .script
   * @returns {Promise}
   */
  async getPrograms(scriptPath) {
    const response = await apiClient.get('/programs', {
      params: { script_path: scriptPath }
    })
    return response.data
  },

  /**
   * Obtener un programa específico
   * @param {number} programId - ID del programa (1-10)
   * @param {string} scriptPath - Ruta al archivo .script
   * @returns {Promise}
   */
  async getProgram(programId, scriptPath) {
    const response = await apiClient.get(`/programs/${programId}`, {
      params: { script_path: scriptPath }
    })
    return response.data
  },

  /**
   * Actualizar configuración de un programa
   * @param {number} programId - ID del programa
   * @param {object} programData - Datos del programa
   * @param {string} scriptPath - Ruta al archivo .script
   * @returns {Promise}
   */
  async updateProgram(programId, programData, scriptPath) {
    const response = await apiClient.put(`/programs/${programId}`, programData, {
      params: { script_path: scriptPath }
    })
    return response.data
  },

  /**
   * Obtener puntos de cogida
   * @param {string} scriptPath - Ruta al archivo .script
   * @returns {Promise}
   */
  async getPickPoints(scriptPath) {
    const response = await apiClient.get('/pick-points', {
      params: { script_path: scriptPath }
    })
    return response.data
  },
}

/**
 * Servicio API para health checks
 */
export const healthAPI = {
  /**
   * Verificar estado del servidor
   * @returns {Promise}
   */
  async checkHealth() {
    const response = await apiClient.get('/health')
    return response.data
  },

  /**
   * Obtener información de la API
   * @returns {Promise}
   */
  async getInfo() {
    const response = await apiClient.get('/info')
    return response.data
  },
}

export default {
  mosaics: mosaicsAPI,
  programs: programsAPI,
  health: healthAPI,
}
