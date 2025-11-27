<template>
  <div class="robot-3d-viewer">
    <!-- Canvas para Three.js -->
    <div ref="canvasContainer" class="canvas-container"></div>

    <!-- Controles de visualización -->
    <div class="controls-panel">
      <div class="control-group">
        <label class="control-label">Vista:</label>
        <div class="button-group">
          <button @click="setCameraView('front')" class="btn-view">Frontal</button>
          <button @click="setCameraView('top')" class="btn-view">Superior</button>
          <button @click="setCameraView('side')" class="btn-view">Lateral</button>
          <button @click="setCameraView('iso')" class="btn-view active">Isométrica</button>
        </div>
      </div>

      <div class="control-group">
        <label class="control-label">
          <input type="checkbox" v-model="showWorkspace" @change="toggleWorkspace" />
          Mostrar workspace
        </label>
      </div>

      <div class="control-group">
        <label class="control-label">
          <input type="checkbox" v-model="showGrid" @change="toggleGrid" />
          Mostrar grid
        </label>
      </div>

      <div class="control-group">
        <label class="control-label">
          <input type="checkbox" v-model="showAxes" @change="toggleAxes" />
          Mostrar ejes
        </label>
      </div>

      <div class="control-group">
        <label class="control-label">
          <input type="checkbox" v-model="showTrajectory" @change="toggleTrajectory" />
          Mostrar trayectoria
        </label>
      </div>
    </div>

    <!-- Información de la posición actual -->
    <div class="info-panel" v-if="currentPose">
      <h4>Posición Actual</h4>
      <div class="info-grid">
        <div><strong>X:</strong> {{ currentPose.x.toFixed(1) }} mm</div>
        <div><strong>Y:</strong> {{ currentPose.y.toFixed(1) }} mm</div>
        <div><strong>Z:</strong> {{ currentPose.z.toFixed(1) }} mm</div>
        <div><strong>RX:</strong> {{ (currentPose.rx * 180 / Math.PI).toFixed(1) }}°</div>
        <div><strong>RY:</strong> {{ (currentPose.ry * 180 / Math.PI).toFixed(1) }}°</div>
        <div><strong>RZ:</strong> {{ (currentPose.rz * 180 / Math.PI).toFixed(1) }}°</div>
      </div>
      <div class="info-status" v-if="isWithinLimits !== null">
        <span :class="['status-badge', isWithinLimits ? 'valid' : 'invalid']">
          {{ isWithinLimits ? '✓ Dentro de límites' : '⚠ Fuera de límites' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { UR16E_SPECS, END_EFFECTOR_SPECS, PRODUCT_SPECS, calculateInverseKinematics } from '../utils/ur16e-specs'

const props = defineProps({
  pose: {
    type: Object,
    default: () => ({ x: 0, y: -500, z: 400, rx: 0, ry: 0, rz: 0 })
  },
  productDimensions: {
    type: Object,
    default: () => ({ width: 400, length: 600, height: 150 })
  },
  allPoses: {
    type: Array,
    default: () => []
  }
})

// Referencias
const canvasContainer = ref(null)

// Estado
const showWorkspace = ref(true)
const showGrid = ref(true)
const showAxes = ref(true)
const showTrajectory = ref(false)
const currentPose = ref(null)
const isWithinLimits = ref(null)

// Three.js objects
let scene, camera, renderer, controls
let robot = null
let endEffector = null
let product = null
let workspace = null
let gridHelper = null
let axesHelper = null
let trajectoryLine = null

/**
 * Inicializar escena Three.js
 */
function initScene() {
  // Crear escena
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0xf0f0f0)

  // Crear cámara
  camera = new THREE.PerspectiveCamera(
    50,
    canvasContainer.value.clientWidth / canvasContainer.value.clientHeight,
    10,
    10000
  )
  camera.position.set(1500, 1500, 1500)
  camera.lookAt(0, 0, 0)

  // Crear renderer
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight)
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  canvasContainer.value.appendChild(renderer.domElement)

  // Controles de cámara
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.target.set(0, 300, 0)
  controls.update()

  // Iluminación
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
  directionalLight.position.set(1000, 2000, 1000)
  directionalLight.castShadow = true
  directionalLight.shadow.camera.left = -1500
  directionalLight.shadow.camera.right = 1500
  directionalLight.shadow.camera.top = 1500
  directionalLight.shadow.camera.bottom = -1500
  directionalLight.shadow.mapSize.width = 2048
  directionalLight.shadow.mapSize.height = 2048
  scene.add(directionalLight)

  // Luz de relleno
  const fillLight = new THREE.DirectionalLight(0xffffff, 0.3)
  fillLight.position.set(-1000, 1000, -1000)
  scene.add(fillLight)

  // Grid
  gridHelper = new THREE.GridHelper(2000, 20, 0x888888, 0xcccccc)
  scene.add(gridHelper)

  // Ejes
  axesHelper = new THREE.AxesHelper(500)
  scene.add(axesHelper)

  // Suelo
  const floorGeometry = new THREE.PlaneGeometry(3000, 3000)
  const floorMaterial = new THREE.MeshStandardMaterial({
    color: 0xe0e0e0,
    roughness: 0.8,
    metalness: 0.2
  })
  const floor = new THREE.Mesh(floorGeometry, floorMaterial)
  floor.rotation.x = -Math.PI / 2
  floor.receiveShadow = true
  scene.add(floor)
}

