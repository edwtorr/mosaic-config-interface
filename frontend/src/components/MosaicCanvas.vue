<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'

const props = defineProps({
  mosaic: {
    type: Object,
    required: true
  }
})

const canvas = ref(null)
const selectedLayer = ref('type1') // 'type1' o 'type2'

// Constantes de visualización
const CANVAS_WIDTH = 800
const CANVAS_HEIGHT = 600
const SCALE = 800 // escala en mm (800mm = 80cm de área visible)
const POINT_RADIUS = 6
const GRID_SPACING = 100 // espaciado del grid en mm

onMounted(() => {
  drawMosaic()
})

watch(() => [props.mosaic, selectedLayer.value], () => {
  nextTick(() => drawMosaic())
})

function drawMosaic() {
  if (!canvas.value) return

  const ctx = canvas.value.getContext('2d')
  ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

  // Fondo
  ctx.fillStyle = '#f8fafc'
  ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

  // Dibujar grid
  drawGrid(ctx)

  // Dibujar ejes
  drawAxes(ctx)

  // Dibujar alcance máximo del robot (900mm)
  drawRobotReach(ctx)

  // Dibujar puntos del mosaico
  const layer = selectedLayer.value === 'type1' ? props.mosaic.type1 : props.mosaic.type2
  drawPoints(ctx, layer)

  // Dibujar orden de movimiento
  drawOrder(ctx, layer)

  // Dibujar leyenda
  drawLegend(ctx)
}

function drawGrid(ctx) {
  ctx.strokeStyle = '#e2e8f0'
  ctx.lineWidth = 1

  // Líneas verticales
  for (let x = 0; x <= CANVAS_WIDTH; x += GRID_SPACING * (CANVAS_WIDTH / SCALE)) {
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, CANVAS_HEIGHT)
    ctx.stroke()
  }

  // Líneas horizontales
  for (let y = 0; y <= CANVAS_HEIGHT; y += GRID_SPACING * (CANVAS_HEIGHT / SCALE)) {
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(CANVAS_WIDTH, y)
    ctx.stroke()
  }
}

function drawAxes(ctx) {
  const centerX = CANVAS_WIDTH / 2
  const centerY = CANVAS_HEIGHT / 2

  ctx.strokeStyle = '#64748b'
  ctx.lineWidth = 2

  // Eje X
  ctx.beginPath()
  ctx.moveTo(0, centerY)
  ctx.lineTo(CANVAS_WIDTH, centerY)
  ctx.stroke()

  // Eje Y
  ctx.beginPath()
  ctx.moveTo(centerX, 0)
  ctx.lineTo(centerX, CANVAS_HEIGHT)
  ctx.stroke()

  // Etiquetas de ejes
  ctx.fillStyle = '#64748b'
  ctx.font = '12px sans-serif'
  ctx.fillText('X', CANVAS_WIDTH - 20, centerY - 10)
  ctx.fillText('Y', centerX + 10, 20)
  ctx.fillText('(0,0)', centerX + 5, centerY - 5)
}

function drawRobotReach(ctx) {
  const centerX = CANVAS_WIDTH / 2
  const centerY = CANVAS_HEIGHT / 2
  const radius = (900 / SCALE) * CANVAS_WIDTH // 900mm de alcance

  ctx.strokeStyle = '#f59e0b'
  ctx.lineWidth = 2
  ctx.setLineDash([5, 5])
  ctx.beginPath()
  ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
  ctx.stroke()
  ctx.setLineDash([])

  // Etiqueta
  ctx.fillStyle = '#f59e0b'
  ctx.font = 'bold 11px sans-serif'
  ctx.fillText('Alcance máximo (900mm)', centerX - radius + 10, centerY - radius + 20)
}

function drawPoints(ctx, layer) {
  const centerX = CANVAS_WIDTH / 2
  const centerY = CANVAS_HEIGHT / 2

  layer.points.forEach((point, index) => {
    if (!point.is_valid) return

    // Convertir coordenadas del robot (metros) a coordenadas del canvas (pixeles)
    const x = centerX + (point.x * 1000 / SCALE) * CANVAS_WIDTH
    const y = centerY - (point.y * 1000 / SCALE) * CANVAS_HEIGHT // Y invertido en canvas

    // Dibujar punto
    ctx.fillStyle = '#3b82f6'
    ctx.beginPath()
    ctx.arc(x, y, POINT_RADIUS, 0, 2 * Math.PI)
    ctx.fill()

    // Borde del punto
    ctx.strokeStyle = '#1e40af'
    ctx.lineWidth = 2
    ctx.stroke()

    // Número del punto
    ctx.fillStyle = '#fff'
    ctx.font = 'bold 10px sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(index + 1, x, y)
  })
}

