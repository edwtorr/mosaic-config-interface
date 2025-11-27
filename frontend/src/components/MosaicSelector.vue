<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  mosaics: {
    type: Array,
    required: true
  },
  selectedId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['select'])

function selectMosaic(id) {
  emit('select', id)
}
</script>

<template>
  <div class="card">
    <h2 class="text-xl font-bold text-gray-800 mb-4">Mosaicos Disponibles</h2>

    <div v-if="mosaics.length === 0" class="text-center py-8 text-gray-500">
      <svg class="w-12 h-12 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
      </svg>
      <p>No hay mosaicos disponibles</p>
    </div>

    <div v-else class="space-y-2">
      <button
        v-for="mosaic in mosaics"
        :key="mosaic.mosaic_id"
        @click="selectMosaic(mosaic.mosaic_id)"
        :class="[
          'w-full text-left p-4 rounded-lg border-2 transition-all',
          selectedId === mosaic.mosaic_id
            ? 'border-blue-600 bg-blue-50'
            : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
        ]"
      >
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <h3 class="font-semibold text-gray-800">{{ mosaic.name }}</h3>
            <div class="mt-2 text-sm text-gray-600 space-y-1">
              <div class="flex items-center">
                <span class="w-20 font-medium">Tipo 1:</span>
                <span>{{ mosaic.type1.n_valid_points }} puntos</span>
              </div>
              <div class="flex items-center">
                <span class="w-20 font-medium">Tipo 2:</span>
                <span>{{ mosaic.type2.n_valid_points }} puntos</span>
              </div>
            </div>
          </div>
          <div v-if="selectedId === mosaic.mosaic_id" class="ml-3">
            <svg class="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>
      </button>
    </div>

    <div class="mt-6 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
      <p class="font-medium">Información:</p>
      <p class="mt-1">Selecciona un mosaico para ver su configuración y editarlo.</p>
    </div>
  </div>
</template>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>