/**
 * Crear modelo del robot UR16e
 */
function createRobot() {
  robot = new THREE.Group()
  const specs = UR16E_SPECS.dimensions

  // Base del robot
  const baseGeometry = new THREE.CylinderGeometry(specs.baseRadius, specs.baseRadius, specs.baseHeight, 32)
  const baseMaterial = new THREE.MeshStandardMaterial({
    color: UR16E_SPECS.colors.base,
    roughness: 0.5,
    metalness: 0.5
  })
  const base = new THREE.Mesh(baseGeometry, baseMaterial)
  base.position.y = specs.baseHeight / 2
  base.castShadow = true
  robot.add(base)

  // Joint 1 (Base rotation) - Hombro
  const shoulder = new THREE.Group()
  shoulder.position.y = specs.d1

  const shoulderGeometry = new THREE.SphereGeometry(specs.shoulderRadius, 32, 16)
  const jointMaterial = new THREE.MeshStandardMaterial({
    color: UR16E_SPECS.colors.joints,
    roughness: 0.3,
    metalness: 0.7
  })
  const shoulderMesh = new THREE.Mesh(shoulderGeometry, jointMaterial)
  shoulderMesh.castShadow = true
  shoulder.add(shoulderMesh)

  // Upper arm (Shoulder to Elbow)
  const upperArmGeometry = new THREE.CylinderGeometry(40, 40, specs.a2, 16)
  const linkMaterial = new THREE.MeshStandardMaterial({
    color: UR16E_SPECS.colors.links,
    roughness: 0.4,
    metalness: 0.6
  })
  const upperArm = new THREE.Mesh(upperArmGeometry, linkMaterial)
  upperArm.position.x = specs.a2 / 2
  upperArm.rotation.z = Math.PI / 2
  upperArm.castShadow = true
  shoulder.add(upperArm)

  robot.add(shoulder)
  robot.userData.shoulder = shoulder

  // Joint 2 (Elbow)
  const elbow = new THREE.Group()
  elbow.position.set(specs.a2, specs.d1, 0)

  const elbowGeometry = new THREE.SphereGeometry(specs.elbowRadius, 32, 16)
  const elbowMesh = new THREE.Mesh(elbowGeometry, jointMaterial)
  elbowMesh.castShadow = true
  elbow.add(elbowMesh)

  // Forearm (Elbow to Wrist)
  const forearmGeometry = new THREE.CylinderGeometry(35, 35, specs.a3, 16)
  const forearm = new THREE.Mesh(forearmGeometry, linkMaterial)
  forearm.position.x = specs.a3 / 2
  forearm.rotation.z = Math.PI / 2
  forearm.castShadow = true
  elbow.add(forearm)

  robot.add(elbow)
  robot.userData.elbow = elbow

  // Wrist assembly
  const wrist = new THREE.Group()
  wrist.position.set(specs.a2 + specs.a3, specs.d1, 0)

  const wristGeometry = new THREE.SphereGeometry(specs.wristRadius, 32, 16)
  const wristMesh = new THREE.Mesh(wristGeometry, jointMaterial)
  wristMesh.castShadow = true
  wrist.add(wristMesh)

  // Flange
  const flangeGeometry = new THREE.CylinderGeometry(60, 60, 30, 32)
  const flangeMaterial = new THREE.MeshStandardMaterial({
    color: UR16E_SPECS.colors.flange,
    roughness: 0.2,
    metalness: 0.8
  })
  const flange = new THREE.Mesh(flangeGeometry, flangeMaterial)
  flange.position.z = specs.d6 / 2
  flange.rotation.x = Math.PI / 2
  flange.castShadow = true
  wrist.add(flange)

  robot.add(wrist)
  robot.userData.wrist = wrist
  robot.userData.flange = flange

  scene.add(robot)
  return robot
}

