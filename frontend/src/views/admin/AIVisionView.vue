<template>
  <div class="p-6 lg:p-10 space-y-8 bg-surface-container-low min-h-screen">
    <!-- 顶部标题 -->
    <header class="flex flex-col md:flex-row justify-between items-start md:items-center">
      <div>
        <h1 class="text-3xl font-extrabold text-primary tracking-tight font-headline flex items-center gap-3">
          <span class="material-symbols-outlined text-4xl">neurology</span>
          AI 视觉感知中心
        </h1>
        <p class="text-secondary text-sm mt-1">基于 YOLOv8x 的实时车辆检测与车牌识别模拟系统</p>
      </div>
      <div class="mt-4 md:mt-0 flex gap-3">
        <el-tag type="success" effect="dark" class="!rounded-full px-4">模型状态: YOLOv8x 已就绪</el-tag>
        <el-tag type="info" effect="dark" class="!rounded-full px-4">OCR: EasyOCR 轻量版</el-tag>
      </div>
    </header>

    <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
      <!-- 左侧：识别工作区 -->
      <div class="xl:col-span-2 space-y-6">
        <div class="rounded-3xl bg-surface-container-lowest border border-outline-variant/20 shadow-xl overflow-hidden relative">
          <!-- 模拟监控边框装饰 -->
          <div class="absolute top-4 left-4 z-10 flex items-center gap-2 group">
            <div class="w-3 h-3 rounded-full bg-error animate-pulse"></div>
            <span class="text-[10px] font-bold text-error tracking-tighter uppercase">Live Analysis</span>
          </div>

          <!-- 上传/显示区域 -->
          <div 
            class="aspect-video w-full bg-black flex items-center justify-center relative group cursor-pointer"
            @dragover.prevent
            @drop.prevent="handleDrop"
            @click="triggerUpload"
          >
            <input type="file" ref="fileInput" class="hidden" :multiple="isBatchMode" accept="image/*" @change="handleFileChange" />
            
            <img v-if="previewUrl" :src="previewUrl" ref="sourceImg" class="max-w-full max-h-full object-contain opacity-80" @load="drawResults" />
            
            <canvas id="recognitionCanvas" class="absolute inset-0 pointer-events-none w-full h-full"></canvas>

            <div v-if="!previewUrl" class="text-center space-y-4">
              <div class="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                <span class="material-symbols-outlined text-4xl text-primary">cloud_upload</span>
              </div>
              <p class="text-secondary-fixed font-medium">拖拽或点击上传图片进行模拟识别</p>
              <p class="text-[10px] text-outline text-uppercase tracking-widest">Supports JPG, PNG (Max 10MB)</p>
            </div>

            <!-- 加载蒙层 -->
            <div v-if="isProcessing" class="absolute inset-0 bg-black/60 flex flex-col items-center justify-center backdrop-blur-sm z-20">
              <div class="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
              <p class="text-primary font-bold animate-pulse">AI 推理中...</p>
            </div>
          </div>

          <!-- 底部控制栏 (重构版: 极简且清晰) -->
          <div class="p-4 bg-surface-container/50 backdrop-blur-md flex flex-col md:flex-row justify-between items-center gap-6 border-t border-outline-variant/10">
            <!-- 场景选择 -->
            <div class="flex gap-2 p-1.5 bg-surface-container-high rounded-2xl border border-outline-variant/10">
               <el-radio-group v-model="scene" size="large" class="!flex !gap-1">
                <el-radio-button label="entry" class="custom-tab">入口登记</el-radio-button>
                <el-radio-button label="exit" class="custom-tab">离场结算</el-radio-button>
                <el-radio-button label="monitoring" class="custom-tab">车位同步</el-radio-button>
              </el-radio-group>
            </div>

            <div class="flex items-center gap-4 w-full md:w-auto">
              <!-- 精美的分段切换器 (代替看不清的 Switch) -->
              <div class="flex items-center p-1 bg-surface-container-lowest rounded-2xl border border-outline-variant/10 shadow-inner">
                <button 
                  @click="isBatchMode = false"
                  :class="['px-6 py-2 rounded-xl text-sm font-black transition-all duration-300 flex items-center gap-2', !isBatchMode ? 'bg-primary text-white shadow-lg shadow-primary/30' : 'text-secondary-fixed hover:bg-surface-container']"
                >
                  <span class="material-symbols-outlined text-sm">image</span>
                  单图模式
                </button>
                <button 
                  @click="isBatchMode = true"
                  :class="['px-6 py-2 rounded-xl text-sm font-black transition-all duration-300 flex items-center gap-2', isBatchMode ? 'bg-primary text-white shadow-lg shadow-primary/30' : 'text-secondary-fixed hover:bg-surface-container']"
                >
                  <span class="material-symbols-outlined text-sm">filter_none</span>
                  批量模式
                </button>
              </div>

              <!-- 主执行按钮 -->
              <div class="flex-1 md:flex-none">
                <el-button 
                  v-if="isBatchMode" 
                  type="success" 
                  size="large"
                  :loading="isProcessing" 
                  :disabled="batchFiles.length === 0" 
                  @click="startBatchRecognition" 
                  class="!rounded-2xl !px-8 !font-black !h-[48px] !border-none bg-gradient-to-r from-green-600 to-emerald-500 shadow-xl shadow-green-500/20 hover:scale-105 active:scale-95 !transition-all"
                >
                  开启批量引擎
                </el-button>
                <el-button 
                  v-else 
                  type="primary" 
                  size="large"
                  :loading="isProcessing" 
                  :disabled="!selectedFile" 
                  @click="startRecognition" 
                  class="!rounded-2xl !px-10 !font-black !h-[48px] !border-none bg-gradient-to-r from-primary to-blue-400 shadow-xl shadow-primary/20 hover:scale-105 active:scale-95 !transition-all"
                >
                  开始语义分析
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- 批量结果列表 -->
        <div v-if="isBatchMode && batchFiles.length > 0" class="space-y-4">
          <div class="flex justify-between items-end">
             <h4 class="text-xs font-bold text-secondary uppercase tracking-widest">待处理任务队列 ({{ batchFiles.length }})</h4>
             <el-button link type="danger" size="small" @click="batchFiles = []; batchResults = []">清空队列</el-button>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <div 
              v-for="(res, idx) in batchResults" 
              :key="idx"
              class="bg-surface-container-lowest rounded-2xl p-3 border border-outline-variant/10 animate-in fade-in zoom-in"
            >
              <div class="aspect-square rounded-xl overflow-hidden mb-2 bg-black">
                <!-- 🚀 修复图片路径拼接 -->
                <img :src="res.image_url.startsWith('http') ? res.image_url : `http://127.0.0.1:8000${res.image_url}`" class="w-full h-full object-cover" />
              </div>
              <div class="space-y-1">
                <div class="flex items-center justify-between">
                  <span v-if="res.energy_type" class="px-1 py-0.5 rounded-[4px] text-[8px] text-white font-bold" :class="res.energy_type === 'ICE' ? 'bg-blue-600' : 'bg-green-600'">{{ res.energy_type === 'ICE' ? '油车' : '电车' }}</span>
                </div>
                <p class="text-sm font-black text-on-surface">{{ res.plate_number || '未识别' }}</p>
              </div>
            </div>
            <!-- 占位符 -->
            <div v-for="n in Math.max(0, batchFiles.length - batchResults.length)" :key="'p'+n" class="aspect-square rounded-2xl border-2 border-dashed border-outline-variant/20 flex flex-col items-center justify-center text-outline opacity-40">
               <span class="material-symbols-outlined text-xl">image</span>
               <span class="text-[8px] mt-1">WAITING</span>
            </div>
          </div>
        </div>

        <!-- 识别结果统计 -->
        <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div class="bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant/10">
            <p class="text-xs text-secondary font-bold uppercase mb-1">识别车牌</p>
            <p class="text-2xl font-black text-on-surface">{{ analysisResult?.plate_number || '--' }}</p>
          </div>
          <div class="bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant/10">
            <p class="text-xs text-secondary font-bold uppercase mb-1">车辆类型</p>
            <div class="flex items-center gap-2 mt-1">
              <span 
                v-if="analysisResult?.energy_type"
                :class="[
                  'px-2 py-0.5 rounded text-[10px] font-bold text-white uppercase tracking-wider',
                  analysisResult.energy_type === 'ICE' ? 'bg-blue-600' : (analysisResult.energy_type === 'new_energy' ? 'bg-green-500' : 'bg-gray-500')
                ]"
              >
                {{ analysisResult.energy_type === 'ICE' ? '油车' : (analysisResult.energy_type === 'new_energy' ? '电车' : analysisResult.energy_type) }}
              </span>
            </div>
          </div>
          <div class="bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant/10">
            <p class="text-xs text-secondary font-bold uppercase mb-1">推理时间</p>
            <p class="text-2xl font-black text-green-600">{{ inferenceTime ? `${inferenceTime}ms` : '--' }}</p>
          </div>
        </div>
      </div>

      <!-- 右侧：联动日志 -->
      <div class="space-y-6">
        <div class="rounded-3xl bg-surface-container-lowest border border-outline-variant/20 shadow-xl h-[600px] flex flex-col overflow-hidden">
          <div class="p-6 border-b border-outline-variant/10 flex justify-between items-center">
            <h3 class="font-bold flex items-center gap-2">
              <span class="material-symbols-outlined text-primary">history</span>
              系统联动日志
            </h3>
            <span class="text-[10px] bg-secondary/10 text-secondary px-2 py-0.5 rounded font-bold">REAL-TIME</span>
          </div>
          
          <div class="flex-1 overflow-y-auto p-4 space-y-4 font-mono text-sm custom-scrollbar">
            <div v-if="logs.length === 0" class="h-full flex flex-col items-center justify-center text-outline opacity-50">
                <span class="material-symbols-outlined text-5xl mb-2">dataset_linked</span>
                <p>等待联动指令触发...</p>
            </div>
            <div v-for="(log, i) in logs" :key="i"
                 class="p-3 rounded-xl bg-surface-container flex gap-3 border-l-4 cursor-pointer transition-all hover:bg-surface-container-high"
                 :class="log.expanded ? 'border-l-4 border-l-primary' : 'border-l-4 border-l-primary/40'"
                 @click="toggleLogDetail(i)">
               <span class="text-[10px] text-outline mt-1 flex-shrink-0">{{ log.time }}</span>
               <div class="flex-1 min-w-0">
                 <p class="text-on-surface font-semibold text-sm">{{ log.action }}</p>
                 <p class="text-xs text-secondary mt-1 truncate">{{ log.detail }}</p>
                 <div v-if="log.expanded && log.raw" class="mt-2 pt-2 border-t border-outline-variant/20">
                   <pre class="text-[10px] text-outline whitespace-pre-wrap break-all leading-relaxed max-h-32 overflow-y-auto">{{ typeof log.raw === 'object' ? JSON.stringify(log.raw, null, 2) : log.raw }}</pre>
                 </div>
               </div>
               <span class="material-symbols-outlined text-[14px] text-outline flex-shrink-0 self-start mt-0.5">{{ log.expanded ? 'expand_less' : 'expand_more' }}</span>
            </div>
          </div>

          <div class="p-4 bg-primary/5 text-center">
             <p class="text-[10px] text-primary font-bold uppercase tracking-widest">Sentinel AI Engine v1.2</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'

