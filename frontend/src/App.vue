<template>
  <div class="app">
    <header class="header">
      <h1>拣货路线比赛</h1>
      <div class="header-controls">
        <button @click="generateNewOrder">新订单</button>
        <label>行数 <input type="number" v-model.number="mapParams.x" min="2" max="4" @change="generateNewOrder" /></label>
        <label>段数 <input type="number" v-model.number="mapParams.k" min="2" max="6" @change="generateNewOrder" /></label>
        <label>货架数/段 <input type="number" v-model.number="mapParams.b" min="2" max="6" @change="generateNewOrder" /></label>
        <label>SKU数 <input type="number" v-model.number="mapParams.numSkus" min="3" max="10" @change="generateNewOrder" /></label>
      </div>
    </header>

    <main class="main">
      <div class="map-panel">
        <svg ref="svgRef" :width="canvasWidth" :height="canvasHeight" @click="handleMapClick">
          <g v-for="(row, r) in mapGrid" :key="'row-'+r">
            <rect
              v-for="(cell, c) in row"
              :key="'cell-'+r+'-'+c"
              :x="c * cellSize"
              :y="r * cellSize"
              :width="cellSize"
              :height="cellSize"
              :fill="getCellColor(cell, r, c)"
              stroke="#ddd"
              stroke-width="0.5"
            />
          </g>
          
          <circle
            v-for="(sku, idx) in orderSkus"
            :key="'sku-'+idx"
            :cx="sku.col * cellSize + cellSize/2"
            :cy="sku.row * cellSize + cellSize/2"
            :r="cellSize/3"
            :fill="getSkuColor(sku)"
            class="sku-point"
          />
          <text
            v-for="(sku, idx) in orderSkus"
            :key="'sku-label-'+idx"
            :x="sku.col * cellSize + cellSize/2"
            :y="sku.row * cellSize + cellSize/2 + 4"
            text-anchor="middle"
            font-size="10"
            fill="#000"
          >{{ sku.label }}</text>

          <circle
            :cx="startPoint[1] * cellSize + cellSize/2"
            :cy="startPoint[0] * cellSize + cellSize/2"
            :r="cellSize/3"
            fill="#22c55e"
          />
          <text
            :x="startPoint[1] * cellSize + cellSize/2"
            :y="startPoint[0] * cellSize + cellSize/2 + 4"
            text-anchor="middle"
            font-size="10"
            fill="#fff"
          >A</text>

          <line
            v-for="(seg, idx) in humanRouteSegments"
            :key="'human-seg-'+idx"
            :x1="seg.x1 * cellSize + cellSize/2"
            :y1="seg.y1 * cellSize + cellSize/2"
            :x2="seg.x2 * cellSize + cellSize/2"
            :y2="seg.y2 * cellSize + cellSize/2"
            stroke="#3b82f6"
            stroke-width="3"
            stroke-linecap="round"
          />

          <line
            v-for="(seg, idx) in aiRouteSegments"
            :key="'ai-seg-'+idx"
            :x1="seg.x1 * cellSize + cellSize/2"
            :y1="seg.y1 * cellSize + cellSize/2"
            :x2="seg.x2 * cellSize + cellSize/2"
            :y2="seg.y2 * cellSize + cellSize/2"
            stroke="#ef4444"
            stroke-width="2"
            stroke-dasharray="5,3"
            v-show="gameState === 'finished' || gameState === 'running'"
          />

          <circle
            :cx="humanBall.x * cellSize + cellSize/2"
            :cy="humanBall.y * cellSize + cellSize/2"
            :r="cellSize/4"
            fill="#3b82f6"
            v-show="gameState === 'running' || gameState === 'finished'"
          />
          <circle
            :cx="aiBall.x * cellSize + cellSize/2"
            :cy="aiBall.y * cellSize + cellSize/2"
            :r="cellSize/4"
            fill="#ef4444"
            v-show="gameState === 'running' || gameState === 'finished'"
          />
        </svg>
      </div>

      <div class="side-panel">
        <div class="order-section">
          <h2>订单列表</h2>
          <ul class="order-list">
            <li v-for="sku in orderSkus" :key="sku.sku_id">
              {{ sku.label }}: ({{ sku.row }}, {{ sku.col }})
            </li>
          </ul>
        </div>

        <div class="route-section">
          <h2>你的路线</h2>
          <ul class="route-list" v-if="selectedWaypoints.length > 0">
            <li><strong>起点 A</strong></li>
            <li v-for="(wp, idx) in selectedWaypoints" :key="idx">
              {{ getSkuByPos(wp).label }}
            </li>
            <li><strong>返回 A</strong></li>
          </ul>
          <p v-else class="hint">点击地图上的SKU点选择顺序</p>
        </div>

        <div class="distance-section">
          <div class="distance-row">
            <span>你的路线长度:</span>
            <span class="value">{{ humanDistance !== null ? humanDistance : '--' }}</span>
          </div>
          <div class="distance-row">
            <span>AI路线长度:</span>
            <span class="value">{{ aiDistance !== null ? aiDistance : '--' }}</span>
          </div>
          <div class="distance-row result" v-if="gameState === 'finished'">
            <span>{{ getResultText() }}</span>
          </div>
        </div>

        <div class="controls">
          <button @click="undoWaypoint" :disabled="selectedWaypoints.length === 0 || gameState !== 'planning'">撤销</button>
          <button @click="clearWaypoints" :disabled="selectedWaypoints.length === 0 || gameState !== 'planning'">清空</button>
          <button @click="startGame" :disabled="selectedWaypoints.length !== orderSkus.length || gameState !== 'planning'">开始比赛</button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

