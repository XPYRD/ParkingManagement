<template>
  <div class="diagnostic-container">
    <h1>🔧 停车场地图诊断工具</h1>
    
    <div class="section">
      <h2>1. 后端连接检查</h2>
      <button @click="checkBackendConnection">测试连接</button>
      <div v-if="diagnostics.backendStatus" :class="['status', diagnostics.backendStatus.success ? 'success' : 'error']">
        {{ diagnostics.backendStatus.message }}
      </div>
    </div>

    <div class="section">
      <h2>2. API 数据加载</h2>
      <div class="floor-buttons">
        <button v-for="floor in ['B2', 'B1', '1F']" :key="floor" @click="testFloorData(floor)">
          加载 {{ floor }}
        </button>
      </div>
      <div v-if="diagnostics.floorData" class="data-display">
        <p><strong>楼层:</strong> {{ diagnostics.floorData.floor }}</p>
        <p><strong>车位数:</strong> {{ diagnostics.floorData.count }}</p>
        <p><strong>示例数据:</strong></p>
        <pre>{{ JSON.stringify(diagnostics.floorData.sample, null, 2) }}</pre>
      </div>
    </div>

    <div class="section">
      <h2>3. SVG 地图测试</h2>
      <button @click="testSVGMap">加载 SVG</button>
      <div v-if="diagnostics.svgStatus" :class="['status', diagnostics.svgStatus.success ? 'success' : 'error']">
        {{ diagnostics.svgStatus.message }}
      </div>
    </div>

    <div class="section">
      <h2>4. 实时地图渲染</h2>
      <div class="map-preview" v-if="diagnostics.mapData">
        <svg viewBox="0 0 1098 771" style="border: 1px solid #ddd;">
          <!-- SVG 背景 -->
          <rect width="1098" height="771" fill="#f9f9f9"/>
          
          <!-- 停车位标记 -->
          <g v-for="space in diagnostics.mapData.spaces" :key="space.space_id">
            <circle 
              :cx="space.center_x" 
              :cy="space.center_y" 
              r="20" 
              :fill="space.status === 'occupied' ? '#ef4444' : '#10b981'"
              opacity="0.7"
              stroke="white"
              stroke-width="1"
            >
              <title>{{ space.space_id }}</title>
            </circle>
          </g>
        </svg>
        <p>共显示 {{ diagnostics.mapData.spaces.length }} 个停车位</p>
      </div>
      <button v-if="!diagnostics.mapData" @click="testMapRendering">测试地图渲染</button>
    </div>

    <div class="section">
      <h2>5. 浏览器信息</h2>
      <div class="browser-info">
        <p><strong>当前 URL:</strong> {{ currentUrl }}</p>
        <p><strong>API 基础 URL:</strong> /api/v1</p>
        <p><strong>CORS 来源:</strong> {{ window.location.origin }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const diagnostics = ref({
  backendStatus: null,
  floorData: null,
  svgStatus: null,
  mapData: null
})

const currentUrl = computed(() => window.location.href)

const checkBackendConnection = async () => {
  try {
    const response = await fetch('/api/v1/parking/map/spaces/?floor=B2')
    const data = await response.json()
    
    diagnostics.value.backendStatus = {
      success: response.ok && data.code === 200,
      message: response.ok 
        ? `✓ 连接成功 (${data.data.length} 个停车位)`
        : `✗ 错误: ${data.error || response.status}`
    }
  } catch (error) {
    diagnostics.value.backendStatus = {
      success: false,
      message: `✗ 连接失败: ${error.message}`
    }
  }
}

const testFloorData = async (floor) => {
  try {
    const response = await fetch(`/api/v1/parking/map/spaces/?floor=${floor}`)
    const data = await response.json()
    
    if (data.code === 200 && data.data.length > 0) {
      diagnostics.value.floorData = {
        floor: data.floor,
        count: data.data.length,
        sample: data.data[0]
      }
    }
  } catch (error) {
    console.error('加载失败:', error)
  }
}

const testSVGMap = async () => {
  try {
    const response = await fetch('/api/v1/parking/map/svg/')
    const data = await response.json()
    
    diagnostics.value.svgStatus = {
      success: data.code === 200 && data.data?.svg,
      message: data.code === 200 
        ? `✓ SVG 加载成功 (${data.data.svg.length} 字符)`
        : `✗ 加载失败`
    }
  } catch (error) {
    diagnostics.value.svgStatus = {
      success: false,
      message: `✗ 错误: ${error.message}`
    }
  }
}

const testMapRendering = async () => {
  try {
    const response = await fetch('/api/v1/parking/map/spaces/?floor=B2')
    const data = await response.json()
    
    if (data.code === 200) {
      diagnostics.value.mapData = {
        spaces: data.data
      }
    }
  } catch (error) {
    console.error('渲染失败:', error)
  }
}
</script>

<style scoped>
.diagnostic-container {
  max-width: 1000px;
  margin: 20px auto;
  padding: 20px;
  font-family: Arial, sans-serif;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

h1 {
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 10px;
}

.section {
  margin: 20px 0;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.section h2 {
  margin-top: 0;
  color: #667eea;
  font-size: 16px;
}

button {
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  margin: 5px 5px 5px 0;
}

button:hover {
  background: #764ba2;
}

.floor-buttons {
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
}

.status {
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
  font-weight: bold;
}

.status.success {
  background: #c8e6c9;
  color: #2e7d32;
  border: 1px solid #81c784;
}

.status.error {
  background: #ffcdd2;
  color: #c62828;
  border: 1px solid #ef5350;
}

.data-display {
  margin-top: 10px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

pre {
  background: #fff;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  max-height: 300px;
  border: 1px solid #ddd;
}

.map-preview {
  margin-top: 15px;
}

svg {
  width: 100%;
  max-width: 600px;
  height: auto;
}

.browser-info {
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
}

.browser-info p {
  margin: 5px 0;
  word-break: break-all;
}
</style>
