<template>
  <div class="simulator-container">
    <!-- 标题 -->
    <div class="simulator-header">
      <h1>🚗 传感器与二维码寻车逻辑模拟器</h1>
      <p class="subtitle">演示智慧停车系统的核心数据流与绑定逻辑</p>
    </div>

    <div class="simulator-body">
      <!-- 左侧：停车场模拟视图 -->
      <div class="left-panel">
        <h3>📍 停车场模拟视图</h3>
        <div class="parking-grid">
          <div
            v-for="(space, idx) in parkingSpaces"
            :key="idx"
            class="space-card"
            :class="space.sensorState === 'occupied' ? 'occupied' : 'free'"
            @click="selectSpace(space)"
          >
            <div class="space-id">{{ space.id }}</div>
            <div class="space-status">
              <span v-if="space.sensorState === 'occupied'" class="status-badge occupied">
                🔴 占用
              </span>
              <span v-else class="status-badge free">
                🟢 空闲
              </span>
            </div>
            <div class="space-plate">
              {{ space.plate || '—' }}
            </div>
            <div class="space-qr">
              <span v-if="space.sensorState === 'occupied'" class="qr-icon" @click.stop="simulateScan(space)">
                🔲 扫码
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 中间：控制面板 -->
      <div class="middle-panel">
        <h3>⚙️ 控制面板</h3>

        <!-- 模拟硬件传感器 -->
        <div class="control-section">
          <h4>📡 传感器模拟</h4>
          <div class="sensor-controls">
            <div
              v-for="(space, idx) in parkingSpaces"
              :key="`sensor-${idx}`"
              class="sensor-item"
            >
              <span class="space-label">{{ space.id }}</span>
              <el-switch
                v-model="space.sensorState"
                active-value="occupied"
                inactive-value="free"
                @change="() => handleSensorChange(space)"
              />
              <span class="sensor-status">
                {{ space.sensorState === 'occupied' ? '有车' : '无车' }}
              </span>
            </div>
          </div>
          <p class="tip">💡 切换开关以模拟传感器探测到车辆进出</p>
        </div>

        <!-- 用户扫码绑定 -->
        <div class="control-section">
          <h4>📱 用户扫码绑定</h4>
          <div v-if="selectedSpace" class="scan-input">
            <p>选中车位：<strong>{{ selectedSpace.id }}</strong></p>
            <el-input
              v-model="scanPlateNumber"
              placeholder="输入车牌号 (例: 京A88888)"
              clearable
            />
            <el-button
              type="primary"
              @click="performBinding"
              :disabled="selectedSpace.sensorState !== 'occupied' || !scanPlateNumber"
              class="bind-button"
            >
              确认绑定
            </el-button>
            <div v-if="selectedSpace.sensorState !== 'occupied'" class="warning">
              ⚠️ 车位为空闲状态，无法绑定（需要传感器先探测到车）
            </div>
          </div>
          <div v-else class="hint">
            👈 请先在左侧选择一个车位
          </div>
        </div>
      </div>

      <!-- 右侧：数据库与日志 -->
      <div class="right-panel">
        <h3>🗄️ 实时数据库状态</h3>

        <!-- 数据库表格 -->
        <div class="db-table">
          <table>
            <thead>
              <tr>
                <th>车位ID</th>
                <th>传感器状态</th>
                <th>绑定车牌</th>
                <th>更新时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(space, idx) in parkingSpaces" :key="`db-${idx}`">
                <td class="space-id-cell">{{ space.id }}</td>
                <td>
                  <span :class="'status-' + space.sensorState">
                    {{ space.sensorState === 'occupied' ? '占用(1)' : '空闲(0)' }}
                  </span>
                </td>
                <td class="plate-cell">
                  <span v-if="space.plate" class="plate-badge">{{ space.plate }}</span>
                  <span v-else class="empty-cell">—</span>
                </td>
                <td class="time-cell">{{ formatTime(space.lastUpdated) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 控制台日志 -->
        <h4 class="log-title">📝 控制台日志</h4>
        <div class="console-log">
          <div v-if="logs.length === 0" class="empty-log">
            (等待事件...)
          </div>
          <div v-for="(log, idx) in logs.slice(-10)" :key="`log-${idx}`" :class="'log-' + log.type">
            <span class="log-time">[{{ formatTime(log.time) }}]</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>

        <!-- 清除日志按钮 -->
        <el-button @click="clearLogs" size="small" class="clear-btn">
          清除日志
        </el-button>
      </div>
    </div>

    <!-- 模拟绑定弹窗 -->
    <el-dialog
      v-model="scanDialogVisible"
      title="📱 扫描车位二维码"
      width="40%"
      :close-on-click-modal="false"
    >
      <div class="scan-modal">
        <div class="qr-code">
          <div class="qr-placeholder">
            🔲
          </div>
          <p>车位：{{ scannedSpace?.id }}</p>
          <p class="qr-token">QR_{{ scannedSpace?.id }}_2026041901</p>
        </div>

        <el-form>
          <el-form-item label="车牌号">
            <el-input
              v-model="scanPlateNumber"
              placeholder="输入您的车牌号"
              clearable
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="scanDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            @click="performBindingFromDialog"
            :disabled="!scanPlateNumber"
            :loading="bindingInProgress"
          >
            记录位置
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 结果提示 -->
    <el-notification
      v-if="showNotification"
      :title="notificationData.title"
      :description="notificationData.description"
      :type="notificationData.type"
      :duration="3000"
      position="top-right"
      @close="showNotification = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'

// ============ 响应式状态 ============

const parkingSpaces = reactive([
  {
    id: 'A01',
    sensorState: 'free',
    plate: null,
    qrToken: 'QR_A01_2026041901',
    lastUpdated: new Date()
  },
  {
    id: 'A02',
    sensorState: 'occupied',
    plate: '京A88888',
    qrToken: 'QR_A02_2026041901',
    lastUpdated: new Date()
  },
  {
    id: 'A03',
    sensorState: 'occupied',
    plate: null,
    qrToken: 'QR_A03_2026041901',
    lastUpdated: new Date()
  },
  {
    id: 'B01',
    sensorState: 'free',
    plate: null,
    qrToken: 'QR_B01_2026041901',
    lastUpdated: new Date()
  }
])

const selectedSpace = ref(null)
const scanPlateNumber = ref('')
const scanDialogVisible = ref(false)
const scannedSpace = ref(null)
const bindingInProgress = ref(false)
const logs = ref([])
const showNotification = ref(false)
const notificationData = ref({
  title: '',
  description: '',
  type: 'success'
})

// ============ 方法 ============

/**
 * 选择车位
 */
function selectSpace(space) {
  selectedSpace.value = space
  scanPlateNumber.value = ''
  addLog(`选中车位 ${space.id}`)
}

/**
 * 模拟扫描二维码
 */
function simulateScan(space) {
  if (space.sensorState !== 'occupied') {
    showNotificationMessage(
      '⚠️ 车位为空闲',
      '该车位没有车辆，无法扫码绑定',
      'warning'
    )
    addLog(`扫码失败: ${space.id} 车位为空闲状态`, 'error')
    return
  }

  scannedSpace.value = space
  scanDialogVisible.value = true
  scanPlateNumber.value = ''
  addLog(`扫描二维码: ${space.id}`)
}

/**
 * 执行绑定（来自弹窗）
 */
function performBindingFromDialog() {
  performBinding()
  scanDialogVisible.value = false
}

/**
 * 执行绑定逻辑
 */
function performBinding() {
  if (!selectedSpace.value && !scannedSpace.value) {
    ElMessage.warning('请先选择车位')
    return
  }

  const space = selectedSpace.value || scannedSpace.value
  const plate = scanPlateNumber.value.trim()

  if (!plate) {
    ElMessage.warning('请输入车牌号')
    return
  }

  // 校验车位状态
  if (space.sensorState !== 'occupied') {
    showNotificationMessage(
      '❌ 绑定失败',
      `车位 ${space.id} 当前为空闲状态，无法绑定`,
      'error'
    )
    addLog(
      `绑定失败: ${space.id} 状态为 ${space.sensorState}，需要状态为 occupied`,
      'error'
    )
    return
  }

  // 执行绑定
  bindingInProgress.value = true
  setTimeout(() => {
    space.plate = plate
    space.lastUpdated = new Date()
    bindingInProgress.value = false

    showNotificationMessage(
      '✅ 绑定成功',
      `车牌 ${plate} 已成功绑定到车位 ${space.id}`,
      'success'
    )
    addLog(
      `✅ 绑定成功: 车牌 ${plate} → 车位 ${space.id}`,
      'success'
    )

    scanPlateNumber.value = ''
    selectedSpace.value = null
  }, 800)
}

/**
 * 处理传感器状态变化
 */
function handleSensorChange(space) {
  space.lastUpdated = new Date()

  if (space.sensorState === 'occupied') {
    // 从空闲变为占用（车进来了）
    addLog(`📍 传感器探测: 车驶入 ${space.id}`, 'info')
  } else {
    // 从占用变为空闲（车离开了）
    const previousPlate = space.plate
    space.plate = null // ⭐ 关键逻辑：传感器变空闲时清空绑定信息

    if (previousPlate) {
      addLog(
        `🚗 车离开: ${space.id} 的车牌 ${previousPlate} 已清空`,
        'warning'
      )
    } else {
      addLog(`✓ 传感器探测: ${space.id} 车位已空闲`, 'info')
    }
  }
}

/**
 * 添加日志
 */
function addLog(message, type = 'info') {
  logs.value.push({
    message,
    type,
    time: new Date()
  })
}

/**
 * 清除日志
 */
function clearLogs() {
  logs.value = []
  addLog('日志已清除')
}

/**
 * 显示通知
 */
function showNotificationMessage(title, description, type = 'success') {
  notificationData.value = {
    title,
    description,
    type
  }
  showNotification.value = true
}

/**
 * 格式化时间
 */
function formatTime(date) {
  if (!date) return '--:--:--'
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

// 初始化日志
addLog('🎬 模拟器已启动，准备演示...')
addLog('💡 左侧：切换传感器开关以模拟车辆进出')
addLog('💡 中间：选择车位后可进行扫码绑定')
addLog('💡 右侧：实时查看数据库状态变化')
</script>

<style scoped lang="scss">
.simulator-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;

  .simulator-header {
    text-align: center;
    color: white;
    margin-bottom: 30px;

    h1 {
      margin: 0 0 10px 0;
      font-size: 28px;
      font-weight: 700;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }

    .subtitle {
      margin: 0;
      font-size: 14px;
      opacity: 0.9;
    }
  }

  .simulator-body {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 20px;
    max-width: 1400px;
    margin: 0 auto;

    > div {
      background: white;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);

      h3 {
        margin: 0 0 15px 0;
        font-size: 18px;
        font-weight: 600;
        color: #333;
        border-bottom: 2px solid #667eea;
        padding-bottom: 10px;
      }

      h4 {
        margin: 15px 0 10px 0;
        font-size: 14px;
        font-weight: 600;
        color: #555;
      }
    }
  }

  // 左侧面板：停车场视图
  .left-panel {
    .parking-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;

      .space-card {
        padding: 15px;
        border: 2px solid #ddd;
        border-radius: 8px;
        background: #f9f9f9;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;

        &.free {
          background: linear-gradient(135deg, #e0f7fa, #b3e5fc);
          border-color: #0288d1;
        }

        &.occupied {
          background: linear-gradient(135deg, #ffebee, #ffcdd2);
          border-color: #d32f2f;
        }

        &:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 16px rgba(0, 0, 0, 0.12);
        }

        .space-id {
          font-size: 16px;
          font-weight: 700;
          color: #333;
          margin-bottom: 8px;
        }

        .space-status {
          margin-bottom: 8px;

          .status-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;

            &.occupied {
              background: #ffcdd2;
              color: #c62828;
            }

            &.free {
              background: #c8e6c9;
              color: #2e7d32;
            }
          }
        }

        .space-plate {
          font-size: 13px;
          color: #666;
          margin-bottom: 8px;
          font-family: monospace;
          font-weight: 600;
          height: 20px;
        }

        .space-qr {
          .qr-icon {
            display: inline-block;
            padding: 6px 10px;
            background: #667eea;
            color: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: background 0.3s;

            &:hover {
              background: #5568d3;
            }
          }
        }
      }
    }
  }

  // 中间面板：控制
  .middle-panel {
    .control-section {
      margin-bottom: 20px;
      padding: 15px;
      background: #f9f9f9;
      border-radius: 8px;

      .sensor-controls {
        .sensor-item {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 10px;
          padding: 8px;
          background: white;
          border-radius: 4px;

          .space-label {
            font-weight: 600;
            color: #333;
            width: 40px;
          }

          .sensor-status {
            font-size: 12px;
            color: #666;
            flex: 1;
          }
        }
      }

      .scan-input {
        .bind-button {
          width: 100%;
          margin-top: 10px;
        }

        .warning {
          margin-top: 10px;
          padding: 8px;
          background: #fff3cd;
          border-left: 3px solid #ffc107;
          font-size: 12px;
          color: #856404;
          border-radius: 2px;
        }
      }

      .hint {
        text-align: center;
        color: #999;
        font-size: 12px;
        padding: 20px;
      }

      .tip {
        margin-top: 8px;
        font-size: 11px;
        color: #666;
        font-style: italic;
      }
    }
  }

  // 右侧面板：数据库与日志
  .right-panel {
    .db-table {
      margin-bottom: 20px;
      overflow: auto;
      max-height: 200px;

      table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;

        thead {
          position: sticky;
          top: 0;
          background: #667eea;
          color: white;

          th {
            padding: 8px;
            text-align: left;
            font-weight: 600;
          }
        }

        tbody tr {
          border-bottom: 1px solid #eee;

          &:hover {
            background: #f5f5f5;
          }

          td {
            padding: 8px;

            .space-id-cell {
              font-weight: 600;
              color: #333;
            }

            .status-free {
              color: #2e7d32;
              font-weight: 600;
            }

            .status-occupied {
              color: #c62828;
              font-weight: 600;
            }

            .plate-badge {
              display: inline-block;
              padding: 2px 6px;
              background: #e3f2fd;
              color: #1565c0;
              border-radius: 3px;
              font-family: monospace;
              font-weight: 600;
            }

            .empty-cell {
              color: #ccc;
            }

            .time-cell {
              font-family: monospace;
              color: #999;
            }
          }
        }
      }
    }

    .log-title {
      margin: 15px 0 10px 0;
      font-size: 13px;
      font-weight: 600;
      color: #555;
    }

    .console-log {
      background: #1e1e1e;
      color: #00ff00;
      padding: 12px;
      border-radius: 6px;
      font-family: 'Courier New', monospace;
      font-size: 11px;
      line-height: 1.6;
      max-height: 250px;
      overflow-y: auto;

      .empty-log {
        color: #666;
        font-style: italic;
      }

      [class^='log-'] {
        display: flex;
        gap: 8px;
        margin-bottom: 4px;

        .log-time {
          color: #888;
          flex-shrink: 0;
        }

        .log-message {
          flex: 1;
          word-break: break-all;
        }
      }

      .log-success {
        color: #00ff00;
      }

      .log-info {
        color: #00aaff;
      }

      .log-warning {
        color: #ffaa00;
      }

      .log-error {
        color: #ff6666;
      }
    }

    .clear-btn {
      width: 100%;
      margin-top: 10px;
    }
  }
}

.scan-modal {
  text-align: center;

  .qr-code {
    margin-bottom: 20px;
    padding: 20px;
    background: #f5f5f5;
    border-radius: 8px;

    .qr-placeholder {
      font-size: 80px;
      margin-bottom: 10px;
    }

    p {
      margin: 8px 0;
      font-size: 13px;
      color: #666;

      &.qr-token {
        font-family: monospace;
        font-weight: 600;
        color: #333;
      }
    }
  }
}

@media (max-width: 1200px) {
  .simulator-body {
    grid-template-columns: 1fr !important;
  }
}
</style>