const API_BASE = '/api'

const cellSize = 30

const svgRef = ref(null)
const mapGrid = ref([])
const rows = ref(0)
const cols = ref(0)
const startPoint = ref([0, 0])
const orderSkus = ref([])
const selectedWaypoints = ref([])
const humanRoute = ref([])
const humanRouteSegments = ref([])
const aiRoute = ref([])
const aiRouteSegments = ref([])
const humanDistance = ref(null)
const aiDistance = ref(null)
const gameState = ref('planning')
const humanBall = ref({ x: 0, y: 0 })
const aiBall = ref({ x: 0, y: 0 })

const mapParams = ref({
  x: 4,
  k: 4,
  b: 3,
  numSkus: 5
})

const canvasWidth = computed(() => cols.value * cellSize)
const canvasHeight = computed(() => rows.value * cellSize)

async function loadMapInfo() {
  try {
    const res = await axios.get(`${API_BASE}/map_info`)
    if (res.data.success) {
      rows.value = res.data.rows
      cols.value = res.data.cols
      startPoint.value = res.data.start
      mapGrid.value = []
      for (let r = 0; r < rows.value; r++) {
        const row = []
        for (let c = 0; c < cols.value; c++) {
          const isWalkable = res.data.walkable_points.some(p => p[0] === r && p[1] === c)
          row.push(isWalkable ? 0 : 1)
        }
        mapGrid.value.push(row)
      }
    }
  } catch (e) {
    console.error('Failed to load map:', e)
  }
}

async function generateNewOrder() {
  try {
    const res = await axios.post(`${API_BASE}/generate_order`, {
      x: mapParams.value.x,
      k: mapParams.value.k,
      b: mapParams.value.b,
      num_skus: mapParams.value.numSkus
    })
    if (res.data.success) {
      orderSkus.value = res.data.order.skus
      selectedWaypoints.value = []
      humanRoute.value = []
      humanRouteSegments.value = []
      aiRoute.value = []
      aiRouteSegments.value = []
      humanDistance.value = null
      aiDistance.value = null
      gameState.value = 'planning'
      await loadMapInfo()
      await calculateHumanRoute()
    }
  } catch (e) {
    console.error('Failed to generate order:', e)
  }
}

async function calculateHumanRoute() {
  if (selectedWaypoints.value.length === 0) {
    humanRoute.value = []
    humanRouteSegments.value = []
    humanDistance.value = null
    return
  }
  try {
    const res = await axios.post(`${API_BASE}/route_from_waypoints`, {
      waypoints: selectedWaypoints.value,
      return_to_start: false
    })
    if (res.data.success) {
      humanRoute.value = res.data.route
      humanDistance.value = res.data.total_distance
      humanRouteSegments.value = computeSegments(res.data.route, false)
    }
  } catch (e) {
    console.error('Failed to calculate human route:', e)
  }
}

async function calculateHumanRouteFull() {
  try {
    const res = await axios.post(`${API_BASE}/route_from_waypoints`, {
      waypoints: selectedWaypoints.value,
      return_to_start: true
    })
    if (res.data.success) {
      humanRoute.value = res.data.route
      humanDistance.value = res.data.total_distance
      humanRouteSegments.value = computeSegments(res.data.route, false)
    }
  } catch (e) {
    console.error('Failed to calculate human route:', e)
  }
}

async function calculateAiRoute() {
  try {
    const res = await axios.post(`${API_BASE}/solve`, {
      start: startPoint.value,
      middle_points: orderSkus.value.map(s => [s.row, s.col])
    })
    if (res.data.success) {
      aiRoute.value = res.data.route
      aiDistance.value = res.data.total_distance
      aiRouteSegments.value = computeSegments(res.data.route, true)
    }
  } catch (e) {
    console.error('Failed to calculate AI route:', e)
  }
}

function computeSegments(route, isAi = false) {
  if (route.length < 2) return []
  const segments = []
  const OFFSET = 0.15
  const dir = isAi ? -1 : 1
  for (let i = 0; i < route.length - 1; i++) {
    const r1 = route[i][0], c1 = route[i][1]
    const r2 = route[i + 1][0], c2 = route[i + 1][1]
    const dr = r2 - r1, dc = c2 - c1
    const ox = -dr * OFFSET * dir
    const oy = -dc * OFFSET * dir
    segments.push({
      x1: c1 + ox,
      y1: r1 + oy,
      x2: c2 + ox,
      y2: r2 + oy
    })
  }
  return segments
}

