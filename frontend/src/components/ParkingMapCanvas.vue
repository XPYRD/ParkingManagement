<template>
  <div class="relative w-full h-full bg-[#f8fafc] overflow-hidden cursor-move select-none" 
       ref="container"
       @mousedown="startPan"
       @mousemove="handlePan"
       @mouseup="stopPan"
       @mouseleave="stopPan"
       @wheel="handleZoom"
       @click="handleCanvasClick"
  >
    <canvas ref="canvasRef" class="w-full h-full"></canvas>
    
    <!-- 工具栏 -->
    <div class="absolute top-6 right-6 flex flex-col gap-2">
       <el-button circle size="small" @click="resetView" title="重置视图">
          <span class="material-symbols-outlined scale-75">home</span>
       </el-button>
       <el-button circle size="small" @click="zoomIn" title="放大">
          <span class="material-symbols-outlined scale-75">add</span>
       </el-button>
       <el-button circle size="small" @click="zoomOut" title="缩小">
          <span class="material-symbols-outlined scale-75">remove</span>
       </el-button>
    </div>
    
    <!-- 图例 -->
    <div class="absolute bottom-6 left-6 bg-white/90 backdrop-blur-sm rounded-lg p-3 shadow-lg text-sm">
      <div class="space-y-1.5">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-green-500 rounded"></div>
          <span>空闲</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-red-500 rounded"></div>
          <span>已占用</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-blue-500 rounded"></div>
          <span>已预约</span>
        </div>
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 bg-gray-400 rounded"></div>
          <span>维修中</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  spots: { type: Array, required: true },
  selectedId: { type: [String, Number], default: null }
})

const emit = defineEmits(['select'])

const container = ref(null)
const canvasRef = ref(null)
let ctx = null

// 地图配置 (统一坐标系: 0-100 百分比)
const MAP_W = 4000
const MAP_H = 3000
const SPOT_W = 80     // 单个车位宽度
const SPOT_H = 120    // 单个车位高度
const MARGIN = 150    // 停车区域边距

const offset = ref({ x: 100, y: 100 })
const zoom = ref(0.55)
const isPanning = ref(false)
const lastMouse = ref({ x: 0, y: 0 })

/**
 * 主渲染函数 - 分层设计
 */
function draw() {
  if (!ctx || !canvasRef.value) return
  
  const w = canvasRef.value.clientWidth
  const h = canvasRef.value.clientHeight
  
  ctx.clearRect(0, 0, w, h)
  ctx.save()
  ctx.translate(offset.value.x, offset.value.y)
  ctx.scale(zoom.value, zoom.value)
  
  // 1. 白色背景
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, MAP_W, MAP_H)
  
  // 2. 灰色网格参考线
  drawGridBackground()
  
  // 3. 停车位框架 (灰色)
  drawParkingFramework()
  
  // 4. 道路与设施
  drawRoads()
  drawFacilities()
  
  // 5. 区域标签
  drawAreaLabels()
  
  // 6. 动态车位状态
  props.spots.forEach(spot => drawSpot(spot))
  
  // 7. 边界
  drawBoundary()
  
  ctx.restore()
}

/**
 * 1. 背景网格 (淡灰)
 */
function drawGridBackground() {
  ctx.strokeStyle = '#f0f0f0'
  ctx.lineWidth = 1
  const gridSize = 200
  
  for (let x = 0; x <= MAP_W; x += gridSize) {
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, MAP_H)
    ctx.stroke()
  }
  
  for (let y = 0; y <= MAP_H; y += gridSize) {
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(MAP_W, y)
    ctx.stroke()
  }
}

/**
 * 2. 停车位框架 - 根据数据库坐标
 */
function drawParkingFramework() {
  ctx.strokeStyle = '#d1d5db'
  ctx.lineWidth = 1.5
  
  // 遍历所有传入的车位数据，用其 floor_x, floor_y 绘制框架
  const drawnSpots = new Set()
  
  props.spots.forEach(spot => {
    const key = `${spot.floor_x}-${spot.floor_y}`
    if (drawnSpots.has(key)) return
    drawnSpots.add(key)
    
    // 转换百分比坐标到像素
    const x = (spot.floor_x / 100) * MAP_W
    const y = (spot.floor_y / 100) * MAP_H
    
    ctx.strokeRect(x - SPOT_W/2, y - SPOT_H/2, SPOT_W, SPOT_H)
  })
}

