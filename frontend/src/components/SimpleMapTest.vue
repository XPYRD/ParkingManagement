<template>
  <div class="simple-map-wrapper">
    <h2>停车场地图 - 简化测试版</h2>
    
    <div class="controls">
      <button v-for="floor in floors" :key="floor" @click="currentFloor = floor">
        {{ floor }}
      </button>
      <span class="status">
        状态: {{ loading ? '⏳ 加载中' : (spaces.length > 0 ? `✓ 已加载 ${spaces.length} 个` : '✗ 未加载') }}
      </span>
    </div>

    <div class="map-area">
      <svg viewBox="0 0 1098 771" preserveAspectRatio="xMidYMid meet">
        <!-- 背景 -->
        <rect width="1098" height="771" fill="#f9f9f9" stroke="#ddd" stroke-width="1"/>
        
        <!-- 调试信息 -->
        <text x="50" y="50" font-size="16" fill="#666">
          {{ spaces.length > 0 ? `显示 ${spaces.length} 个停车位` : '无数据' }}
        </text>
        
        <!-- 停车位标记 -->
        <circle 
          v-for="space in spaces" 
          :key="space.space_id"
          :cx="space.center_x"
          :cy="space.center_y"
          r="23"
          :fill="space.status === 'occupied' ? '#ef4444' : '#10b981'"
          stroke="white"
          stroke-width="2"
          opacity="0.8"
          style="cursor: pointer;"
          @click="selectSpace(space)"
        >
          <title>{{ space.space_id }}: {{ space.status }}</title>
        </circle>

        <!-- 选中的标记高亮 -->
        <circle 
          v-if="selectedSpace"
          :cx="selectedSpace.center_x"
          :cy="selectedSpace.center_y"
          r="30"
          fill="none"
          stroke="#0066cc"
          stroke-width="3"
        />
      </svg>
    </div>

    <div v-if="selectedSpace" class="info-panel">
      <p><strong>车位 ID:</strong> {{ selectedSpace.space_id }}</p>
      <p><strong>坐标:</strong> ({{ selectedSpace.center_x }}, {{ selectedSpace.center_y }})</p>
      <p><strong>状态:</strong> {{ selectedSpace.status }}</p>
      <button @click="selectedSpace = null">关闭</button>
    </div>

    <div class="debug-info">
      <p><strong>当前楼层:</strong> {{ currentFloor }}</p>
      <p><strong>数据数量:</strong> {{ spaces.length }}</p>
      <p><strong>加载状态:</strong> {{ loading ? '加载中' : '就绪' }}</p>
      <p v-if="error" style="color: red;"><strong>错误:</strong> {{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const floors = ref(['B2', 'B1', '1F'])
const currentFloor = ref('B2')
const spaces = ref([])
const loading = ref(false)
const error = ref(null)
const selectedSpace = ref(null)

const loadSpaces = async (floor) => {
  loading.value = true
  error.value = null
  
  try {
    console.log(`[loadSpaces] Loading ${floor}...`)
    const response = await fetch(`/api/v1/parking/map/spaces/?floor=${floor}`)
    const data = await response.json()
    
    console.log(`[loadSpaces] Response:`, data)
    
    if (data.code === 200 && Array.isArray(data.data)) {
      spaces.value = data.data
      console.log(`[loadSpaces] Loaded ${data.data.length} spaces`)
      
      // 打印前3个坐标
      if (data.data.length > 0) {
        console.log('[loadSpaces] First 3 spaces:')
        data.data.slice(0, 3).forEach(s => {
          console.log(`  ${s.space_id}: center=(${s.center_x}, ${s.center_y})`)
        })
      }
    } else {
      error.value = `Invalid response: ${data.error || 'unknown'}`
      spaces.value = []
    }
  } catch (err) {
    error.value = err.message
    spaces.value = []
    console.error('[loadSpaces] Error:', err)
  } finally {
    loading.value = false
  }
}

const selectSpace = (space) => {
  selectedSpace.value = selectedSpace.value?.space_id === space.space_id ? null : space
}

// 监听楼层变化
watch(currentFloor, (newFloor) => {
  loadSpaces(newFloor)
}, { immediate: true })
</script>

<style scoped>
.simple-map-wrapper {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h2 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 10px;
}

.controls {
  display: flex;
  gap: 8px;
  margin: 15px 0;
  align-items: center;
}

button {
  padding: 10px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

button:hover {
  background: #764ba2;
}

.status {
  margin-left: 20px;
  font-weight: bold;
  color: #666;
}

.map-area {
  border: 3px solid #667eea;
  padding: 10px;
  background: white;
  margin: 20px 0;
  border-radius: 4px;
  overflow: auto;
  max-height: 700px;
}

svg {
  width: 100%;
  height: auto;
  display: block;
  background: white;
}

.info-panel {
  background: #e3f2fd;
  border: 1px solid #2196f3;
  padding: 15px;
  border-radius: 4px;
  margin: 15px 0;
}

.info-panel button {
  margin-top: 10px;
}

.debug-info {
  background: #f5f5f5;
  border: 1px solid #ddd;
  padding: 10px;
  border-radius: 4px;
  font-size: 12px;
  font-family: monospace;
  margin-top: 15px;
}

.debug-info p {
  margin: 4px 0;
}
</style>