function handleMapClick(event) {
  if (gameState.value !== 'planning') return
  
  const rect = svgRef.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  const col = Math.floor(x / cellSize)
  const row = Math.floor(y / cellSize)

  const sku = orderSkus.value.find(s => s.row === row && s.col === col)
  if (!sku) return
  
  const isAlreadySelected = selectedWaypoints.value.some(
    wp => wp[0] === row && wp[1] === col
  )
  if (isAlreadySelected) return
  
  selectedWaypoints.value.push([row, col])
}

function getSkuByPos(pos) {
  return orderSkus.value.find(s => s.row === pos[0] && s.col === pos[1]) || {}
}

function getCellColor(cell, r, c) {
  if (cell === 1) return '#6b7280'
  const isStart = r === startPoint.value[0] && c === startPoint.value[1]
  if (isStart) return '#22c55e'
  return '#e5e7eb'
}

function getSkuColor(sku) {
  const idx = selectedWaypoints.value.findIndex(
    wp => wp[0] === sku.row && wp[1] === sku.col
  )
  if (idx !== -1) {
    const colors = ['#fbbf24', '#f97316', '#ec4899', '#8b5cf6', '#06b6d4', '#10b981']
    return colors[idx % colors.length]
  }
  return '#fde047'
}

function undoWaypoint() {
  if (selectedWaypoints.value.length > 0) {
    selectedWaypoints.value.pop()
  }
}

function clearWaypoints() {
  selectedWaypoints.value = []
}

async function startGame() {
  if (selectedWaypoints.value.length !== orderSkus.value.length) return
  if (humanRoute.value.length === 0) return
  
  await calculateHumanRouteFull()
  await calculateAiRoute()
  
  gameState.value = 'running'
  
  let humanIdx = 0
  let aiIdx = 0
  
  humanBall.value = { x: humanRoute.value[0][1], y: humanRoute.value[0][0] }
  aiBall.value = { x: aiRoute.value[0][1], y: aiRoute.value[0][0] }
  
  const interval = setInterval(() => {
    if (humanIdx < humanRoute.value.length - 1) {
      humanIdx++
      humanBall.value = { x: humanRoute.value[humanIdx][1], y: humanRoute.value[humanIdx][0] }
    }
    if (aiIdx < aiRoute.value.length - 1) {
      aiIdx++
      aiBall.value = { x: aiRoute.value[aiIdx][1], y: aiRoute.value[aiIdx][0] }
    }
    
    if (humanIdx >= humanRoute.value.length - 1 && aiIdx >= aiRoute.value.length - 1) {
      clearInterval(interval)
      gameState.value = 'finished'
    }
  }, 200)
}

function getResultText() {
  if (humanDistance.value === null || aiDistance.value === null) return ''
  if (humanDistance.value < aiDistance.value) return '你赢了！'
  if (humanDistance.value > aiDistance.value) return 'AI赢了'
  return '平局！'
}

watch(selectedWaypoints, () => {
  calculateHumanRoute()
}, { deep: true })

onMounted(async () => {
  await loadMapInfo()
  await generateNewOrder()
})
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #1f2937;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  font-size: 1.5rem;
}

.header-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.header-controls select, .header-controls input[type="number"] {
  padding: 0.5rem;
  border-radius: 0.25rem;
  border: none;
  width: 140px;
}

.header-controls label {
  color: white;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.header-controls button {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
}

.header-controls button:hover {
  background: #2563eb;
}

.main {
  display: flex;
  flex: 1;
  gap: 1rem;
  padding: 1rem;
}

.map-panel {
  flex: 1;
  background: white;
  border-radius: 0.5rem;
  padding: 1rem;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  overflow: auto;
}

.side-panel {
  width: 300px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.side-panel > div {
  background: white;
  border-radius: 0.5rem;
  padding: 1rem;
}

h2 {
  font-size: 1rem;
  margin-bottom: 0.5rem;
  color: #374151;
}

.order-list, .route-list {
  list-style: none;
  font-size: 0.9rem;
}

.order-list li, .route-list li {
  padding: 0.25rem 0;
}

.hint {
  color: #9ca3af;
  font-size: 0.9rem;
}

.distance-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.distance-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.distance-row .value {
  font-weight: bold;
  color: #3b82f6;
}

.distance-row.result {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e5e7eb;
  font-weight: bold;
  color: #10b981;
}

.controls {
  display: flex;
  gap: 0.5rem;
}

.controls button {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-weight: bold;
}

.controls button:nth-child(1) {
  background: #6b7280;
  color: white;
}

.controls button:nth-child(2) {
  background: #ef4444;
  color: white;
}

.controls button:nth-child(3) {
  background: #22c55e;
  color: white;
}

.controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.sku-point {
  cursor: pointer;
  transition: filter 0.15s;
  filter: drop-shadow(0 0 0 transparent);
}

.sku-point:hover {
  filter: drop-shadow(0 0 4px #fde047) drop-shadow(0 0 8px #fde047);
}
</style>