/**
 * 3. 道路系统
 */
function drawRoads() {
  // 主道路 (浅灰色)
  ctx.fillStyle = '#f5f5f5'
  
  // 水平主干道
  ctx.fillRect(0, 900, MAP_W, 350)
  ctx.fillRect(0, 1900, MAP_W, 350)
  
  // 竖向主干道
  ctx.fillRect(700, 0, 400, MAP_H)
  ctx.fillRect(2400, 0, 400, MAP_H)
  
  // 道路中心线 (黄色虚线)
  ctx.strokeStyle = '#fbbf24'
  ctx.lineWidth = 2
  ctx.setLineDash([20, 20])
  
  ctx.beginPath()
  ctx.moveTo(0, 900 + 175)
  ctx.lineTo(MAP_W, 900 + 175)
  ctx.stroke()
  
  ctx.beginPath()
  ctx.moveTo(0, 1900 + 175)
  ctx.lineTo(MAP_W, 1900 + 175)
  ctx.stroke()
  
  ctx.beginPath()
  ctx.moveTo(700 + 200, 0)
  ctx.lineTo(700 + 200, MAP_H)
  ctx.stroke()
  
  ctx.beginPath()
  ctx.moveTo(2400 + 200, 0)
  ctx.lineTo(2400 + 200, MAP_H)
  ctx.stroke()
  
  ctx.setLineDash([])
}

/**
 * 4. 设施标记
 */
function drawFacilities() {
  // 电梯/出入口 (浅蓝背景)
  ctx.fillStyle = '#dbeafe'
  ctx.fillRect(3100, 200, 300, 280)
  
  ctx.fillStyle = '#0369a1'
  ctx.font = 'bold 28px Arial'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('🛗 LIFT', 3250, 280)
  ctx.font = '16px Arial'
  ctx.fillText('电梯/出入口', 3250, 320)
  
  // 入口箭头标记
  drawArrow(300, 1200, 0, '📍 入口')
  drawArrow(3600, 1500, Math.PI, '📍 出口')
}

/**
 * 绘制箭头与标签
 */
function drawArrow(x, y, angle, label) {
  ctx.save()
  ctx.translate(x, y)
  ctx.rotate(angle)
  
  ctx.fillStyle = '#1e40af'
  ctx.beginPath()
  ctx.moveTo(0, 0)
  ctx.lineTo(-30, -20)
  ctx.lineTo(-30, 20)
  ctx.closePath()
  ctx.fill()
  
  ctx.restore()
  
  ctx.fillStyle = '#374151'
  ctx.font = '14px Arial'
  ctx.textAlign = 'center'
  ctx.fillText(label, x, y + 40)
}

/**
 * 5. 区域标签
 */
function drawAreaLabels() {
  ctx.font = 'bold 32px Arial'
  ctx.fillStyle = '#9ca3af'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  
  // A 区
  ctx.fillText('A 区', 500, 500)
  
  // B 区
  ctx.fillText('B 区', 2000, 500)
  
  // C 区 (下层)
  ctx.fillText('C 区', 500, 2600)
}

/**
 * 6. 单个车位绘制 - 关键函数
 */
function drawSpot(spot) {
  // 转换坐标: 百分比 → 像素
  const x = (spot.floor_x / 100) * MAP_W
  const y = (spot.floor_y / 100) * MAP_H
  
  ctx.save()
  ctx.translate(x, y)
  
  // 旋转 (B 区车位倾斜)
  if (spot.zone === 'B') {
    ctx.rotate((32 * Math.PI) / 180)
  }
  
  // 填充状态颜色
  ctx.fillStyle = getStatusColor(spot.status)
  ctx.fillRect(-SPOT_W/2 + 2, -SPOT_H/2 + 2, SPOT_W - 4, SPOT_H - 4)
  
  // 选中边框 (蓝色)
  if (spot.id === props.selectedId) {
    ctx.strokeStyle = '#2563eb'
    ctx.lineWidth = 3
    ctx.strokeRect(-SPOT_W/2, -SPOT_H/2, SPOT_W, SPOT_H)
  }
  
  // 车位类型图标
  ctx.font = 'bold 24px Arial'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillStyle = 'white'
  
  if (spot.spot_type === 'ev') {
    ctx.fillText('⚡', 0, -35)
  } else if (spot.spot_type === 'vip') {
    ctx.fillText('👑', 0, -35)
  } else if (spot.spot_type === 'accessible') {
    ctx.fillText('♿', 0, -35)
  }
  
  // 车位编号 (只在足够放大时显示)
  if (zoom.value > 0.35) {
    ctx.font = 'bold 14px Arial'
    ctx.fillStyle = 'white'
    ctx.fillText(spot.spot_id.split('-').pop(), 0, 10)
  }
  
  ctx.restore()
}

