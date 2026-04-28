<template>
  <div class="w-full h-full bg-white overflow-auto relative flex flex-col">
    <!-- 楼层切换条 -->
    <div class="bg-gray-100 border-b border-gray-200 px-4 py-3 flex items-center gap-2">
      <span class="text-sm font-medium text-gray-700">楼层：</span>
      <div class="flex gap-2">
        <button
          v-for="floor in floors"
          :key="floor"
          @click="selectedFloor = floor"
          :class="[
            'px-3 py-1 rounded text-sm font-medium transition-colors',
            selectedFloor === floor
              ? 'bg-blue-500 text-white'
              : 'bg-white border border-gray-300 text-gray-700 hover:border-gray-400'
          ]"
        >
          {{ floor }}
        </button>
      </div>
      <span class="ml-auto text-xs text-gray-500">
        共 {{ filteredSpots.length }} 个停车位（已占用: {{ occupiedCount }}, 空闲: {{ freeCount }}）
      </span>
    </div>

    <!-- SVG 地图容器 -->
    <div class="flex-1 overflow-auto relative">
      <svg
        v-if="svgContent"
        :viewBox="`0 0 ${svgViewBox.width} ${svgViewBox.height}`"
        class="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
        @click="handleSvgClick"
      >
        <!-- 加载 SVG 内容 -->
        <g v-html="svgContent"></g>

        <!-- 停车位覆盖层 -->
        <g class="parking-spots-layer">
          <rect
            v-for="spot in filteredSpots"
            :key="spot.id"
            :x="getSpotX(spot)"
            :y="getSpotY(spot)"
            :width="getSpotWidth(spot)"
            :height="getSpotHeight(spot)"
            :class="`spot-marker status-${getStatus(spot)}`"
            :data-spot-id="spot.id"
            @click.stop="selectSpot(spot)"
            @mouseover="hoveredSpot = spot.id"
            @mouseout="hoveredSpot = null"
            style="cursor: pointer;"
          >
            <title>{{ spot.floor }}_{{ spot.spot_id || spot.space_id || spot.id }} - {{ getStatusLabel(getStatus(spot)) }}</title>
          </rect>

          <!-- 悬停标签 -->
          <g v-if="hoveredSpot">
            <text
              v-for="spot in filteredSpots.filter(s => s.id === hoveredSpot)"
              :key="`label-${spot.id}`"
              :x="getSpotCx(spot)"
              :y="getSpotY(spot) - 10"
              class="spot-label"
              text-anchor="middle"
              pointer-events="none"
            >
              {{ spot.spot_id || spot.space_id || spot.id }} - {{ getStatusLabel(getStatus(spot)) }}
            </text>
          </g>

          <!-- 选中突出显示 -->
          <rect
            v-if="selectedSpot"
            :x="getSpotX(selectedSpot)"
            :y="getSpotY(selectedSpot)"
            :width="getSpotWidth(selectedSpot)"
            :height="getSpotHeight(selectedSpot)"
            class="spot-selected"
            pointer-events="none"
          />
        </g>
      </svg>

      <!-- 加载指示器 -->
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-black/10 z-20">
        <div class="bg-white rounded-lg p-6 shadow-lg text-center">
          <div class="spinner mb-3"></div>
          <p class="text-sm text-gray-600">加载地图中...</p>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="absolute inset-0 flex items-center justify-center bg-black/10 z-20">
        <div class="bg-white rounded-lg p-6 shadow-lg text-center max-w-xs">
          <p class="text-sm text-red-600 mb-3">{{ error }}</p>
          <button
            @click="loadSvg"
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            重试
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'

const props = defineProps({
  spots: { type: Array, required: true },
  selectedId: { type: [String, Number], default: null },
  currentFloor: { type: String, default: 'B2' }  // ✅ 从父组件接收当前楼层
})

const emit = defineEmits(['select'])

const svgContent = ref('')
const loading = ref(true)
const error = ref(null)
const hoveredSpot = ref(null)
const selectedSpot = ref(null)
const svgViewBox = ref({ width: 1098, height: 771 })
const floors = ref(['B2', 'B1', '1F'])
const selectedFloor = ref('B2')

// ✅ 当父组件传入的 currentFloor 变化时，同步更新 selectedFloor
watch(() => props.currentFloor, (newFloor) => {
  selectedFloor.value = newFloor
}, { immediate: true })

// 根据选中的楼层过滤停车位
const filteredSpots = computed(() => {
  if (!props.spots) return []
  return props.spots.filter(spot => spot.floor === selectedFloor.value)
})

// 计算已占用和空闲数量
const occupiedCount = computed(() => {
  return filteredSpots.value.filter(s => s.status === 'occupied').length
})

const freeCount = computed(() => {
  return filteredSpots.value.filter(s => s.status === 'free').length
})

const getStatus = (spot) => {
  return spot.status || 'free'
}

const getStatusLabel = (status) => {
  const labels = {
    free: '空闲',
    occupied: '已占用',
    reserved: '已预约',
    maintenance: '维修中'
  }
  return labels[status] || '未知'
}