function drawOrder(ctx, layer) {
  if (!layer.order || layer.order.length === 0) return

  const centerX = CANVAS_WIDTH / 2
  const centerY = CANVAS_HEIGHT / 2

  ctx.strokeStyle = '#8b5cf6'
  ctx.lineWidth = 2
  ctx.setLineDash([3, 3])

  // Dibujar líneas entre puntos según el orden
  for (let i = 0; i < layer.order.length - 1; i++) {
    const currentIdx = layer.order[i] - 1 // El orden es 1-indexed
    const nextIdx = layer.order[i + 1] - 1

    if (currentIdx < 0 || currentIdx >= layer.points.length) continue
    if (nextIdx < 0 || nextIdx >= layer.points.length) continue

    const p1 = layer.points[currentIdx]
    const p2 = layer.points[nextIdx]

    if (!p1.is_valid || !p2.is_valid) continue

    const x1 = centerX + (p1.x * 1000 / SCALE) * CANVAS_WIDTH
    const y1 = centerY - (p1.y * 1000 / SCALE) * CANVAS_HEIGHT
    const x2 = centerX + (p2.x * 1000 / SCALE) * CANVAS_WIDTH
    const y2 = centerY - (p2.y * 1000 / SCALE) * CANVAS_HEIGHT

    ctx.beginPath()
    ctx.moveTo(x1, y1)
    ctx.lineTo(x2, y2)
    ctx.stroke()
  }

  ctx.setLineDash([])
}

function drawLegend(ctx) {
  const legendX = 10
  const legendY = 10

  // Fondo de la leyenda
  ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
  ctx.fillRect(legendX, legendY, 180, 90)
  ctx.strokeStyle = '#cbd5e1'
  ctx.lineWidth = 1
  ctx.strokeRect(legendX, legendY, 180, 90)

  ctx.fillStyle = '#1e293b'
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'left'

  // Título
  ctx.font = 'bold 12px sans-serif'
  ctx.fillText('Leyenda', legendX + 10, legendY + 20)

  ctx.font = '11px sans-serif'

  // Punto válido
  ctx.fillStyle = '#3b82f6'
  ctx.beginPath()
  ctx.arc(legendX + 15, legendY + 40, 5, 0, 2 * Math.PI)
  ctx.fill()
  ctx.fillStyle = '#1e293b'
  ctx.fillText('Punto válido', legendX + 30, legendY + 43)

  // Orden de movimiento
  ctx.strokeStyle = '#8b5cf6'
  ctx.lineWidth = 2
  ctx.setLineDash([3, 3])
  ctx.beginPath()
  ctx.moveTo(legendX + 10, legendY + 60)
  ctx.lineTo(legendX + 25, legendY + 60)
  ctx.stroke()
  ctx.setLineDash([])
  ctx.fillStyle = '#1e293b'
  ctx.fillText('Orden de visita', legendX + 30, legendY + 63)

  // Alcance máximo
  ctx.strokeStyle = '#f59e0b'
  ctx.lineWidth = 2
  ctx.setLineDash([5, 5])
  ctx.beginPath()
  ctx.moveTo(legendX + 10, legendY + 80)
  ctx.lineTo(legendX + 25, legendY + 80)
  ctx.stroke()
  ctx.setLineDash([])
  ctx.fillStyle = '#1e293b'
  ctx.fillText('Alcance máximo', legendX + 30, legendY + 83)
}
</script>

<template>
  <div>
    <!-- Selector de capa -->
    <div class="mb-4 flex gap-2">
      <button
        @click="selectedLayer = 'type1'"
        :class="[
          'px-4 py-2 rounded-lg font-medium transition-colors',
          selectedLayer === 'type1'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        ]"
      >
        Tipo 1 ({{ mosaic.type1.n_valid_points }} puntos)
      </button>
      <button
        @click="selectedLayer = 'type2'"
        :class="[
          'px-4 py-2 rounded-lg font-medium transition-colors',
          selectedLayer === 'type2'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        ]"
      >
        Tipo 2 ({{ mosaic.type2.n_valid_points }} puntos)
      </button>
    </div>

    <!-- Canvas -->
    <div class="border-2 border-gray-300 rounded-lg overflow-hidden">
      <canvas
        ref="canvas"
        :width="CANVAS_WIDTH"
        :height="CANVAS_HEIGHT"
        class="w-full h-auto"
      />
    </div>

    <!-- Información adicional -->
    <div class="mt-4 grid grid-cols-2 gap-4 text-sm">
      <div class="p-3 bg-gray-100 rounded">
        <p class="font-medium text-gray-700">Vista actual:</p>
        <p class="text-gray-600">{{ selectedLayer === 'type1' ? 'Capa Tipo 1' : 'Capa Tipo 2' }}</p>
      </div>
      <div class="p-3 bg-gray-100 rounded">
        <p class="font-medium text-gray-700">Escala:</p>
        <p class="text-gray-600">{{ SCALE }}mm ({{ SCALE / 10 }}cm)</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
canvas {
  display: block;
}
</style>
