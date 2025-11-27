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
 * Crear modelo del robot UR16e con jerarquía correcta
 */
function createRobot() {
  robot = new THREE.Group()
  robot.name = 'UR16e_Robot'
  const specs = UR16E_SPECS.dimensions

  // Materiales
  const baseMaterial = new THREE.MeshStandardMaterial({
    color: UR16E_SPECS.colors.base,
    roughness: 0.5,
    metalness: 0.5
  })
  const jointMaterial = new THREE.MeshStandardMaterial({
    color: UR16E_SPECS.colors.joints,
    roughness: 0.3,
    metalness: 0.7
  })
  const linkMaterial = new THREE.MeshStandardMaterial({
    color: UR16E_SPECS.colors.links,
    roughness: 0.4,
    metalness: 0.6
  })
  const flangeMaterial = new THREE.MeshStandardMaterial({
    color: UR16E_SPECS.colors.flange,
    roughness: 0.2,
    metalness: 0.8
  })

  // BASE FIJA
  const baseGeometry = new THREE.CylinderGeometry(specs.baseRadius, specs.baseRadius, specs.baseHeight, 32)
  const base = new THREE.Mesh(baseGeometry, baseMaterial)
  base.position.y = specs.baseHeight / 2
  base.castShadow = true
  robot.add(base)

  // JOINT 1 - Base rotation (alrededor de Y)
  const j1 = new THREE.Group()
  j1.name = 'joint1_base'
  j1.position.y = specs.d1
  robot.add(j1)

  // Shoulder visual
  const shoulderGeometry = new THREE.SphereGeometry(specs.shoulderRadius, 32, 16)
  const shoulderMesh = new THREE.Mesh(shoulderGeometry, jointMaterial)
  shoulderMesh.castShadow = true
  j1.add(shoulderMesh)

  // JOINT 2 - Shoulder rotation (alrededor de Z local)
  const j2 = new THREE.Group()
  j2.name = 'joint2_shoulder'
  j2.position.set(0, 0, 0) // En el centro del shoulder
  j1.add(j2)

  // Upper arm (brazo superior)
  const upperArmGeometry = new THREE.CylinderGeometry(40, 40, specs.a2, 16)
  const upperArm = new THREE.Mesh(upperArmGeometry, linkMaterial)
  upperArm.position.x = specs.a2 / 2
  upperArm.rotation.z = Math.PI / 2
  upperArm.castShadow = true
  j2.add(upperArm)

  // JOINT 3 - Elbow rotation
  const j3 = new THREE.Group()
  j3.name = 'joint3_elbow'
  j3.position.x = specs.a2
  j2.add(j3)

  // Elbow visual
  const elbowGeometry = new THREE.SphereGeometry(specs.elbowRadius, 32, 16)
  const elbowMesh = new THREE.Mesh(elbowGeometry, jointMaterial)
  elbowMesh.castShadow = true
  j3.add(elbowMesh)

  // Forearm (brazo inferior)
  const forearmGeometry = new THREE.CylinderGeometry(35, 35, specs.a3, 16)
  const forearm = new THREE.Mesh(forearmGeometry, linkMaterial)
  forearm.position.x = specs.a3 / 2
  forearm.rotation.z = Math.PI / 2
  forearm.castShadow = true
  j3.add(forearm)

  // JOINT 4 - Wrist 1
  const j4 = new THREE.Group()
  j4.name = 'joint4_wrist1'
  j4.position.x = specs.a3
  j3.add(j4)

  // Wrist 1 visual
  const wrist1Geometry = new THREE.SphereGeometry(specs.wristRadius, 32, 16)
  const wrist1Mesh = new THREE.Mesh(wrist1Geometry, jointMaterial)
  wrist1Mesh.castShadow = true
  j4.add(wrist1Mesh)

  // JOINT 5 - Wrist 2
  const j5 = new THREE.Group()
  j5.name = 'joint5_wrist2'
  j5.position.y = specs.d4
  j4.add(j5)

  // Wrist 2 visual
  const wrist2Geometry = new THREE.SphereGeometry(specs.wristRadius, 32, 16)
  const wrist2Mesh = new THREE.Mesh(wrist2Geometry, jointMaterial)
  wrist2Mesh.castShadow = true
  j5.add(wrist2Mesh)

  // JOINT 6 - Wrist 3
  const j6 = new THREE.Group()
  j6.name = 'joint6_wrist3'
  j6.position.y = specs.d5
  j5.add(j6)

  // Wrist 3 visual
  const wrist3Geometry = new THREE.SphereGeometry(specs.wristRadius * 0.8, 32, 16)
  const wrist3Mesh = new THREE.Mesh(wrist3Geometry, jointMaterial)
  wrist3Mesh.castShadow = true
  j6.add(wrist3Mesh)

  // FLANGE (Tool mounting plate)
  const flangeGroup = new THREE.Group()
  flangeGroup.name = 'flange'
  flangeGroup.position.y = specs.d6
  j6.add(flangeGroup)

  const flangeGeometry = new THREE.CylinderGeometry(60, 60, 30, 32)
  const flange = new THREE.Mesh(flangeGeometry, flangeMaterial)
  flange.rotation.x = Math.PI / 2
  flange.castShadow = true
  flangeGroup.add(flange)

  // Guardar referencias a las articulaciones
  robot.userData.joints = {
    j1, j2, j3, j4, j5, j6
  }
  robot.userData.flange = flangeGroup

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
  if (!robot || !robot.userData.joints) return

  currentPose.value = pose

  // Calcular cinemática inversa (simplificada)
  const jointAngles = calculateInverseKinematics(pose)

  // Aplicar ángulos a las articulaciones
  const joints = robot.userData.joints

  // J1 - Base rotation (alrededor de Y)
  joints.j1.rotation.y = jointAngles.j1

  // J2 - Shoulder rotation (alrededor de Z local)
  joints.j2.rotation.z = jointAngles.j2

  // J3 - Elbow rotation (alrededor de Z local)
  joints.j3.rotation.z = jointAngles.j3

  // J4, J5, J6 - Wrist rotations
  joints.j4.rotation.z = jointAngles.j4
  joints.j5.rotation.y = jointAngles.j5
  joints.j6.rotation.z = jointAngles.j6

  // Añadir efector final al flange si no está ya
  if (endEffector && robot.userData.flange && !robot.userData.flange.children.includes(endEffector)) {
    robot.userData.flange.add(endEffector)
  }

  // Actualizar posición del producto (debajo del efector)
  if (product && robot.userData.flange) {
    const effectorPosition = new THREE.Vector3()
    robot.userData.flange.getWorldPosition(effectorPosition)

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
                         pose.z <= UR16E_SPECS.workspace.maxReach
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