const scene = ref('entry')
const isProcessing = ref(false)
const selectedFile = ref(null)
const previewUrl = ref('')
const analysisResult = ref(null)
const inferenceTime = ref(0)
const logs = ref([])
const fileInput = ref(null)
const sourceImg = ref(null)

// 🚀 批量模式扩展
const isBatchMode = ref(false)
const batchFiles = ref([])
const batchResults = ref([])

const triggerUpload = () => fileInput.value.click()

const handleFileChange = (e) => {
  if (isBatchMode.value) {
    const files = Array.from(e.target.files)
    setBatchFiles(files)
  } else {
    const file = e.target.files[0]
    if (file) setFile(file)
  }
}

const handleDrop = (e) => {
  if (isBatchMode.value) {
    const files = Array.from(e.dataTransfer.files)
    setBatchFiles(files)
  } else {
    const file = e.dataTransfer.files[0]
    if (file) setFile(file)
  }
}

const setBatchFiles = (files) => {
  const images = files.filter(f => f.type.startsWith('image/'))
  if (images.length === 0) return
  batchFiles.value = images
  batchResults.value = []
  // 取第一张作为大图预览
  setFile(images[0])
}

const setFile = (file) => {
  if (!file.type.startsWith('image/')) {
    ElMessage.error('只允许上传图片文件')
    return
  }
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  analysisResult.value = null
  inferenceTime.value = 0
  clearCanvas()
}

