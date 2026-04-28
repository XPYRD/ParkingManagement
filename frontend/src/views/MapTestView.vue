<template>
  <div class="test-container">
    <h1>🧪 地图标记测试 - 硬编码数据</h1>
    
    <div class="status">
      <p><strong>SVG 已加载:</strong> {{ svgLoaded ? '✓' : '✗' }}</p>
      <p><strong>显示的标记数:</strong> {{ testSpaces.length }}</p>
    </div>

    <div class="map-wrapper">
      <svg viewBox="0 0 1098 771" class="test-map">
        <!-- 灰色背景 -->
        <rect width="1098" height="771" fill="#f5f5f5" stroke="#ddd" stroke-width="2"/>
        
        <!-- 硬编码的测试标记 -->
        <circle cx="223" cy="325" r="25" fill="#c8e6c9" stroke="white" stroke-width="2" opacity="0.8">
          <title>测试位置 1</title>
        </circle>
        
        <circle cx="274" cy="325" r="25" fill="#c8e6c9" stroke="white" stroke-width="2" opacity="0.8">
          <title>测试位置 2</title>
        </circle>
        
        <circle cx="325" cy="325" r="25" fill="#ffcdd2" stroke="white" stroke-width="2" opacity="0.8">
          <title>测试位置 3（占用）</title>
        </circle>
        
        <circle cx="376" cy="325" r="25" fill="#c8e6c9" stroke="white" stroke-width="2" opacity="0.8">
          <title>测试位置 4</title>
        </circle>
        
        <!-- 从 API 加载的实际数据 -->
        <g v-if="testSpaces.length > 0" class="actual-data">
          <circle 
            v-for="(space, idx) in testSpaces.slice(0, 20)" 
            :key="idx"
            :cx="space.center_x" 
            :cy="space.center_y" 
            r="20" 
            :fill="space.status === 'occupied' ? '#ef4444' : '#10b981'"
            stroke="white"
            stroke-width="2"
            opacity="0.7"
          >
            <title>{{ space.space_id }}</title>
          </circle>
        </g>
      </svg>
    </div>

    <div class="instructions">
      <p>✓ 如果能看到 4 个硬编码的圆形标记（绿色和红色），说明 SVG 和样式是正常的。</p>
      <p>✓ 如果还能看到额外的较小圆形标记，说明 API 数据也已正确加载。</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const svgLoaded = ref(false)
const testSpaces = ref([])

onMounted(async () => {
  // 标记 SVG 已加载
  svgLoaded.value = true
  
  // 尝试从 API 加载实际数据
  try {
    const response = await fetch('/api/v1/parking/map/spaces/?floor=B2')
    const data = await response.json()
    
    if (data.code === 200 && data.data) {
      testSpaces.value = data.data
      console.log(`✓ 成功加载 ${data.data.length} 个停车位`)
    }
  } catch (error) {
    console.error('✗ API 加载失败:', error)
  }
})
</script>

<style scoped>
.test-container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 10px;
}

.status {
  padding: 15px;
  background: #e3f2fd;
  border-radius: 4px;
  margin: 15px 0;
}

.status p {
  margin: 5px 0;
  color: #1565c0;
}

.map-wrapper {
  border: 3px solid #667eea;
  padding: 10px;
  background: white;
  margin: 20px 0;
  overflow: auto;
  max-height: 600px;
}

.test-map {
  width: 100%;
  height: auto;
  display: block;
  background: white;
}

.instructions {
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  padding: 15px;
  margin-top: 20px;
  color: #856404;
}

.instructions p {
  margin: 5px 0;
}
</style>
