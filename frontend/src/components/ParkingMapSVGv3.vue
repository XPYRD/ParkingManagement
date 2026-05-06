/**
 * 📍 停车场地图 - SVG 渲染版本
 * 
 * 功能：
 * ✅ SVG 底图 + 停车位标记
 * ✅ 内部缩放/平移
 * ✅ 停车位点击选择
 * ✅ 实时状态更新
 * ✅ 路径导航渲染
 */

<template>
  <div
    class="relative w-full h-full bg-white overflow-hidden select-none"
    ref="container"
  >
    <div
      class="w-full h-full overflow-hidden map-viewport"
      @dragstart.prevent
    >
      <svg
        ref="svgRef"
        class="w-full h-full"
        :viewBox="`0 0 ${MAP_W} ${MAP_H}`"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <linearGradient id="navigation-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#38bdf8" />
            <stop offset="50%" stop-color="#22c55e" />
            <stop offset="100%" stop-color="#14b8a6" />
          </linearGradient>
          <filter id="navigation-glow" x="-40%" y="-40%" width="180%" height="180%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <marker
            id="navigation-arrow"
            markerWidth="12"
            markerHeight="12"
            refX="10"
            refY="6"
            orient="auto"
            markerUnits="strokeWidth"
          >
            <path d="M0,0 L12,6 L0,12 z" fill="#14b8a6" />
          </marker>
        </defs>

        <g
          id="map-content"
          ref="transformGroup"
          :transform="mapTransform()"
        >
          <image
            v-if="svgDataUrl"
            :href="svgDataUrl"
            x="0"
            y="0"
            :width="MAP_W"
            :height="MAP_H"
            class="pointer-events-none"
          />

          <rect
            v-else
            x="0"
            y="0"
            :width="MAP_W"
            :height="MAP_H"
            fill="#f8f8f8"
            stroke="#ccc"
            stroke-width="2"
          />

          <g v-if="navigationPathPoints.length > 1" class="navigation-layer">
            <path
              :d="navigationPathD"
              fill="none"
              stroke="#0f172a"
              stroke-width="5"
              stroke-linecap="round"
              stroke-linejoin="round"
              opacity="0.12"
              filter="url(#navigation-glow)"
            />
            <path
              :d="navigationPathD"
              fill="none"
              stroke="url(#navigation-gradient)"
              stroke-width="3"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-dasharray="14 10"
              class="navigation-path"
              filter="url(#navigation-glow)"
              marker-end="url(#navigation-arrow)"
            />
            <circle
              :cx="navigationAnchors.start ? navigationAnchors.start.x : navigationPathPoints[0].x"
              :cy="navigationAnchors.start ? navigationAnchors.start.y : navigationPathPoints[0].y"
              r="7"
              fill="#2563eb"
              stroke="#fff"
              stroke-width="3"
              class="navigation-start"
            />
            <circle
              :cx="navigationAnchors.end ? navigationAnchors.end.x : navigationPathPoints[navigationPathPoints.length - 1].x"
              :cy="navigationAnchors.end ? navigationAnchors.end.y : navigationPathPoints[navigationPathPoints.length - 1].y"
              r="7"
              fill="#ef4444"
              stroke="#fff"
              stroke-width="3"
              class="navigation-end"
            />
          </g>

          <g class="spots-layer">
            <g
              v-for="spot in spots"
              :key="spot.id"
              @click="selectSpot(spot)"
              class="spot-group"
              :class="{ selected: spot.id === selectedId }"
              :transform="getSpotTransform(spot)"
            >
              <rect
                x="0"
                y="0"
                :width="SPOT_WIDTH"
                :height="SPOT_HEIGHT"
                :fill="getSpotColor(spot)"
                stroke="#333"
                stroke-width="1"
                :opacity="0.4"
                class="parking-spot"
              />

              <rect
                v-if="spot.id === selectedId"
                x="-2"
                y="-2"
                :width="SPOT_WIDTH + 4"
                :height="SPOT_HEIGHT + 4"
                fill="none"
                stroke="#3b82f6"
                stroke-width="3"
              />

              <text
                v-if="zoom > 0.4"
                :x="SPOT_WIDTH / 2"
                :y="SPOT_HEIGHT / 2 + 2"
                text-anchor="middle"
                dominant-baseline="middle"
                class="spot-label"
                font-size="12"
                font-weight="bold"
                fill="#fff"
                pointer-events="none"
                :transform="getLabelTransform(spot)"
              >
                {{ spot.spot_id?.split('-')?.pop() }}
              </text>

              <text
                v-if="spot.spot_type === 'ev'"
                :x="SPOT_WIDTH / 2"
                :y="SPOT_HEIGHT / 2 - 12"
                text-anchor="middle"
                font-size="16"
                pointer-events="none"
              >
                ⚡
              </text>
            </g>
          </g>
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  spots: { type: Array, required: true, default: () => [] },
  selectedId: { type: [String, Number], default: null },
  navigationPath: { type: Array, default: () => [] },
})

const emit = defineEmits(['select'])

const container = ref(null)
const svgRef = ref(null)
const transformGroup = ref(null)

const MAP_W = 1098
const MAP_H = 771
const SPOT_WIDTH = 46.6
const SPOT_HEIGHT = 78.4

const zoom = ref(1)
const offset = ref({ x: 0, y: 0 })
const selectedSpot = ref(null)
const svgDataUrl = ref(null)

const navigationPathPoints = computed(() => {
  if (!Array.isArray(props.navigationPath)) {
    return []
  }

  return props.navigationPath
    .map((point) => ({
      x: Number(point?.x),
      y: Number(point?.y),
    }))
    .filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y))
})