const startRecognition = async () => {
  if (!selectedFile.value) return
  
  isProcessing.value = true
  const startTime = Date.now()
  
  const formData = new FormData()
  formData.append('image', selectedFile.value)
  formData.append('scene', scene.value)

  try {
    const res = await request.post('/ai/recognize/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000  // 含首次模型加载，约 3-5s 识别 + 模型下载
    })
    
    if (res.success) {
      analysisResult.value = res
      inferenceTime.value = Date.now() - startTime

      logs.value.unshift({
        time: new Date().toLocaleTimeString(),
        action: scene.value === 'entry' ? '入场自动核销' : (scene.value === 'exit' ? '离场账单结算' : '车位状态映射'),
        detail: res.action_taken || '识别成功，系统已自动响应'
      })

      drawResults()
      ElMessage.success('视觉感知分析完成')
    } else {
      inferenceTime.value = Date.now() - startTime
      ElMessage.warning(res.detail || '未识别到车牌')
    }
  } catch (err) {
    console.error(err)
    ElMessage.error('AI 推理失败')
  } finally {
    isProcessing.value = false
  }
}

const startBatchRecognition = async () => {
  if (batchFiles.value.length === 0) return
  
  isProcessing.value = true
  batchResults.value = []
  
  const formData = new FormData()
  batchFiles.value.forEach(file => {
    formData.append('images', file)
  })
  formData.append('scene', scene.value)

  try {
    const res = await request.post('/ai/recognize/batch-recognize/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000 // 批量单帧模式，约 20-30s
    })
    
    batchResults.value = res.results
    
    // 添加聚合日志
    logs.value.unshift({
      time: new Date().toLocaleTimeString(),
      action: '批量感知任务完成',
      detail: `成功识别 ${res.count} 辆入场车辆，系统已完成批量登记逻辑。`
    })

    ElMessage.success(`批量分析完成，共识别 ${res.count} 个目标`)
  } catch (err) {
    console.error(err)
    ElMessage.error('批量识别任务异常')
  } finally {
    isProcessing.value = false
  }
}