/**
 * Crear efector final (plano aspirante con ventosas)
 */
function createEndEffector() {
  endEffector = new THREE.Group()
  const specs = END_EFFECTOR_SPECS.dimensions
  const cups = END_EFFECTOR_SPECS.suction_cups

  // Placa principal
  const plateGeometry = new THREE.BoxGeometry(specs.width, specs.thickness, specs.length)
  const plateMaterial = new THREE.MeshStandardMaterial({
    color: END_EFFECTOR_SPECS.colors.plate,
    roughness: 0.4,
    metalness: 0.6
  })
  const plate = new THREE.Mesh(plateGeometry, plateMaterial)
  plate.position.y = -specs.height
  plate.castShadow = true
  endEffector.add(plate)

  // Ventosas
  const cupGeometry = new THREE.CylinderGeometry(cups.diameter / 2, cups.diameter / 2, 30, 16)
  const cupMaterial = new THREE.MeshStandardMaterial({
    color: END_EFFECTOR_SPECS.colors.suction_cup,
    roughness: 0.3,
    metalness: 0.7
  })

  // Calcular posiciones de ventosas
  const startX = -(cups.cols - 1) * cups.spacing.x / 2
  const startZ = -(cups.rows - 1) * cups.spacing.y / 2

  for (let row = 0; row < cups.rows; row++) {
    for (let col = 0; col < cups.cols; col++) {
      const cup = new THREE.Mesh(cupGeometry, cupMaterial)
      cup.position.set(
        startX + col * cups.spacing.x,
        -specs.height - specs.thickness / 2 - 15,
        startZ + row * cups.spacing.y
      )
      cup.castShadow = true
      endEffector.add(cup)
    }
  }

  // Marco de soporte
  const frameGeometry = new THREE.BoxGeometry(10, specs.height, specs.length + 20)
  const frameMaterial = new THREE.MeshStandardMaterial({
    color: 0x7F8C8D,
    roughness: 0.5,
    metalness: 0.5
  })

  const frame1 = new THREE.Mesh(frameGeometry, frameMaterial)
  frame1.position.set(-specs.width / 2 + 10, -specs.height / 2, 0)
  frame1.castShadow = true
  endEffector.add(frame1)

  const frame2 = new THREE.Mesh(frameGeometry, frameMaterial)
  frame2.position.set(specs.width / 2 - 10, -specs.height / 2, 0)
  frame2.castShadow = true
  endEffector.add(frame2)

  return endEffector
}