// 坐标转换函数 - 矩形标记的左上角坐标
// 停车位尺寸：46.6 × 78.4
// 使用数据库中的 x, y 字段（SVG translate 左上角坐标）
let debugLogged = false
const getSpotX = (spot) => {
  if (!spot) return 200
  // 优先使用 x 字段（SVG 坐标系左上角）
  if (spot.x !== undefined && spot.x !== null) {
    if (!debugLogged && typeof spot.x === 'number') {
      console.log('getSpotX: using x field', spot.space_id, 'x=', spot.x)
      debugLogged = true
    }
    return parseFloat(spot.x)
  }
  // 备用：从 center_x 推算
  if (spot.center_x !== undefined && spot.center_x !== null) {
    const calcX = parseFloat(spot.center_x) - 23.3
    if (!debugLogged) {
      console.log('getSpotX: calculated from center_x', spot.space_id, spot.center_x, '->', calcX)
      debugLogged = true
    }
    return calcX
  }
  console.warn('getSpotX: No valid coordinates for', spot.space_id)
  return 200
}

const getSpotY = (spot) => {
  if (!spot) return 200
  // 优先使用 y 字段（SVG 坐标系左上角）
  if (spot.y !== undefined && spot.y !== null) {
    return parseFloat(spot.y)
  }
  // 备用：从 center_y 推算
  if (spot.center_y !== undefined && spot.center_y !== null) {
    return parseFloat(spot.center_y) - 39.2
  }
  console.warn('getSpotY: No valid coordinates for', spot.space_id)
  return 200
}

// 中心坐标（用于标签定位）
const getSpotCx = (spot) => {
  if (!spot) return 200
  if (spot.center_x !== undefined) return spot.center_x
  // 备用：从 x 推算
  if (spot.x !== undefined) return spot.x + 23.3
  if (spot.floor_x !== undefined) {
    return (spot.floor_x - 5) / 85 * 900 + 100
  }
  return 200
}

const getSpotCy = (spot) => {
  if (!spot) return 200
  if (spot.center_y !== undefined) return spot.center_y
  // 备用：从 y 推算
  if (spot.y !== undefined) return spot.y + 39.2
  if (spot.floor_y !== undefined) {
    return (spot.floor_y - 5) / 70 * 650 + 50
  }
  return 200
}

// ✨ 新增：根据旋转角度获取停车位的正确宽度
const getSpotWidth = (spot) => {
  const rotation = spot?.rotation || 0
  // 90° 旋转时交换宽度和高度
  return rotation === 90 ? 78.4 : 46.6
}

// ✨ 新增：根据旋转角度获取停车位的正确高度
const getSpotHeight = (spot) => {
  const rotation = spot?.rotation || 0
  // 90° 旋转时交换宽度和高度
  return rotation === 90 ? 46.6 : 78.4
}

const selectSpot = (spot) => {
  selectedSpot.value = spot
  emit('select', spot)
}

const loadSvg = async () => {
  loading.value = true
  error.value = null
  try {
    // 从后端 API 加载 SVG
    const response = await fetch('/api/v1/parking/map/svg/')
    const result = await response.json()

    if (result.code === 200 && result.data?.svg) {
      svgContent.value = result.data.svg
      svgViewBox.value = {
        width: result.data.width || 1098,
        height: result.data.height || 771
      }
      console.log('SVG loaded successfully')
    } else {
      error.value = '加载 SVG 失败: ' + (result.error || '未知错误')
    }
  } catch (err) {
    error.value = '加载 SVG 失败: ' + err.message
    console.error('Error loading SVG:', err)
  } finally {
    loading.value = false
  }
}

const handleSvgClick = (e) => {
  if (e.target.classList?.contains('spot-marker')) {
    return
  }
}

onMounted(() => {
  console.log('ParkingMapSVG mounted')
  console.log('Props.spots:', props.spots.length, 'items')
  if (props.spots.length > 0) {
    console.log('First spot:', props.spots[0])
  }
  loadSvg()
})
</script>

<style scoped>
.spot-marker {
  opacity: 0.65;
  stroke: white;
  stroke-width: 1.5;
  transition: all 0.2s;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1));
}

.spot-marker:hover {
  opacity: 0.85;
  stroke-width: 2;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.3));
}

.spot-marker.status-free {
  fill: #10b981;
}

.spot-marker.status-occupied {
  fill: #ef4444;
}

.spot-marker.status-reserved {
  fill: #3b82f6;
}

.spot-marker.status-maintenance {
  fill: #9ca3af;
}

.spot-label {
  font-size: 12px;
  font-weight: bold;
  fill: #1f2937;
  text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.9);
  padding: 2px 6px;
  border-radius: 2px;
  pointer-events: none;
}

.spot-selected {
  fill: none;
  stroke: #fbbf24;
  stroke-width: 2.5;
  opacity: 0.9;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    stroke-width: 2;
    opacity: 0.9;
  }
  50% {
    stroke-width: 3;
    opacity: 1;
  }
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