const clearCanvas = () => {
  const canvas = document.getElementById('recognitionCanvas')
  if (canvas) canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
}

const drawResults = () => {
  if (!analysisResult.value || !analysisResult.value.result_data || !sourceImg.value) return
  
  const canvas = document.getElementById('recognitionCanvas')
  const ctx = canvas.getContext('2d')
  const img = sourceImg.value
  
  // 匹配 Canvas 大小与图片原始比例，但也要适应屏幕容器
  canvas.width = img.naturalWidth
  canvas.height = img.naturalHeight
  
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  const detections = analysisResult.value.result_data.detections || []
  
  detections.forEach(det => {
    const [x1, y1, x2, y2] = det.bbox
    
    // 绘制主边框 (Neumorphism / Sci-fi Style)
    ctx.strokeStyle = '#34d399' // 绿色
    ctx.lineWidth = Math.max(2, canvas.width / 200)
    ctx.strokeRect(x1, y1, x2 - x1, y2 - y1)
    
    // 绘制拐角强化
    const cornerSize = (x2 - x1) * 0.2
    ctx.beginPath()
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = ctx.lineWidth * 2
    // 左上
    ctx.moveTo(x1, y1 + cornerSize); ctx.lineTo(x1, y1); ctx.lineTo(x1 + cornerSize, y1)
    // 右上
    ctx.moveTo(x2 - cornerSize, y1); ctx.lineTo(x2, y1); ctx.lineTo(x2, y1 + cornerSize)
    // ... 简单画两个角
    ctx.stroke()

    // 绘制标签背景
    ctx.fillStyle = 'rgba(52, 211, 153, 0.9)'
    const fontSize = Math.max(12, canvas.width / 50)
    ctx.font = `bold ${fontSize}px Inter, sans-serif`
    const text = `${det.type} ${det.plate || ''}`.trim()
    const textWidth = ctx.measureText(text).width
    ctx.fillRect(x1, y1 - fontSize - 5, textWidth + 10, fontSize + 5)
    
    // 绘制文字
    ctx.fillStyle = '#111827'
    ctx.fillText(text, x1 + 5, y1 - 8)
  })
}

function toggleLogDetail(index) {
  if (logs.value[index]) {
    logs.value[index].expanded = !logs.value[index].expanded
  }
}

onMounted(() => {
  window.addEventListener('resize', drawResults)
})
</script>

<style scoped>
.font-headline {
  font-family: 'Outfit', sans-serif;
}
.font-mono {
  font-family: 'JetBrains Mono', monospace;
}
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(var(--primary-rgb), 0.2);
  border-radius: 10px;
}
</style>