/**
 * 7. 边界框
 */
function drawBoundary() {
  ctx.strokeStyle = '#1f2937'
  ctx.lineWidth = 12
  ctx.strokeRect(5, 5, MAP_W - 10, MAP_H - 10)
}

/**
 * 获取状态颜色
 */
function getStatusColor(status) {
  const colors = {
    'free': '#10b981',        // 翠绿
    'occupied': '#ef4444',    // 鲜红
    'reserved': '#3b82f6',    // 海蓝
    'maintenance': '#9ca3af', // 灰色
    'overstay': '#f97316'     // 橙红
  }
  return colors[status] || '#e5e7eb'
}

// ════════════════ 交互控制 ════════════════

function startPan(e) {
  isPanning.value = true
  lastMouse.value = { x: e.clientX, y: e.clientY }
}

function handlePan(e) {
  if (!isPanning.value) return
  const dx = e.clientX - lastMouse.value.x
  const dy = e.clientY - lastMouse.value.y
  offset.value.x += dx
  offset.value.y += dy
  lastMouse.value = { x: e.clientX, y: e.clientY }
  draw()
}

function stopPan() {
  isPanning.value = false
}

function handleZoom(e) {
  e.preventDefault()
  const factor = e.deltaY > 0 ? 0.9 : 1.1
  const newZoom = zoom.value * factor
  
  if (newZoom < 0.2 || newZoom > 3) return
  
  // 以鼠标位置为中心缩放
  const rect = canvasRef.value.getBoundingClientRect()
  const mx = e.clientX - rect.left
  const my = e.clientY - rect.top
  
  offset.value.x = mx + (offset.value.x - mx) * factor
  offset.value.y = my + (offset.value.y - my) * factor
  zoom.value = newZoom
  
  draw()
}

function handleCanvasClick(e) {
  if (isPanning.value) return
  
  const rect = canvasRef.value.getBoundingClientRect()
  const clientX = e.clientX - rect.left
  const clientY = e.clientY - rect.top
  
  // 屏幕坐标 → 逻辑坐标
  const logicX = (clientX - offset.value.x) / zoom.value
  const logicY = (clientY - offset.value.y) / zoom.value
  
  // 查找点击的车位
  for (const spot of props.spots) {
    const sx = (spot.floor_x / 100) * MAP_W
    const sy = (spot.floor_y / 100) * MAP_H
    
    // 简单矩形碰撞检测
    if (Math.abs(logicX - sx) < SPOT_W/2 && Math.abs(logicY - sy) < SPOT_H/2) {
      emit('select', spot)
      draw()
      return
    }
  }
}

function resetView() {
  offset.value = { x: 100, y: 100 }
  zoom.value = 0.55
  draw()
}

function zoomIn() {
  zoom.value = Math.min(zoom.value * 1.2, 3)
  draw()
}

function zoomOut() {
  zoom.value = Math.max(zoom.value * 0.8, 0.2)
  draw()
}

function resize() {
  if (!container.value || !canvasRef.value) return
  canvasRef.value.width = container.value.clientWidth
  canvasRef.value.height = container.value.clientHeight
  draw()
}

let animId = null
function animate() {
  draw()
  animId = requestAnimationFrame(animate)
}

onMounted(() => {
  ctx = canvasRef.value.getContext('2d')
  resize()
  window.addEventListener('resize', resize)
  animate()
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  if (animId) cancelAnimationFrame(animId)
})

watch(() => props.spots, () => {
  draw()
}, { deep: true })
</script>