// 计算从车位边缘开始/结束的渲染路径，避免穿过车位中心。
function _normalize(vx, vy) {
  const len = Math.hypot(vx, vy) || 1
  return { x: vx / len, y: vy / len }
}

function computeNavigationPathData(pts) {
  if (!pts || pts.length < 2) return { d: '', start: null, end: null }

  const out = []
  const offsetDist = Math.max(SPOT_WIDTH, SPOT_HEIGHT) / 2 * 0.9

  let startAnchor = null
  let endAnchor = null

  for (let i = 1; i < pts.length; i++) {
    const prev = pts[i - 1]
    const curr = pts[i]
    const dx = curr.x - prev.x
    const dy = curr.y - prev.y
    const n = _normalize(dx, dy)

    // 从 prev 向外偏移，curr 向内偏移，保证不从车位中心直接穿过
    const segStart = { x: prev.x + n.x * offsetDist, y: prev.y + n.y * offsetDist }
    const segEnd = { x: curr.x - n.x * offsetDist, y: curr.y - n.y * offsetDist }

    if (i === 1) {
      startAnchor = segStart
      out.push(segStart)
    }

    // 使用 Manhattan 风格分段：横向/纵向折返，减少斜穿
    const midX = segStart.x + (segEnd.x - segStart.x) / 2
    out.push({ x: midX, y: segStart.y })
    out.push({ x: midX, y: segEnd.y })
    out.push(segEnd)

    if (i === pts.length - 1) {
      endAnchor = segEnd
    }
  }

  if (!startAnchor) startAnchor = pts[0]
  if (!endAnchor) endAnchor = pts[pts.length - 1]

  // 从 points 数组生成 SVG 路径 d
  let d = ''
  if (out.length > 0) {
    d = `M ${out[0].x} ${out[0].y}`
    for (let i = 1; i < out.length; i++) {
      d += ` L ${out[i].x} ${out[i].y}`
    }
  }

  return { d, start: startAnchor, end: endAnchor }
}

const navigationPathD = computed(() => {
  const pts = navigationPathPoints.value
  if (pts.length < 2) return ''
  return computeNavigationPathData(pts).d
})

const navigationAnchors = computed(() => {
  const pts = navigationPathPoints.value
  if (pts.length < 2) return { start: null, end: null }
  return computeNavigationPathData(pts)
})

onMounted(() => {
  loadSVGBackground()
})

async function loadSVGBackground() {
  try {
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8080'
    const response = await fetch(`${apiBase}/api/v1/parking/map/svg/`)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()

    if (data.code === 200 && data.data?.svg) {
      const blob = new Blob([data.data.svg], { type: 'image/svg+xml' })
      svgDataUrl.value = URL.createObjectURL(blob)
      console.log('✓ SVG 背景加载成功')
    } else {
      console.error('✗ SVG 加载失败:', data.error)
    }
  } catch (err) {
    console.error('✗ 加载 SVG 底图失败:', err)
  }
}

function getStatusColor(status) {
  const colors = {
    free: '#3b82f6',
    occupied: '#ef4444',
    reserved: '#f59e0b',
    maintenance: '#cbd5e1',
    overstay: '#e85d75',
  }
  return colors[status] || '#94a3b8'
}

function getSpotColor(spot) {
  if (spot?.marker_color) {
    return spot.marker_color
  }
  if (spot?.status === 'free' && spot?.spot_type === 'ev') {
    return '#22c55e'
  }
  if (spot?.status === 'free') {
    return '#3b82f6'
  }
  return getStatusColor(spot?.status)
}

function getSpotTransform(spot) {
  const x = Number(spot.floor_x || 0)
  const y = Number(spot.floor_y || 0)
  const rotation = Number(spot.rotation || 0)

  if (rotation === 90) {
    return `matrix(0,-1,1,0,${x},${y})`
  }

  return `translate(${x},${y})`
}

function getLabelTransform(spot) {
  const rotation = Number(spot.rotation || 0)
  if (rotation === 90) {
    const centerX = SPOT_WIDTH / 2
    const centerY = SPOT_HEIGHT / 2 + 2
    return `rotate(90 ${centerX} ${centerY})`
  }
  return null
}

function mapTransform() {
  return `translate(${offset.value.x}, ${offset.value.y}) scale(${zoom.value})`
}

function selectSpot(spot) {
  selectedSpot.value = spot
  emit('select', spot)
}

watch(() => props.selectedId, (newId) => {
  if (newId) {
    const spot = props.spots.find((s) => s.id === newId)
    if (spot) {
      selectedSpot.value = spot
    }
  } else {
    selectedSpot.value = null
  }
})
</script>

<style scoped>
.map-viewport {
  touch-action: none;
  overscroll-behavior: contain;
  -webkit-user-select: none;
  user-select: none;
}

svg {
  background: #fff;
}

.spot-group {
  transition: opacity 0.2s;
}

.spot-group:hover .parking-spot {
  opacity: 1 !important;
}

.parking-spot {
  stroke: #333;
}

.selected .parking-spot {
  stroke: #3b82f6;
  stroke-width: 2;
}

.navigation-path {
  animation: dash-flow 1.6s linear infinite;
}

.navigation-start,
.navigation-end {
  animation: pulse-node 1.8s ease-in-out infinite;
}

@keyframes dash-flow {
  to {
    stroke-dashoffset: -24;
  }
}

@keyframes pulse-node {
  0%,
  100% {
    transform: scale(1);
    transform-origin: center;
  }
  50% {
    transform: scale(1.12);
    transform-origin: center;
  }
}
</style>