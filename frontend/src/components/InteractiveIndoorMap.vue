<template>
  <div class="interactive-indoor-map">
  <!-- 标题栏 -->
  <div class="map-header">
    <h2>室内停车场地图</h2>
    <p class="subtitle">需求文档 Section 3.1 - 室内交互地图模块</p>
  </div>

    <!-- SVG 地图容器 - 内联 SVG（需求文档 Section 3.2）-->
    <div class="map-container">
      <svg
        class="parking-map"
        height="771"
        viewBox="0 0 1098 771"
        width="1098"
        xmlns="http://www.w3.org/2000/svg"
        xmlns:xlink="http://www.w3.org/1999/xlink"
      >
        <!-- 背景 -->
        <rect width="1098" height="771" fill="#ffffff" />
        
        <!-- 以下内容来自 backend/svg/interactive_map.svg -->
        <!-- 内联 SVG 内容已直接嵌入组件中 -->
        <defs />
        <g transform="translate(-26.88,1.00)">
          <g id="group1" transform="matrix(0.000000,1.000000,-1.000000,0.000000,1072.980000,65.323000)">
            <path d="M.0,.0L8.0,.0L8.0,27.6L.0,27.6L.0,.0z" fill="#ffffff" fill-rule="nonzero" id="shape2" stroke="#000000" stroke-width="1" transform="translate(18.375070,33.394100)"/>
            <path d="M.0,.0L8.0,.0L8.0,27.6L.0,27.6L.0,.0z" fill="#ffffff" fill-rule="nonzero" id="shape3" stroke="#000000" stroke-width="1" transform="translate(26.121670,33.330700)"/>
            <path d="M.0,.0L8.0,.0L8.0,27.6L.0,27.6L.0,.0z" fill="#ffffff" fill-rule="nonzero" id="shape4" stroke="#000000" stroke-width="1" transform="translate(33.940170,33.330700)"/>
            <path d="M.0,.0L8.0,.0L8.0,27.6L.0,27.6L.0,.0z" fill="#ffffff" fill-rule="nonzero" id="shape5" stroke="#000000" stroke-width="1" transform="translate(41.759370,33.330700)"/>
            <path d="M.0,.0L8.0,.0L8.0,27.6L.0,27.6L.0,.0z" fill="#ffffff" fill-rule="nonzero" id="shape6" stroke="#000000" stroke-width="1" transform="translate(49.578770,33.330700)"/>
            <path d="M.0,.0L8.0,.0L8.0,27.6L.0,27.6L.0,.0z" fill="#ffffff" fill-rule="nonzero" id="shape7" stroke="#000000" stroke-width="1" transform="translate(57.396970,33.330700)"/>
            <path d="M.0,.0L8.0,.0L8.0,27.6L.0,27.6L.0,.0z" fill="#ffffff" fill-rule="nonzero" id="shape8" stroke="#000000" stroke-width="1" transform="translate(65.216270,33.330700)"/>
          </g>
          <g id="group22" transform="translate(43.000000,44.299000)">
            <g id="shape23" transform="matrix(1.000000,-0.000000,0.000000,1.000000,0.000000,0.000029)">
              <path d="M.0,.0L1037.0,.0L1052.1,-15.1L-15.1,-15.1L.0,.0z" fill="#808080" fill-rule="nonzero"/>
              <path d="M.0,.0L1037.0,.0M1052.1,-15.1L-15.1,-15.1" fill="none" stroke="#808080" stroke-width="1"/>
            </g>
          </g>
        </g>

        <!-- 65 个停车位元素 -->
        <!-- 需求文档 Section 3.2：SVG 中的车位节点具备固定格式 <path class="parking-space" id="space_A001" /> -->
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A001" stroke="#7e7e7e" stroke-width="1" transform="translate(199.863500,286.577500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A002" stroke="#7e7e7e" stroke-width="1" transform="translate(199.863500,369.178500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A003" stroke="#7e7e7e" stroke-width="1" transform="translate(251.062500,286.577500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A004" stroke="#7e7e7e" stroke-width="1" transform="translate(251.062500,369.178500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A005" stroke="#7e7e7e" stroke-width="1" transform="translate(302.262500,286.577500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A006" stroke="#7e7e7e" stroke-width="1" transform="translate(302.262500,369.178500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A007" stroke="#7e7e7e" stroke-width="1" transform="translate(353.461500,286.577500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A008" stroke="#7e7e7e" stroke-width="1" transform="translate(353.461500,369.178500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A009" stroke="#7e7e7e" stroke-width="1" transform="translate(404.660500,286.577500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A010" stroke="#7e7e7e" stroke-width="1" transform="translate(404.660500,369.178500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A011" stroke="#7e7e7e" stroke-width="1" transform="translate(455.859500,286.577500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A012" stroke="#7e7e7e" stroke-width="1" transform="translate(455.859500,369.347500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A013" stroke="#7e7e7e" stroke-width="1" transform="translate(199.866500,543.421500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A014" stroke="#7e7e7e" stroke-width="1" transform="translate(251.066500,543.421500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A015" stroke="#7e7e7e" stroke-width="1" transform="translate(302.266500,543.421500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A016" stroke="#7e7e7e" stroke-width="1" transform="translate(353.466500,543.421500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A017" stroke="#7e7e7e" stroke-width="1" transform="translate(404.666500,543.421500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A018" stroke="#7e7e7e" stroke-width="1" transform="translate(455.856500,543.590500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A019" stroke="#7e7e7e" stroke-width="1" transform="translate(516.975500,286.662500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A020" stroke="#7e7e7e" stroke-width="1" transform="translate(516.975500,369.263500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A021" stroke="#7e7e7e" stroke-width="1" transform="translate(568.175500,286.662500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A022" stroke="#7e7e7e" stroke-width="1" transform="translate(568.175500,369.263500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A023" stroke="#7e7e7e" stroke-width="1" transform="translate(619.375500,286.662500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A024" stroke="#7e7e7e" stroke-width="1" transform="translate(619.375500,369.263500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A025" stroke="#7e7e7e" stroke-width="1" transform="translate(670.575500,286.662500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A026" stroke="#7e7e7e" stroke-width="1" transform="translate(670.575500,369.263500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A027" stroke="#7e7e7e" stroke-width="1" transform="translate(721.775500,286.662500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A028" stroke="#7e7e7e" stroke-width="1" transform="translate(721.775500,369.263500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A029" stroke="#7e7e7e" stroke-width="1" transform="translate(772.965500,286.662500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A030" stroke="#7e7e7e" stroke-width="1" transform="translate(772.965500,369.432500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A031" stroke="#7e7e7e" stroke-width="1" transform="translate(241.483500,46.299200)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A032" stroke="#7e7e7e" stroke-width="1" transform="translate(292.683500,46.299200)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A033" stroke="#7e7e7e" stroke-width="1" transform="translate(343.883500,46.299200)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A034" stroke="#7e7e7e" stroke-width="1" transform="translate(395.083500,46.299200)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A035" stroke="#7e7e7e" stroke-width="1" transform="translate(446.283500,46.299200)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A036" stroke="#7e7e7e" stroke-width="1" transform="translate(497.473500,46.299200)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A037" stroke="#7e7e7e" stroke-width="1" transform="matrix(0.000000,-1.000000,1.000000,0.000000,996.595500,311.195500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A038" stroke="#7e7e7e" stroke-width="1" transform="matrix(0.000000,-1.000000,1.000000,0.000000,996.595500,259.995500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A039" stroke="#7e7e7e" stroke-width="1" transform="matrix(0.000000,-1.000000,1.000000,0.000000,996.595500,208.805500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A040" stroke="#7e7e7e" stroke-width="1" transform="matrix(0.000000,-1.000000,1.000000,0.000000,996.595500,475.815500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A041" stroke="#7e7e7e" stroke-width="1" transform="matrix(0.000000,-1.000000,1.000000,0.000000,996.595500,424.615500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A042" stroke="#7e7e7e" stroke-width="1" transform="matrix(0.000000,-1.000000,1.000000,0.000000,996.595500,373.425500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A043" stroke="#7e7e7e" stroke-width="1" transform="matrix(0.000000,-1.000000,1.000000,0.000000,996.595500,640.000500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A044" stroke="#7e7e7e" stroke-width="1" transform="matrix(0.000000,-1.000000,1.000000,0.000000,996.595500,588.800500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A045" stroke="#7e7e7e" stroke-width="1" transform="matrix(0.000000,-1.000000,1.000000,0.000000,996.595500,537.610500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A046" stroke="#7e7e7e" stroke-width="1" transform="matrix(0.000000,-1.000000,1.000000,0.000000,996.595500,752.350500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A047" stroke="#7e7e7e" stroke-width="1" transform="matrix(0.000000,-1.000000,1.000000,0.000000,996.595500,701.150500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A048" stroke="#7e7e7e" stroke-width="1" transform="translate(516.975500,543.772500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A049" stroke="#7e7e7e" stroke-width="1" transform="translate(568.175500,543.772500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A050" stroke="#7e7e7e" stroke-width="1" transform="translate(619.375500,543.772500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A051" stroke="#7e7e7e" stroke-width="1" transform="translate(670.575500,543.772500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A052" stroke="#7e7e7e" stroke-width="1" transform="translate(721.775500,543.772500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A053" stroke="#7e7e7e" stroke-width="1" transform="translate(772.965500,543.941500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A054" stroke="#7e7e7e" stroke-width="1" transform="translate(199.864500,624.976500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A055" stroke="#7e7e7e" stroke-width="1" transform="translate(251.064500,624.976500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A056" stroke="#7e7e7e" stroke-width="1" transform="translate(302.264500,624.976500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A057" stroke="#7e7e7e" stroke-width="1" transform="translate(353.464500,624.976500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A058" stroke="#7e7e7e" stroke-width="1" transform="translate(404.664500,624.976500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A059" stroke="#7e7e7e" stroke-width="1" transform="translate(455.854500,625.145500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A060" stroke="#7e7e7e" stroke-width="1" transform="translate(516.974500,625.061500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A061" stroke="#7e7e7e" stroke-width="1" transform="translate(568.174500,625.061500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A062" stroke="#7e7e7e" stroke-width="1" transform="translate(619.374500,625.061500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A063" stroke="#7e7e7e" stroke-width="1" transform="translate(670.574500,625.061500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A064" stroke="#7e7e7e" stroke-width="1" transform="translate(721.774500,625.061500)"/>
        <path class="parking-space" d="M.0,.0L46.6,.0L46.6,78.4L.0,78.4L.0,.0z" fill="#ffffff" id="space_A065" stroke="#7e7e7e" stroke-width="1" transform="translate(772.964500,625.230500)"/>
      </svg>
    </div>

    <!-- 底部信息卡片 -->
    <div v-if="selectedSpace" class="info-card-bottom">
      <div class="card-header">
        <h3>车位信息</h3>
        <button @click="selectedSpace = null" class="close-btn">✕</button>
      </div>
      <div class="card-body">
        <div class="info-row">
          <span class="label">车位号：</span>
          <span class="value">{{ selectedSpace.space_id }}</span>
        </div>
        <div class="info-row">
          <span class="label">状态：</span>
          <span :class="['value', getStatusClass(selectedSpace.status)]">
            {{ getStatusLabel(selectedSpace.status) }}
          </span>
        </div>
        <div v-if="selectedSpace.current_plate" class="info-row">
          <span class="label">车牌号：</span>
          <span class="value">{{ selectedSpace.current_plate }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

/**
 * 响应式状态字典 - 需求文档 Section 3.2 (数据绑定)
 * 格式：spaceStatus: { 'space_A001': 'occupied', 'space_A002': 'free', ... }
 */
const spaceStatus = ref({})
const selectedSpace = ref(null)

onMounted(async () => {
  await loadMapData()
  attachSpaceClickHandlers()
})

/**
 * 加载地图数据 - 调用后端 API
 * GET /api/v1/map/spaces/ (需求文档 Section 3.3)
 * 
 * 返回格式：
 * {
 *   "code": 200,
 *   "data": [
 *     {"space_id": "space_A001", "status": "occupied"},
 *     {"space_id": "space_A002", "status": "free"}
 *   ]
 * }
 */
async function loadMapData() {
  try {
    const response = await axios.get('/api/v1/map/spaces/')
    
    if (response.data.code === 200) {
      // 构建响应式状态字典 - 需求文档 Section 3.2
      response.data.data.forEach(space => {
        spaceStatus.value[space.space_id] = space.status
        
        // 立即更新 SVG 元素的填充色 - 动态数据绑定
        updateSpaceColor(space.space_id, space.status)
      })
    }
  } catch (error) {
    console.error('加载地图数据失败:', error)
  }
}

/**
 * 根据状态值更新 SVG 元素的填充色
 * 需求文档 Section 3.2 (状态渲染)
 * 
 * 颜色映射标准：
 * - 'free' 空闲：fill="#e0f7fa"
 * - 'occupied' 占用：fill="#ffebee"
 * - 'reserved' 已预约：fill="#fff7e6"
 * - 'maintenance' 维修中：fill="#f3f4f6"
 */
function updateSpaceColor(spaceId, status) {
  const element = document.getElementById(spaceId)
  if (!element) return
  
  // 颜色映射 - 来自需求文档 Section 3.2
  const colors = {
    'free': '#e0f7fa',        // 浅绿色 - 空闲
    'occupied': '#ffebee',    // 浅红色 - 占用
    'reserved': '#fff7e6',    // 浅橙色 - 已预约
    'maintenance': '#f3f4f6', // 浅灰色 - 维修中
  }
  
  const fillColor = colors[status] || '#ffffff'
  element.setAttribute('fill', fillColor)
}

/**
 * 为所有停车位元素附加点击事件处理
 * 需求文档 Section 3.2 (交互事件)
 */
function attachSpaceClickHandlers() {
  const spaceElements = document.querySelectorAll('.parking-space')
  
  spaceElements.forEach(element => {
    const spaceId = element.getAttribute('id')
    element.style.cursor = 'pointer'
    element.addEventListener('click', () => onClickSpace(spaceId))
  })
}

/**
 * 点击停车位时的处理函数
 * 需求文档 Section 3.2 (交互事件：触发 onClickSpace(space_id)，弹出信息卡片)
 */
function onClickSpace(spaceId) {
  // 查找该停车位的状态信息
  const status = spaceStatus.value[spaceId]
  
  if (!status) {
    console.warn(`未找到车位 ${spaceId} 的状态信息`)
    return
  }
  
  // 构建选中的车位对象
  selectedSpace.value = {
    space_id: spaceId,
    status: status,
    current_plate: null  // TODO: 从 API 获取车牌号
  }
}

/**
 * 获取状态标签 - 需求文档标准
 */
function getStatusLabel(status) {
  const labels = {
    'free': '空闲',
    'occupied': '占用',
    'reserved': '已预约',
    'maintenance': '维修中',
  }
  return labels[status] || '未知'
}

/**
 * 获取状态样式类
 */
function getStatusClass(status) {
  if (status === 'free') return 'status-free'
  if (status === 'occupied') return 'status-occupied'
  if (status === 'reserved') return 'status-reserved'
  if (status === 'maintenance') return 'status-maintenance'
  return 'status-occupied'
}
</script>

<style scoped>
.interactive-indoor-map {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f5f5;
}

.map-header {
  padding: 20px 24px;
  background-color: white;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.map-header h2 {
  margin: 0 0 4px 0;
  font-size: 24px;
  color: #333;
}

.subtitle {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.map-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: auto;
  padding: 20px;
}

.parking-map {
  width: 100%;
  height: 100%;
  max-width: 1098px;
  max-height: 771px;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 停车位样式 */
.parking-space {
  cursor: pointer;
  transition: fill 0.3s ease, stroke 0.3s ease;
  stroke: #7e7e7e;
  stroke-width: 1;
}

.parking-space:hover {
  stroke: #3b82f6;
  stroke-width: 2;
  filter: brightness(0.95);
}

/* 底部信息卡片 */
.info-card-bottom {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 500px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideUp 0.3s ease-out;
  z-index: 100;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f9f9f9;
  border-radius: 8px 8px 0 0;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background-color: transparent;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #f0f0f0;
  color: #333;
}

.card-body {
  padding: 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.label {
  color: #666;
  font-weight: 500;
  min-width: 80px;
}

.value {
  color: #333;
  font-weight: 600;
}

.value.status-free {
  color: #10b981;
}

.value.status-occupied {
  color: #ef4444;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}
</style>
