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

          <g class="public-locations-layer">
            <g
              v-for="loc in publicLocations"
              :key="'pub-'+loc.id"
              @click="() => emit('select-public', loc)"
              class="location-group"
              :class="{ selected: loc.id === selectedId }"
              :transform="`translate(${Number(loc.center_x || loc.x || 0)}, ${Number(loc.center_y || loc.y || 0)})`"
            >
              <rect
                x="-16" y="-16" width="32" height="32"
                rx="6"
                :fill="loc.id === selectedId ? '#3b82f6' : '#6366f1'"
                :stroke="loc.id === selectedId ? '#1d4ed8' : '#4f46e5'"
                stroke-width="2"
                opacity="0.85"
                class="location-marker"
              />
              <text
                x="0" y="1"
                text-anchor="middle"
                dominant-baseline="middle"
                font-size="16"
                pointer-events="none"
              >{{ locationEmoji(loc) }}</text>
              <text
                x="0" y="24"
                text-anchor="middle"
                font-size="9"
                font-weight="600"
                fill="#475569"
                pointer-events="none"
              >{{ loc.name }}</text>
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
  publicLocations: { type: Array, default: () => [] },
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

function buildPathD(pts) {
  if (!pts || pts.length < 2) return ''
  let d = `M ${pts[0].x} ${pts[0].y}`
  for (let i = 1; i < pts.length; i++) {
    d += ` L ${pts[i].x} ${pts[i].y}`
  }
  return d
}

const navigationPathD = computed(() => buildPathD(navigationPathPoints.value))

function locationEmoji(loc) {
  const name = loc.name || ''
  if (name.includes('电梯')) return '\u{2B06}'
  if (name.includes('出口')) return '\u{1F6AA}'
  if (name.includes('入口')) return '\u{1F6AA}'
  if (name.includes('楼梯')) return '\u{1F6B6}'
  if (name.includes('服务')) return '\u{1F481}'
  return '\u{1F4CD}'
}

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

@keyframes dash-flow {
  to {
    stroke-dashoffset: -24;
  }
}

.location-group {
  cursor: pointer;
}

.location-marker {
  transition: opacity 0.2s;
}

.location-group:hover .location-marker {
  opacity: 1 !important;
}
</style>