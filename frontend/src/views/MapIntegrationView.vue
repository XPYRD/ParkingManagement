<template>
  <div class="map-integration-page">
    <!-- 标签页导航 -->
    <el-tabs v-model="activeTab" class="tabs-header" type="border-card">
      <el-tab-pane label="🗺️ SVG 交互地图" name="map">
        <template #label>
          <span>
            <i class="el-icon-map"></i>
            SVG 交互地图
          </span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="🎮 模拟演示" name="simulator">
        <template #label>
          <span>
            <i class="el-icon-video-play"></i>
            模拟演示
          </span>
        </template>
      </el-tab-pane>
      <el-tab-pane label="📖 使用指南" name="guide">
        <template #label>
          <span>
            <i class="el-icon-document"></i>
            使用指南
          </span>
        </template>
      </el-tab-pane>
    </el-tabs>

    <!-- 标签页内容 -->
    <div class="tabs-content">
      <!-- SVG 交互地图 -->
      <div v-show="activeTab === 'map'" class="tab-pane">
        <interactive-map />
      </div>

      <!-- 模拟演示 -->
      <div v-show="activeTab === 'simulator'" class="tab-pane">
        <sensor-qr-simulator />
      </div>

      <!-- 使用指南 -->
      <div v-show="activeTab === 'guide'" class="tab-pane guide-pane">
        <div class="guide-content">
          <h2>📖 系统使用指南</h2>

          <!-- 系统架构 -->
          <section class="guide-section">
            <h3>🏗️ 系统架构概述</h3>
            <div class="architecture-diagram">
              <div class="arch-box">
                <strong>硬件层（传感器）</strong>
                <p>超声波/地磁传感器</p>
              </div>
              <div class="arrow">→</div>
              <div class="arch-box">
                <strong>后端API</strong>
                <p>Webhook + 绑定接口</p>
              </div>
              <div class="arrow">→</div>
              <div class="arch-box">
                <strong>前端UI</strong>
                <p>SVG地图 + 交互</p>
              </div>
            </div>
          </section>

          <!-- 核心功能 -->
          <section class="guide-section">
            <h3>🎯 核心功能说明</h3>

            <div class="feature-card">
              <h4>① 传感器状态同步</h4>
              <p><strong>工作流程：</strong></p>
              <ol>
                <li>硬件传感器探测到车辆进出</li>
                <li>通过 <code>POST /api/v1/hardware/webhook/</code> 推送事件</li>
                <li>后端更新 ParkingSpace 表的 status 字段</li>
                <li>前端轮询获取最新状态，更新 SVG 颜色</li>
              </ol>
              <p><strong>状态定义：</strong></p>
              <ul>
                <li>status = 0（free）→ SVG 显示绿色 🟢</li>
                <li>status = 1（occupied）→ SVG 显示红色 🔴</li>
              </ul>
            </div>

            <div class="feature-card">
              <h4>② 二维码绑定流程</h4>
              <p><strong>用户操作：</strong></p>
              <ol>
                <li>用户停稳车辆后，传感器检测到占用</li>
                <li>用户扫描车位前的二维码（包含 space_id + qr_code_token）</li>
                <li>跳转至绑定页面，输入车牌号</li>
                <li>调用 <code>POST /api/v1/parking_spaces/bind/</code> 接口</li>
                <li>后端更新 ParkingSpace.current_plate 字段</li>
              </ol>
              <p><strong>关键逻辑：</strong></p>
              <ul>
                <li>只有 status=occupied 的车位才能绑定</li>
                <li>传感器检测车离开（status→free）时，自动清空 current_plate</li>
              </ul>
            </div>

            <div class="feature-card">
              <h4>③ 反向寻车算法</h4>
              <p><strong>用户场景：</strong> 用户忘记停在哪里，想找自己的车</p>
              <p><strong>操作流程：</strong></p>
              <ol>
                <li>用户在停车场某处（如电梯口）扫描"起始点二维码"</li>
                <li>获取当前位置 <code>start_node</code></li>
                <li>输入车牌号查询，后端返回车所在的 space_id</li>
                <li>获取目标位置坐标 <code>target_node</code></li>
                <li>使用 Dijkstra 算法计算最短路径</li>
                <li>前端在 SVG 地图上绘制导引虚线和箭头</li>
              </ol>
            </div>
          </section>

          <!-- API 端点 -->
          <section class="guide-section">
            <h3>🔌 API 端点清单</h3>
            <el-table :data="apiEndpoints" stripe>
              <el-table-column prop="method" label="方法" width="80">
                <template #default="{ row }">
                  <el-tag :type="getMethodColor(row.method)">{{ row.method }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="endpoint" label="端点" width="280" />
              <el-table-column prop="description" label="说明" show-overflow-tooltip />
            </el-table>
          </section>

          <!-- 数据库模型 -->
          <section class="guide-section">
            <h3>🗄️ ParkingSpace 数据库模型</h3>
            <div class="model-diagram">
              <div class="model-field">
                <span class="field-name">space_id</span>
                <span class="field-type">CharField</span>
                <span class="field-desc">车位编号（对应 SVG id）</span>
              </div>
              <div class="model-field">
                <span class="field-name">qr_code_token</span>
                <span class="field-type">CharField</span>
                <span class="field-desc">二维码唯一识别码</span>
              </div>
              <div class="model-field">
                <span class="field-name">status</span>
                <span class="field-type">CharField</span>
                <span class="field-desc">free/occupied（由传感器决定）</span>
              </div>
              <div class="model-field">
                <span class="field-name">current_plate</span>
                <span class="field-type">CharField</span>
                <span class="field-desc">绑定的车牌号（由用户决定）</span>
              </div>
              <div class="model-field">
                <span class="field-name">bind_time</span>
                <span class="field-type">DateTimeField</span>
                <span class="field-desc">绑定时间</span>
              </div>
              <div class="model-field">
                <span class="field-name">x, y</span>
                <span class="field-type">FloatField</span>
                <span class="field-desc">坐标（路径规划用）</span>
              </div>
            </div>
          </section>

          <!-- 快速开始 -->
          <section class="guide-section">
            <h3>⚡ 快速开始</h3>
            <div class="quickstart-steps">
              <div class="step">
                <div class="step-number">1</div>
                <div class="step-content">
                  <strong>初始化数据</strong>
                  <p>运行管理后台，创建 ParkingSpace 记录，填入 space_id、qr_code_token、x、y</p>
                </div>
              </div>
              <div class="step">
                <div class="step-number">2</div>
                <div class="step-content">
                  <strong>准备 SVG 地图</strong>
                  <p>在 <code>/frontend/src/assets/</code> 放置 <code>interactive_map.svg</code></p>
                </div>
              </div>
              <div class="step">
                <div class="step-number">3</div>
                <div class="step-content">
                  <strong>配置后端 WebHook</strong>
                  <p>在硬件网关设置推送地址为 <code>/api/v1/hardware/webhook/</code></p>
                </div>
              </div>
              <div class="step">
                <div class="step-number">4</div>
                <div class="step-content">
                  <strong>启动前端轮询</strong>
                  <p>SVG 地图组件会自动每 5 秒轮询 <code>/api/v1/map/spaces/</code></p>
                </div>
              </div>
              <div class="step">
                <div class="step-number">5</div>
                <div class="step-content">
                  <strong>测试系统</strong>
                  <p>在"模拟演示"标签页测试传感器+绑定的完整流程</p>
                </div>
              </div>
            </div>
          </section>

          <!-- 常见问题 -->
          <section class="guide-section">
            <h3>❓ 常见问题</h3>
            <el-collapse>
              <el-collapse-item title="Q: 为什么我的车位总是显示空闲？" name="1">
                <p>A: 检查以下几点：</p>
                <ul>
                  <li>传感器是否正常工作？使用测试接口推送事件</li>
                  <li>WebHook 是否已配置？检查硬件网关设置</li>
                  <li>ParkingSpace 表中是否有该车位的记录？</li>
                </ul>
              </el-collapse-item>
              <el-collapse-item title="Q: 传感器显示占用，但没有绑定车牌，寻车时会怎样？" name="2">
                <p>A: 系统只能寻到已绑定车牌的车位。未绑定的车位无法通过寻车功能找到，但地图上会显示红色（占用状态）。</p>
              </el-collapse-item>
              <el-collapse-item title="Q: 如果用户没有扫码绑定车牌会怎样？" name="3">
                <p>A: 车位会长期显示为"占用但未绑定"，这种车位：</p>
                <ul>
                  <li>用户无法通过寻车功能找到</li>
                  <li> 可能是异常情况（传感器误触、故障等）</li>
                  <li>管理员可以在后台手动处理</li>
                </ul>
              </el-collapse-item>
              <el-collapse-item title="Q: 路径规划需要如何配置？" name="4">
                <p>A: 路径规划基于 SpotConnection 模型：</p>
                <ul>
                  <li>在管理后台创建停车位间的连接关系</li>
                  <li>设置每条连接的距离值</li>
                  <li>系统使用 Dijkstra 算法计算最短路径</li>
                </ul>
              </el-collapse-item>
            </el-collapse>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import InteractiveMap from '@/components/InteractiveMap.vue'
import SensorQRSimulator from '@/components/SensorQRSimulator.vue'

const activeTab = ref('map')

const apiEndpoints = [
  {
    method: 'GET',
    endpoint: '/api/v1/map/spaces/',
    description: '获取全局车位状态（前端轮询用）'
  },
  {
    method: 'GET',
    endpoint: '/api/v1/map/find_car/?plate_number=京A88888',
    description: '根据车牌号寻车'
  },
  {
    method: 'POST',
    endpoint: '/api/v1/parking_spaces/bind/',
    description: '用户扫码绑定车牌'
  },
  {
    method: 'POST',
    endpoint: '/api/v1/hardware/webhook/',
    description: '硬件推送的车位变化事件（传感器推送）'
  },
  {
    method: 'GET',
    endpoint: '/api/v1/parking_spaces/',
    description: '获取所有 ParkingSpace 记录'
  },
  {
    method: 'POST',
    endpoint: '/api/v1/parking/navigation/find-path/',
    description: '计算两点间的最短导航路径（Dijkstra）'
  }
]

function getMethodColor(method) {
  const colors = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger'
  }
  return colors[method] || 'info'
}
</script>