/**
 * Crear modelo del producto/caja
 */
function createProduct(dimensions) {
  if (product) {
    scene.remove(product)
  }

  product = new THREE.Group()

  // Caja
  const boxGeometry = new THREE.BoxGeometry(dimensions.width, dimensions.height, dimensions.length)
  const boxMaterial = new THREE.MeshStandardMaterial({
    color: PRODUCT_SPECS.colors.box,
    roughness: 0.8,
    metalness: 0.1,
    transparent: true,
    opacity: 0.9
  })
  const box = new THREE.Mesh(boxGeometry, boxMaterial)
  box.castShadow = true
  box.receiveShadow = true
  product.add(box)

  // Bordes para mejor visualización
  const edges = new THREE.EdgesGeometry(boxGeometry)
  const lineMaterial = new THREE.LineBasicMaterial({ color: 0x2C3E50, linewidth: 2 })
  const wireframe = new THREE.LineSegments(edges, lineMaterial)
  product.add(wireframe)

  scene.add(product)
  return product
}

/**
 * Crear visualización del workspace
 */
function createWorkspace() {
  workspace = new THREE.Group()

  // Cilindro del alcance máximo
  const reachGeometry = new THREE.CylinderGeometry(
    UR16E_SPECS.workspace.maxReach,
    UR16E_SPECS.workspace.maxReach,
    UR16E_SPECS.workspace.maxHeight - UR16E_SPECS.workspace.minHeight,
    32,
    1,
    true
  )
  const reachMaterial = new THREE.MeshBasicMaterial({
    color: 0x3498DB,
    transparent: true,
    opacity: 0.1,
    side: THREE.DoubleSide,
    wireframe: true
  })
  const reachCylinder = new THREE.Mesh(reachGeometry, reachMaterial)
  reachCylinder.position.y = (UR16E_SPECS.workspace.maxHeight + UR16E_SPECS.workspace.minHeight) / 2
  workspace.add(reachCylinder)

  // Círculo del alcance en el suelo
  const circleGeometry = new THREE.RingGeometry(
    UR16E_SPECS.workspace.maxReach - 5,
    UR16E_SPECS.workspace.maxReach,
    64
  )
  const circleMaterial = new THREE.MeshBasicMaterial({
    color: 0x3498DB,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.3
  })
  const circle = new THREE.Mesh(circleGeometry, circleMaterial)
  circle.rotation.x = -Math.PI / 2
  circle.position.y = 1
  workspace.add(circle)

  scene.add(workspace)
  return workspace
}

/**
 * Actualizar posición del robot basado en pose
 */
function updateRobotPose(pose) {
  if (!robot || !endEffector) return

  currentPose.value = pose

  // Calcular cinemática inversa (simplificada)
  const joints = calculateInverseKinematics(pose)

  // Actualizar articulaciones (simplificado - en producción sería más complejo)
  // Por ahora, movemos el TCP directamente
  const tcp = new THREE.Vector3(pose.x, pose.z, -pose.y)

  if (robot.userData.wrist) {
    robot.userData.wrist.position.set(tcp.x, tcp.y, tcp.z)

    // Añadir efector final al wrist
    if (endEffector && !robot.userData.wrist.children.includes(endEffector)) {
      robot.userData.wrist.add(endEffector)
    }

    // Actualizar orientación
    robot.userData.wrist.rotation.set(pose.rx, pose.ry, pose.rz)
  }

  // Actualizar posición del producto (debajo del efector)
  if (product && endEffector) {
    const effectorPosition = new THREE.Vector3()
    endEffector.getWorldPosition(effectorPosition)
    product.position.set(
      effectorPosition.x,
      effectorPosition.y - END_EFFECTOR_SPECS.dimensions.height - props.productDimensions.height / 2 - 50,
      effectorPosition.z
    )
  }

  // Verificar si está dentro de límites
  const distance = Math.sqrt(pose.x * pose.x + pose.y * pose.y)
  isWithinLimits.value = distance <= UR16E_SPECS.workspace.maxReach &&
                         pose.z >= UR16E_SPECS.workspace.minHeight &&
                         pose.z <= UR16E_SPECS.workspace.maxHeight
}

