<template>
  <div class="parking-system-container">
    <header class="app-header">
      <h1>🚗 停车场管理系统</h1>
      <div class="header-actions">
        <button class="action-btn find-car" @click="showFindDialog = true">
          🔍 寻找我的车
        </button>
      </div>
    </header>

    <main class="app-main">
      <!-- 多楼层地图组件 -->
      <MultiFloorMap ref="mapComponent" />
    </main>

    <!-- 全局寻车对话框 -->
    <div v-if="showFindDialog" class="modal-overlay" @click.self="showFindDialog = false">
      <div class="modal-dialog modal-find">
        <div class="modal-header">
          <h3>🔍 寻找我的车</h3>
          <button class="close-btn" @click="showFindDialog = false">✕</button>
        </div>
        <div class="modal-body">
          <input
            v-model="findPlateNumber"
            type="text"
            placeholder="输入车牌号，如 京A88888"
            class="input-plate"
            @keyup.enter="submitFind"
          />
          <div v-if="findResult" :class="['find-result', findResult.status]">
            <div v-if="findResult.status === 'success'">
              <p>✅ <strong>找到您的车！</strong></p>
              <p v-if="findResult.data">
                <strong>车位:</strong> {{ findResult.data.space_id }}
              </p>
              <p v-if="findResult.data">
                <strong>楼层:</strong> {{ findResult.data.floor }} 楼
              </p>
            </div>
            <div v-else>
              <p>❌ <strong>未找到您的车</strong></p>
              <p v-if="findResult.error">错误: {{ findResult.error }}</p>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showFindDialog = false">关闭</button>
          <button 
            class="btn-submit" 
            @click="submitFind" 
            :disabled="!findPlateNumber || findLoading"
          >
            {{ findLoading ? '搜索中...' : '搜索' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="app-footer">
      <p>© 2026 智能停车场管理系统 | 传感器-二维码绑定系统</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MultiFloorMap from '@/components/MultiFloorMap.vue'
import { findCarByPlate } from '@/api/parking.js'

const showFindDialog = ref(false)
const findPlateNumber = ref('')
const findLoading = ref(false)
const findResult = ref(null)
const mapComponent = ref(null)

const submitFind = async () => {
  if (!findPlateNumber.value) return
  
  findLoading.value = true
  findResult.value = null
  
  try {
    const response = await findCarByPlate(findPlateNumber.value)
    findResult.value = {
      status: 'success',
      data: response.data
    }
    // 如果找到车，自动切换到相应楼层
    if (response.data?.floor && mapComponent.value) {
      mapComponent.value.selectedFloor = response.data.floor
    }
  } catch (err) {
    findResult.value = {
      status: 'error',
      error: err.message || '未找到该车辆'
    }
  } finally {
    findLoading.value = false
  }
}
</script>

<style scoped>
.parking-system-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.app-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: bold;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  font-size: 14px;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.action-btn.find-car {
  background: rgba(76, 175, 80, 0.3);
  border-color: rgba(76, 175, 80, 0.6);
}

.action-btn.find-car:hover {
  background: rgba(76, 175, 80, 0.5);
}

.app-main {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.app-footer {
  background: white;
  border-top: 1px solid #e0e0e0;
  padding: 16px;
  text-align: center;
  color: #999;
  font-size: 12px;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-dialog {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-width: 400px;
  width: 90%;
  max-height: 80vh;
  overflow: auto;
}

.modal-find {
  max-width: 500px;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px 12px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.modal-body {
  padding: 20px;
}

.input-plate {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.input-plate:focus {
  outline: none;
  border-color: #667eea;
}

.find-result {
  margin-top: 16px;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.find-result.success {
  background: #c8e6c9;
  border: 1px solid #4caf50;
  color: #2e7d32;
}

.find-result.error {
  background: #ffcdd2;
  border: 1px solid #f44336;
  color: #c62828;
}

.find-result p {
  margin: 6px 0;
}

.find-result strong {
  font-weight: bold;
}

.modal-footer {
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.btn-cancel,
.btn-submit {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.btn-cancel {
  background: #e0e0e0;
  color: #333;
}

.btn-cancel:hover {
  background: #d0d0d0;
}

.btn-submit {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transform: translateY(-2px);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-header {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }

  .app-header h1 {
    font-size: 22px;
  }

  .header-actions {
    width: 100%;
    justify-content: center;
  }

  .action-btn {
    flex: 1;
    max-width: 200px;
  }

  .modal-dialog {
    max-width: 90vw;
  }
}
</style>