<style scoped lang="scss">
.map-integration-page {
  min-height: 100vh;
  background: #f5f7fa;

  .tabs-header {
    margin: 0;
    border-radius: 0;

    :deep(.el-tabs__header) {
      background: white;
      border-bottom: 2px solid #dcdfe6;
      margin: 0;
    }
  }

  .tabs-content {
    padding: 20px;

    .tab-pane {
      background: white;
      border-radius: 4px;
      min-height: 500px;
    }

    .guide-pane {
      padding: 30px;
      max-width: 1000px;

      h2 {
        margin-top: 0;
        color: #303133;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
      }

      .guide-section {
        margin: 30px 0;

        h3 {
          color: #606266;
          border-left: 4px solid #667eea;
          padding-left: 10px;
          margin-top: 20px;
        }

        .architecture-diagram {
          display: flex;
          align-items: center;
          gap: 20px;
          margin: 20px 0;
          padding: 20px;
          background: #f5f7fa;
          border-radius: 8px;

          .arch-box {
            flex: 1;
            padding: 15px;
            background: white;
            border: 2px solid #667eea;
            border-radius: 6px;
            text-align: center;

            strong {
              display: block;
              margin-bottom: 8px;
              color: #303133;
            }

            p {
              margin: 0;
              font-size: 12px;
              color: #909399;
            }
          }

          .arrow {
            font-size: 24px;
            color: #667eea;
            flex-shrink: 0;
          }
        }

        .feature-card {
          margin: 15px 0;
          padding: 15px;
          background: #f9f9f9;
          border-left: 3px solid #667eea;
          border-radius: 4px;

          h4 {
            margin-top: 0;
            color: #303133;
          }

          p {
            margin: 10px 0;
            color: #606266;
            line-height: 1.6;
          }

          ol, ul {
            margin: 10px 0;
            padding-left: 20px;
            color: #606266;

            li {
              line-height: 1.8;
              margin-bottom: 6px;
            }
          }

          code {
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
            color: #d63384;
          }
        }

        .model-diagram {
          background: white;
          border: 1px solid #dcdfe6;
          border-radius: 6px;
          overflow: hidden;

          .model-field {
            display: grid;
            grid-template-columns: 150px 120px 1fr;
            gap: 15px;
            padding: 12px 15px;
            border-bottom: 1px solid #ebeef5;
            align-items: center;

            &:last-child {
              border-bottom: none;
            }

            .field-name {
              font-weight: 600;
              color: #303133;
              font-family: monospace;
            }

            .field-type {
              background: #f0f9ff;
              color: #0ea5e9;
              padding: 4px 8px;
              border-radius: 3px;
              font-size: 12px;
              text-align: center;
              font-family: monospace;
            }

            .field-desc {
              color: #909399;
              font-size: 13px;
            }
          }
        }

        .quickstart-steps {
          display: grid;
          gap: 15px;
          margin: 20px 0;

          .step {
            display: flex;
            gap: 15px;
            padding: 15px;
            background: #f5f7fa;
            border-radius: 6px;
            border-left: 4px solid #667eea;

            .step-number {
              display: flex;
              align-items: center;
              justify-content: center;
              width: 40px;
              height: 40px;
              background: #667eea;
              color: white;
              border-radius: 50%;
              font-weight: 700;
              flex-shrink: 0;
            }

            .step-content {
              flex: 1;

              strong {
                display: block;
                color: #303133;
                margin-bottom: 5px;
              }

              p {
                margin: 0;
                font-size: 13px;
                color: #606266;
                line-height: 1.6;
              }

              code {
                background: #f0f0f0;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
                color: #d63384;
              }
            }
          }
        }

        :deep(.el-collapse-item__header) {
          font-weight: 600;
          color: #303133;
        }

        :deep(.el-collapse-item__body) {
          padding: 20px;

          p, ul, ol {
            margin: 10px 0;
            color: #606266;
            line-height: 1.8;
          }

          ul, ol {
            padding-left: 20px;
          }
        }
      }
    }
  }
}
</style>