/**
 * Cambiar vista de cámara
 */
function setCameraView(view) {
  const distance = 1500

  switch (view) {
    case 'front':
      camera.position.set(0, 300, distance)
      break
    case 'top':
      camera.position.set(0, distance, 0)
      break
    case 'side':
      camera.position.set(distance, 300, 0)
      break
    case 'iso':
    default:
      camera.position.set(distance, distance, distance)
      break
  }

  controls.target.set(0, 300, 0)
  controls.update()
}

/**
 * Toggle workspace visibility
 */
function toggleWorkspace() {
  if (workspace) {
    workspace.visible = showWorkspace.value
  }
}

/**
 * Toggle grid visibility
 */
function toggleGrid() {
  if (gridHelper) {
    gridHelper.visible = showGrid.value
  }
}

/**
 * Toggle axes visibility
 */
function toggleAxes() {
  if (axesHelper) {
    axesHelper.visible = showAxes.value
  }
}

/**
 * Toggle trajectory visibility
 */
function toggleTrajectory() {
  // Implementar visualización de trayectoria
  if (trajectoryLine) {
    trajectoryLine.visible = showTrajectory.value
  }
}

/**
 * Animation loop
 */
function animate() {
  requestAnimationFrame(animate)
  controls.update()
  renderer.render(scene, camera)
}

/**
 * Handle window resize
 */
function onWindowResize() {
  if (!canvasContainer.value) return

  camera.aspect = canvasContainer.value.clientWidth / canvasContainer.value.clientHeight
  camera.updateProjectionMatrix()
  renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight)
}

// Lifecycle hooks
onMounted(() => {
  initScene()
  createRobot()
  endEffector = createEndEffector()
  createProduct(props.productDimensions)
  createWorkspace()

  updateRobotPose(props.pose)
  animate()

  window.addEventListener('resize', onWindowResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onWindowResize)
  if (renderer) {
    renderer.dispose()
  }
})

// Watch for pose changes
watch(() => props.pose, (newPose) => {
  updateRobotPose(newPose)
}, { deep: true })

// Watch for product dimensions changes
watch(() => props.productDimensions, (newDimensions) => {
  createProduct(newDimensions)
}, { deep: true })
</script>

<style scoped>
.robot-3d-viewer {
  position: relative;
  width: 100%;
  height: 600px;
  border-radius: 8px;
  overflow: hidden;
  background: #f0f0f0;
}

.canvas-container {
  width: 100%;
  height: 100%;
}

.controls-panel {
  position: absolute;
  top: 16px;
  left: 16px;
  background: rgba(255, 255, 255, 0.95);
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.control-group {
  margin-bottom: 12px;
}

.control-group:last-child {
  margin-bottom: 0;
}

.control-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 8px;
}

.control-label input[type="checkbox"] {
  margin-right: 8px;
}

.button-group {
  display: flex;
  gap: 4px;
}

.btn-view {
  padding: 6px 12px;
  font-size: 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-view:hover {
  background: #f0f0f0;
  border-color: #3498db;
}

.btn-view.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.info-panel {
  position: absolute;
  bottom: 16px;
  right: 16px;
  background: rgba(255, 255, 255, 0.95);
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  min-width: 250px;
}

.info-panel h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  font-size: 12px;
  color: #34495e;
  margin-bottom: 12px;
}

.info-status {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.valid {
  background: #d5f4e6;
  color: #27ae60;
}

.status-badge.invalid {
  background: #fadbd8;
  color: #e74c3c;
}
</style>
