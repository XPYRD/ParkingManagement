<template>
  <!-- 首页 — 从 stitch_/_1/code.html 转换 -->
  <div class="pb-8">
    <!-- ===== Hero Section ===== -->
    <section
      class="relative px-6 md:px-10 pt-8 pb-32 md:pb-24 bg-cover bg-center min-h-[420px] flex items-end rounded-b-3xl overflow-hidden mx-4 mt-2"
      :style="{ backgroundImage: `url(${heroImage})` }"
    >
      <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent"></div>
      <div class="relative z-10 max-w-2xl">
        <p class="text-white/70 text-sm font-bold uppercase tracking-[0.2em] mb-4">智能停车系统</p>
        <h1 class="text-4xl md:text-5xl font-extrabold text-white font-headline leading-tight tracking-tight mb-4">
          城市流动的<br/>智慧脉搏
        </h1>
        <p class="text-white/70 text-sm max-w-md leading-relaxed mb-6">
          体验下一代 AI 驱动的停车管理——实时监控每一个车位、预测流量峰值、优化空间利用率。
        </p>
        <div class="flex gap-3">
          <router-link to="/map">
            <el-button type="primary" size="large" class="!rounded-full !px-6 !font-bold !shadow-lg">
              查看实时车位
            </el-button>
          </router-link>
          <router-link to="/reserve">
            <el-button size="large" class="!rounded-full !px-6 !font-bold !bg-white/15 !backdrop-blur-md !text-white !border-white/20 hover:!bg-white/25">
              预约停车
            </el-button>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ===== 实时统计 Bento 网格 ===== -->
    <section class="px-6 md:px-10 -mt-16 relative z-20 max-w-7xl mx-auto">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div
          v-for="stat in statsCards"
          :key="stat.label"
          class="glass-panel rounded-2xl p-5 shadow-lg border border-white/30 hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300"
        >
          <div class="flex items-center gap-2 mb-3">
            <span class="material-symbols-outlined text-primary text-xl">{{ stat.icon }}</span>
            <span class="text-xs font-bold text-secondary uppercase tracking-widest">{{ stat.label }}</span>
          </div>
          <p class="text-3xl font-extrabold text-on-surface font-headline tracking-tight">{{ stat.value }}</p>
          <p class="text-xs text-secondary mt-1">{{ stat.desc }}</p>
        </div>
      </div>
    </section>

    <!-- ===== 免登录快速缴费（大区块） ===== -->
    <section class="px-6 md:px-10 mt-12 max-w-7xl mx-auto">
      <div class="rounded-3xl overflow-hidden shadow-2xl border border-primary/10 bg-gradient-to-br from-[#0b3a6f] via-[#0f5ca8] to-[#27a2b8]">
        <div class="grid grid-cols-1 lg:grid-cols-2">
          <div class="p-8 md:p-12 text-white relative">
            <div class="absolute right-6 top-6 text-xs font-black tracking-widest px-3 py-1 rounded-full bg-white/20">免登录</div>
            <p class="text-white/70 text-xs font-bold tracking-[0.18em] uppercase mb-4">Quick Pay Express</p>
            <h2 class="text-3xl md:text-4xl font-black leading-tight font-headline mb-4">快速缴费通道</h2>
            <p class="text-white/85 text-sm md:text-base leading-relaxed max-w-lg">
              车主无需登录，输入车牌即可快速发起缴费。支持微信、支付宝、银行卡扫码支付。
            </p>
            <div class="mt-8 flex flex-wrap gap-3 text-xs">
              <span class="px-3 py-1 rounded-full bg-white/15">无需账号</span>
              <span class="px-3 py-1 rounded-full bg-white/15">30秒完成</span>
              <span class="px-3 py-1 rounded-full bg-white/15">安全支付</span>
            </div>
          </div>

          <div class="p-8 md:p-10 bg-white/95">
            <el-form label-position="top" class="space-y-3" @submit.prevent>
              <el-form-item label="车牌来源">
                <el-radio-group v-model="plateSourceMode" class="!flex gap-2 !w-full">
                  <el-radio-button label="manual" class="flex-1 text-center">手动输入</el-radio-button>
                  <el-radio-button label="my_vehicle" class="flex-1 text-center">我的车辆</el-radio-button>
                </el-radio-group>
              </el-form-item>

              <el-form-item v-if="plateSourceMode === 'my_vehicle'" label="选择我的车辆">
                <el-select
                  v-model="selectedVehicleId"
                  size="large"
                  placeholder="请选择已绑定车辆"
                  class="w-full"
                  filterable
                  clearable
                >
                  <el-option
                    v-for="car in myVehicles"
                    :key="car.id"
                    :label="car.plate_number"
                    :value="car.id"
                  />
                </el-select>
                <p v-if="!myVehicles.length" class="mt-2 text-xs text-slate-500">
                  当前账号暂无已绑定车辆，可切换到手动输入。
                </p>
              </el-form-item>

              <el-form-item label="车牌号">
                <el-input
                  v-model="quickPayForm.plate_number"
                  size="large"
                  placeholder="支持键盘输入/粘贴，或点击展开小键盘"
                  :disabled="plateSourceMode === 'my_vehicle'"
                  @click="plateSourceMode === 'manual' ? (plateKeyboardVisible = true) : null"
                  @focus="plateSourceMode === 'manual' ? (plateKeyboardVisible = true) : null"
                  @input="handleQuickPayPlateInput"
                  @paste="handleQuickPayPlatePaste"
                />
              </el-form-item>

              <div v-if="plateSourceMode === 'manual' && plateKeyboardVisible" class="rounded-2xl border border-slate-200 bg-slate-50 p-3 md:p-4">
                <div class="flex items-center justify-between mb-3">
                  <p class="text-xs font-bold tracking-widest text-slate-500">车牌小键盘</p>
                  <el-button link type="primary" @click="plateKeyboardVisible = false">收起</el-button>
                </div>

                <el-form label-position="top">
                  <el-form-item label="能源类型">
                    <el-radio-group v-model="quickPayForm.energy_type" class="!flex gap-2">
                      <el-radio-button label="ice">油车（蓝牌）</el-radio-button>
                      <el-radio-button label="new_energy">新能源（绿牌）</el-radio-button>
                    </el-radio-group>
                  </el-form-item>
                </el-form>

                <div class="max-h-[340px] overflow-y-auto pr-1">
                  <PlateNumberInput
                    v-model="quickPayForm.plate_number"
                    :energy-type="quickPayForm.energy_type"
                    @complete="handleQuickPayPlateComplete"
                  />
                </div>
              </div>

              <el-form-item>
                <el-button
                  size="large"
                  class="!w-full !h-12 !font-bold"
                  :loading="quickPayQuoteLoading"
                  @click="queryQuickPayQuote"
                >
                  查询停车时长与费用
                </el-button>
              </el-form-item>

              <div v-if="quickPayQuote" class="rounded-2xl border border-primary/20 bg-primary/5 p-4 space-y-2">
                <div class="flex justify-between text-sm text-slate-600">
                  <span>已停时长</span>
                  <span class="font-bold text-slate-800">{{ quickPayQuote.duration_text }}</span>
                </div>
                <div class="flex justify-between text-sm text-slate-600">
                  <span>计费小时</span>
                  <span class="font-bold text-slate-800">{{ quickPayQuote.chargeable_hours }} 小时</span>
                </div>
                <div class="flex justify-between text-sm text-slate-600">
                  <span>当前应缴</span>
                  <span class="font-black text-lg text-primary">¥ {{ quickPayQuote.amount }}</span>
                </div>
                <p v-if="quickPayQuote.payment_state === 'pending_exit'" class="text-xs text-green-600 font-semibold flex items-center gap-1">
                  <span class="material-symbols-outlined text-sm">check_circle</span>
                  已缴费待出场，请在30分钟内离场
                </p>
                <p v-else-if="quickPayQuote.leave_tip" class="text-xs text-amber-600 font-semibold">
                  {{ quickPayQuote.leave_tip }}
                </p>
              </div>

              <el-form-item label="支付方式">
                <el-radio-group v-model="quickPayForm.method" class="!flex gap-2 !w-full">
                  <el-radio-button label="balance" class="flex-1 text-center">
                    <span class="inline-flex items-center gap-1">
                      <span class="material-symbols-outlined text-lg">account_balance_wallet</span>
                      <span>余额</span>
                    </span>
                  </el-radio-button>
                  <el-radio-button label="wechat" class="flex-1 text-center">
                    <span class="inline-flex items-center gap-1">
                      <img src="/微信支付.svg" alt="微信支付" class="w-4 h-4 object-contain" />
                      <span>微信</span>
                    </span>
                  </el-radio-button>
                  <el-radio-button label="alipay" class="flex-1 text-center">
                    <span class="inline-flex items-center gap-1">
                      <img src="/支付宝支付.svg" alt="支付宝支付" class="w-4 h-4 object-contain" />
                      <span>支付宝</span>
                    </span>
                  </el-radio-button>
                  <el-radio-button label="card" class="flex-1 text-center">
                    <span class="inline-flex items-center gap-1">
                      <img src="/银行卡.svg" alt="银行卡支付" class="w-4 h-4 object-contain" />
                      <span>银行卡</span>
                    </span>
                  </el-radio-button>
                </el-radio-group>
                <!-- 余额未登录提示 -->
                <div v-if="quickPayForm.method === 'balance' && !authStore.isLoggedIn" class="mt-3 p-3 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <span class="material-symbols-outlined text-amber-500 text-lg">login</span>
                    <span class="text-sm text-amber-700">余额支付需要先登录</span>
                  </div>
                  <router-link to="/login" class="px-3 py-1 text-xs font-bold text-white bg-primary rounded-lg hover:bg-primary-dark transition-colors">
                    去登录
                  </router-link>
                </div>
              </el-form-item>

              <el-button
                type="primary"
                size="large"
                class="!w-full !h-12 !font-extrabold !text-base"
                :loading="quickPayLoading"
                :disabled="!quickPayQuote || Number(quickPayQuote.amount || 0) <= 0 || quickPayQuote.payment_state === 'pending_exit'"
                @click="submitQuickPay"
              >
                {{ quickPayQuote ? (quickPayQuote.payment_state === 'pending_exit' ? '已缴费待出场' : (Number(quickPayQuote.amount || 0) > 0 ? '立即支付' : '已缴费待出场')) : '请先查询' }}
              </el-button>
            </el-form>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 车辆进出场模拟控制台 ===== -->
    <section class="px-6 md:px-10 mt-8 max-w-7xl mx-auto">
      <div class="sim-console rounded-3xl border border-slate-700/60 p-6 md:p-8 relative overflow-hidden">
        <!-- 背景纹理: 网点 + 扫描线 -->
        <div class="sim-bg-dots"></div>
        <div class="sim-bg-scan"></div>

        <!-- 顶部状态栏 -->
        <div class="relative z-10 flex flex-wrap items-center gap-x-6 gap-y-2 mb-8">
          <div class="flex items-center gap-2.5">
            <span class="sim-status-dot"></span>
            <h2 class="text-base font-bold text-slate-200 tracking-wider">进出场模拟控制台</h2>
          </div>
          <div class="hidden sm:block h-4 w-px bg-slate-600/60"></div>
          <span class="text-[11px] text-slate-500 font-mono tracking-[0.15em] uppercase">Simulation Console</span>
          <div class="hidden sm:block flex-1"></div>
          <span class="text-[10px] text-slate-600 font-mono tracking-wider">SYS {{ new Date().toLocaleTimeString('zh-CN', {hour:'2-digit',minute:'2-digit',second:'2-digit'}) }}</span>
        </div>

        <!-- 模式切换开关 -->
        <div class="relative z-10 flex bg-slate-800/70 rounded-xl p-1 mb-8 border border-slate-700/40">
          <button
            class="flex-1 py-3 px-4 rounded-[10px] text-sm font-bold tracking-wide transition-all duration-300"
            :class="simulationTab === 'entry' ? 'bg-amber-500/15 text-amber-300 shadow-[0_0_12px_rgba(251,191,36,0.15)]' : 'text-slate-500 hover:text-slate-300'"
            @click="simulationTab = 'entry'"
          >
            <span class="inline-flex items-center gap-2">
              <span class="text-lg leading-none">↓</span>
              <span>进场模式</span>
            </span>
          </button>
          <button
            class="flex-1 py-3 px-4 rounded-[10px] text-sm font-bold tracking-wide transition-all duration-300"
            :class="simulationTab === 'exit' ? 'bg-cyan-500/15 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.15)]' : 'text-slate-500 hover:text-slate-300'"
            :disabled="!quickPayQuote || quickPayQuote.found !== true"
            @click="simulationTab = 'exit'"
          >
            <span class="inline-flex items-center gap-2">
              <span class="text-lg leading-none">↑</span>
              <span>出场模式</span>
            </span>
          </button>
        </div>

        <!-- ==================== 进场模式 ==================== -->
        <div v-show="simulationTab === 'entry'" class="relative z-10 space-y-6">
          <!-- 数据源选择: 三态按钮组 -->
          <div>
            <label class="block text-[11px] text-slate-500 font-mono tracking-[0.12em] uppercase mb-3">数据来源</label>
            <div class="flex bg-slate-800/50 rounded-lg p-1 border border-slate-700/30">
              <button
                v-for="src in [{k:'manual',l:'⌨ 手动'},{k:'my_vehicle',l:'🚗 车辆'},{k:'image',l:'📷 识别'}]"
                :key="src.k"
                class="flex-1 py-2 text-xs font-bold rounded-md transition-all duration-200"
                :class="entryPlateSourceMode === src.k ? 'bg-slate-700 text-slate-100 shadow-sm' : 'text-slate-500 hover:text-slate-300'"
                @click="entryPlateSourceMode = src.k"
              >{{ src.l }}</button>
            </div>
          </div>

          <!-- 绑定车辆选择 -->
          <div v-if="entryPlateSourceMode === 'my_vehicle'" class="animate-[fadeIn_0.2s_ease-out]">
            <label class="block text-[11px] text-slate-500 font-mono tracking-[0.12em] uppercase mb-2">选择车辆</label>
            <el-select
              v-model="entryVehicleId"
              placeholder="选择已绑定车辆..."
              class="sim-select w-full"
              filterable clearable
              popper-class="sim-select-dropdown"
            >
              <el-option v-for="car in myVehicles" :key="car.id" :label="car.plate_number" :value="car.id" />
            </el-select>
          </div>

          <!-- 图片上传识别 -->
          <div v-if="entryPlateSourceMode === 'image'" class="animate-[fadeIn_0.2s_ease-out]">
            <label class="block text-[11px] text-slate-500 font-mono tracking-[0.12em] uppercase mb-2">图片识别</label>
            <div class="flex flex-wrap items-center gap-3">
              <label class="sim-file-btn">
                <span class="material-symbols-outlined text-sm mr-1">folder_open</span>
                选择图片
                <input type="file" accept="image/*" class="hidden" @change="handleEntryImageChange" />
              </label>
              <button class="sim-action-btn" :disabled="!entryImageName" :class="{ 'sim-loading': entryRecognitionLoading }" @click="recognizeEntryPlateFromImage">
                <span class="material-symbols-outlined text-sm mr-1">smart_toy</span>
                {{ entryRecognitionLoading ? '识别中...' : '识别车牌' }}
              </button>
              <span v-if="entryImageName" class="text-[11px] text-slate-400 font-mono truncate max-w-[160px]">{{ entryImageName }}</span>
            </div>
          </div>

          <!-- 核心参数区: 车牌号 + 楼层 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-[11px] text-slate-500 font-mono tracking-[0.12em] uppercase mb-2">车牌号码</label>
              <div class="sim-plate-display" :class="{ 'sim-plate-locked': entryPlateSourceMode === 'my_vehicle' }">
                <input
                  v-model="entrySimulationPlate"
                  type="text"
                  :placeholder="entryPlateSourceMode === 'my_vehicle' ? '选择车辆后自动填入' : '输入车牌号...'"
                  :disabled="entryPlateSourceMode === 'my_vehicle'"
                  class="sim-plate-input"
                  @input="handleEntrySimulationPlateInput"
                />
              </div>
            </div>
            <div>
              <label class="block text-[11px] text-slate-500 font-mono tracking-[0.12em] uppercase mb-2">目标楼层</label>
              <div class="sim-floor-selector">
                <button
                  v-for="f in [{k:'B2',l:'B2'},{k:'B1',l:'B1'},{k:'1F',l:'1F'}]"
                  :key="f.k"
                  class="sim-floor-btn"
                  :class="{ 'sim-floor-active': entrySimulationFloor === f.k }"
                  @click="entrySimulationFloor = f.k"
                >{{ f.l }}</button>
              </div>
            </div>
          </div>

          <!-- 执行按钮 -->
          <div class="flex items-end gap-4">
            <button
              class="sim-launch-btn"
              :class="{ 'sim-launch-loading': markEntryLoading }"
              :disabled="markEntryLoading"
              @click="simulateVehicleEntry"
            >
              <span class="sim-launch-ring"></span>
              <span class="relative z-10 inline-flex items-center gap-2 text-sm font-extrabold tracking-wider">
                <span v-if="!markEntryLoading" class="text-lg">▶</span>
                <span v-else class="sim-spinner"></span>
                {{ markEntryLoading ? '分配车位中...' : '执行进场' }}
              </span>
            </button>
            <span class="text-[10px] text-slate-600 font-mono tracking-wider pb-1">系统将自动分配可用车位</span>
          </div>
        </div>

        <!-- ==================== 出场模式 ==================== -->
        <div v-show="simulationTab === 'exit'" class="relative z-10 space-y-6">
          <!-- 在场状态指示 -->
          <div class="flex items-center gap-4 p-4 rounded-xl bg-slate-800/40 border border-slate-700/30">
            <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0"
              :class="quickPayQuote?.found ? 'bg-cyan-500/10' : 'bg-slate-700/50'">
              <span class="material-symbols-outlined text-xl"
                :class="quickPayQuote?.found ? 'text-cyan-400' : 'text-slate-500'">
                {{ quickPayQuote?.found ? 'directions_car' : 'block' }}
              </span>
            </div>
            <div>
              <p class="text-sm font-bold" :class="quickPayQuote?.found ? 'text-slate-200' : 'text-slate-500'">
                {{ quickPayQuote?.found ? '车辆在场，可以出场' : '无在场记录' }}
              </p>
              <p class="text-[11px] text-slate-500 font-mono tracking-wider mt-0.5">
                {{ quickPayQuote?.found ? '需先在上方快速缴费通道查询并支付后执行出场' : '请先在快速缴费通道查询停车记录' }}
              </p>
            </div>
            <div class="flex-1 hidden sm:block"></div>
            <div v-if="quickPayQuote?.found" class="text-right flex-shrink-0">
              <p class="text-[10px] text-slate-500 font-mono tracking-wider uppercase">已停时长</p>
              <p class="text-lg font-black text-slate-200 font-mono">{{ quickPayQuote.duration_text }}</p>
            </div>
          </div>

          <!-- 出场按钮 -->
          <div class="flex items-end gap-4">
            <button
              class="sim-launch-btn sim-launch-exit"
              :class="{ 'sim-launch-loading': markExitLoading }"
              :disabled="!quickPayQuote || quickPayQuote.found !== true || markExitLoading"
              @click="simulateVehicleExit"
            >
              <span class="sim-launch-ring"></span>
              <span class="relative z-10 inline-flex items-center gap-2 text-sm font-extrabold tracking-wider">
                <span v-if="!markExitLoading" class="text-lg">▲</span>
                <span v-else class="sim-spinner"></span>
                {{ markExitLoading ? '执行出场...' : '执行出场' }}
              </span>
            </button>
            <span v-if="quickPayQuote?.found" class="text-[10px] text-slate-600 font-mono tracking-wider pb-1">释放车位并结算费用</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 快速操作 ===== -->
    <section class="px-6 md:px-10 mt-12 max-w-7xl mx-auto">
      <h2 class="text-lg font-bold text-on-surface tracking-tight mb-6 font-headline">快速操作</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <router-link
          v-for="action in quickActions"
          :key="action.path"
          :to="action.path"
          class="group flex flex-col items-center gap-3 p-6 rounded-2xl bg-surface-container-low hover:bg-primary hover:text-white transition-all duration-300 cursor-pointer shadow-sm hover:shadow-lg hover:-translate-y-1"
        >
          <span class="material-symbols-outlined text-3xl text-primary group-hover:text-white transition-colors">{{ action.icon }}</span>
          <span class="text-sm font-bold group-hover:text-white transition-colors">{{ action.label }}</span>
          <span class="text-xs text-secondary group-hover:text-white/70 transition-colors text-center">{{ action.desc }}</span>
        </router-link>
      </div>
    </section>

    <!-- ===== 停车场状态预览 ===== -->
    <section class="px-6 md:px-10 mt-12 max-w-7xl mx-auto">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-lg font-bold text-on-surface tracking-tight font-headline">停车场状态</h2>
        <router-link to="/map" class="text-sm text-primary font-semibold hover:underline">查看详细地图 →</router-link>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          v-for="floor in floorPreview"
          :key="floor.name"
          class="rounded-2xl p-6 bg-surface-container-low border border-outline-variant/10 hover:shadow-md transition-shadow"
        >
          <div class="flex justify-between items-center mb-4">
            <h3 class="font-bold text-on-surface">{{ floor.name }}</h3>
            <span
              class="text-xs font-bold px-3 py-1 rounded-full"
              :class="floor.rate > 90 ? 'bg-error/10 text-error' : floor.rate > 70 ? 'bg-amber-50 text-amber-600' : 'bg-green-50 text-green-600'"
            >
              {{ floor.rate }}% 占用
            </span>
          </div>
          <!-- 占用率进度条 -->
          <div class="w-full h-2.5 bg-surface-container-highest rounded-full overflow-hidden">
            <div
              class="h-full rounded-full transition-all duration-700"
              :class="floor.rate > 90 ? 'bg-error' : floor.rate > 70 ? 'bg-amber-500' : 'bg-green-500'"
              :style="{ width: `${floor.rate}%` }"
            ></div>
          </div>
          <div class="flex justify-between mt-3 text-xs text-secondary">
            <span>空闲 {{ floor.free }} 个</span>
            <span>总计 {{ floor.total }} 个</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 联系信息 ===== -->
    <section class="px-6 md:px-10 mt-12 max-w-7xl mx-auto">
      <div class="rounded-2xl bg-primary p-8 md:p-12 text-white">
        <h2 class="text-2xl font-extrabold font-headline tracking-tight mb-2">需要帮助？</h2>
        <p class="text-white/70 text-sm mb-6 max-w-md">24小时客户服务热线已为您准备就绪。我们的专业团队随时解答您的停车问题。</p>
        <div class="flex flex-wrap gap-6">
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-white/70">call</span>
            <span class="font-bold">400-888-0000</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-white/70">mail</span>
            <span class="font-bold">support@sentinel.com</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-white/70">location_on</span>
            <span class="font-bold">北京市朝阳区科技路88号</span>
          </div>
        </div>
      </div>
    </section>
    <el-dialog v-model="quickPayDialogVisible" title="请扫码完成支付" width="92%" max-width="460px">
      <div class="text-center">
        <img :src="quickPayResult.qr_code_url" alt="快速缴费二维码" class="w-56 h-56 mx-auto rounded-xl border border-slate-200" />
        <p class="mt-4 text-sm text-slate-700">车牌：{{ quickPayResult.plate_number }}</p>
        <p class="mt-1 text-lg font-black text-primary">¥ {{ quickPayResult.amount }}</p>
        <p class="mt-2 text-xs text-slate-500">交易号：{{ quickPayResult.transaction_id }}</p>
      </div>
      <template #footer>
        <div class="w-full space-y-3">
          <div class="p-3 rounded-lg bg-amber-50 border border-amber-200 flex items-center gap-2">
            <span class="material-symbols-outlined text-amber-500 text-lg">schedule</span>
            <span class="text-sm text-amber-700 font-bold">请在30分钟内离场，超过需重新缴费</span>
          </div>
          <el-button type="primary" @click="confirmQuickPayPaid">我已支付（模拟）</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 银行卡选择弹窗 -->
    <el-dialog v-model="bankCardDialogVisible" title="选择银行卡" width="92%" max-width="400px">
      <div v-if="loadingBankCards" class="text-center py-4">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p class="text-sm text-slate-500 mt-2">加载中…</p>
      </div>
      <div v-else-if="bankCards.length === 0" class="text-center py-4">
        <span class="material-symbols-outlined text-4xl text-amber-400">credit_card_off</span>
        <p class="text-sm text-slate-600 mt-2">暂未添加银行卡</p>
        <router-link to="/payment" class="mt-3 inline-block px-4 py-2 text-sm font-bold text-white bg-primary rounded-lg hover:bg-primary-dark transition-colors">
          + 添加银行卡
        </router-link>
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="card in bankCards"
          :key="card.id"
          class="flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-colors"
          :class="quickPayForm.selectedBankCardId === card.id ? 'border-primary bg-primary/5' : 'border-slate-200 hover:border-primary/50'"
          @click="quickPayForm.selectedBankCardId = card.id"
        >
          <div class="flex items-center gap-3">
            <span class="material-symbols-outlined text-primary text-xl">credit_card</span>
            <div>
              <p class="text-sm font-bold text-slate-800">{{ card.bank_name }}</p>
              <p class="text-xs text-slate-500">{{ card.card_type || '储蓄卡' }} *{{ card.card_last4 }}</p>
            </div>
          </div>
          <span v-if="quickPayForm.selectedBankCardId === card.id" class="material-symbols-outlined text-primary">check_circle</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="bankCardDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBankCardAndPay">确认支付</el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
/**
 * 首页 — 接入实际 API 数据
 */

import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { getParkingSpaceStatistics, getSpacesByFloor, sendWebhookEvent, recognizePlateFromImage } from '@/api/parking'
import { quickPayNoLogin, quickPayQuoteNoLogin, quickPayMarkExit, quickPayByPlate, quickPayMarkExitByPlate, confirmQuickPay, getBankCards } from '@/api/payment'
import { getVehicles } from '@/api/user'
import PlateNumberInput from '@/components/PlateNumberInput.vue'
import heroImage from '@/assets/images/hero_bg.png'
import { getDefaultPaymentMethod } from '@/utils/paymentPreference'
import { useAuthStore } from '@/stores/auth'

import { usePlateStore } from '@/stores/plate'
/** 实时统计卡片 */
const statsCards = ref([
  { icon: 'local_parking', label: '可用车位', value: '--', desc: '实时更新' },
  { icon: 'directions_car', label: '在场车辆', value: '--', desc: '总占有' },
  { icon: 'event_available', label: '已预约', value: '--', desc: '预约锁定' },
  { icon: 'build', label: '维修中', value: '--', desc: '暂不可用' },
])

const quickActions = [
  { path: '/map', icon: 'map', label: '查看地图', desc: '实时车位状态' },
  { path: '/map', icon: 'search', label: '车牌找车位', desc: '地图页顶部直接搜索' },
  { path: '/reserve', icon: 'event', label: '预约车位', desc: '提前锁定位置' },
  { path: '/payment', icon: 'credit_card', label: '在线支付', desc: '快速缴费离场' },
]

const floorPreview = ref([])
let refreshTimer = null
const plateStore = usePlateStore()
const authStore = useAuthStore()

const quickPayLoading = ref(false)
const markEntryLoading = ref(false)
const markExitLoading = ref(false)
const quickPayQuoteLoading = ref(false)
const quickPayDialogVisible = ref(false)
const bankCardDialogVisible = ref(false)
const plateKeyboardVisible = ref(false)
const simulationTab = ref('entry')
const plateSourceMode = ref('manual')
const myVehicles = ref([])
const selectedVehicleId = ref(null)
const entryPlateSourceMode = ref('manual')
const entryVehicleId = ref(null)
const entrySimulationPlate = ref('')
const entrySimulationFloor = ref('B2')
const entryImageFile = ref(null)
const entryImageName = ref('')
const entryRecognitionLoading = ref(false)
const quickPayForm = ref({
  plate_number: '',
  energy_type: 'ice',
  method: 'wechat',
  selectedBankCardId: null,
})
const bankCards = ref([])
const loadingBankCards = ref(false)

async function loadBankCards() {
  if (!authStore.isLoggedIn) return
  loadingBankCards.value = true
  try {
    const res = await getBankCards()
    // DRF paginated response: { count, results: [...] }
    // or flat array, or { data: [...] }
    const list = Array.isArray(res?.results) ? res.results
      : Array.isArray(res) ? res
      : Array.isArray(res?.data) ? res.data
      : []
    bankCards.value = list
    if (bankCards.value.length > 0 && !quickPayForm.value.selectedBankCardId) {
      quickPayForm.value.selectedBankCardId = bankCards.value[0].id
    }
  } catch (err) {
    console.error('加载银行卡失败', err)
  } finally {
    loadingBankCards.value = false
  }
}
const quickPayQuote = ref(null)
const quickPayResult = ref({
  qr_code_url: '',
  plate_number: '',
  amount: '0.00',
  transaction_id: '',
})

async function submitQuickPay() {
  if (!quickPayQuote.value) {
    ElMessage.warning('请先查询停车费用')
    return
  }

  const plate = getCurrentPlateNumber()
  if (!plate) {
    ElMessage.warning('请输入车牌号')
    return
  }

  if (quickPayForm.value.method === 'balance' && !authStore.isLoggedIn) {
    ElMessage.warning('余额支付需要先登录')
    return
  }

  // 银行卡：弹出选择弹窗
  if (quickPayForm.value.method === 'card') {
    if (!authStore.isLoggedIn) {
      ElMessage.warning('银行卡支付需要先登录')
      return
    }
    // 加载银行卡列表
    if (bankCards.value.length === 0) {
      await loadBankCards()
    }
    if (bankCards.value.length === 0) {
      ElMessage.warning('请先前往支付中心添加银行卡')
      return
    }
    // 默认选中第一张
    if (!quickPayForm.value.selectedBankCardId) {
      quickPayForm.value.selectedBankCardId = bankCards.value[0].id
    }
    bankCardDialogVisible.value = true
    return
  }

  // 其他支付方式：直接发起
  await proceedPayment(plate)
}

/** 银行卡弹窗确认后执行支付 */
async function confirmBankCardAndPay() {
  if (!quickPayForm.value.selectedBankCardId) {
    ElMessage.warning('请选择一张银行卡')
    return
  }
  bankCardDialogVisible.value = false
  const plate = getCurrentPlateNumber()
  await proceedPayment(plate)
}

/** 执行支付请求 */
async function proceedPayment(plate) {
  quickPayLoading.value = true
  try {
    const res = quickPayQuote.value.session_id
      ? await quickPayNoLogin(
          plate,
          quickPayQuote.value.amount,
          quickPayForm.value.method,
          quickPayQuote.value.session_id,
        )
      : await quickPayByPlate(
          plate,
          quickPayQuote.value.amount,
          quickPayForm.value.method,
        )

    if (res?.payment_state === 'subscription_free') {
      ElMessage.success(res?.leave_tip || '当前订阅有效，车辆进出场免费，无需支付')
      quickPayDialogVisible.value = false
      await queryQuickPayQuote(false)
      return
    }

    // 余额支付直接成功，无需扫码确认
    if (res?.payment_state === 'paid') {
      ElMessage.success('余额支付成功，请在30分钟内离场')
      await queryQuickPayQuote(false)
      return
    }

    quickPayResult.value = {
      qr_code_url: res?.qr_code_url || '',
      plate_number: res?.plate_number || plate,
      amount: res?.amount || String(quickPayQuote.value.amount),
      transaction_id: res?.transaction_id || '',
    }
    quickPayDialogVisible.value = true
  } catch (err) {
    console.error('快速缴费失败', err)
  } finally {
    quickPayLoading.value = false
  }
}

async function simulateVehicleExit() {
  if (!quickPayQuote.value?.found) {
    ElMessage.warning('请先查询在场车辆')
    return
  }

  const plate = getCurrentPlateNumber()
  markExitLoading.value = true
  try {
    if (quickPayQuote.value.session_id) {
      await quickPayMarkExit(plate, quickPayQuote.value.session_id)
    } else {
      await quickPayMarkExitByPlate(plate)
    }
    ElMessage.success('已模拟车辆出场')
    quickPayQuote.value = null
    await queryQuickPayQuote(false)
  } catch (err) {
    console.error('模拟出场失败', err)
    const backendMessage = err?.response?.data?.detail || '模拟出场失败'
    ElMessage.error(backendMessage)
  } finally {
    markExitLoading.value = false
  }
}

function isSpotAvailableForEntry(spot) {
  const isDamaged = Boolean(spot?.is_damaged)
  const isReserved = Boolean(String(spot?.reserved_plate || '').trim())
  const hasCurrentPlate = Boolean(String(spot?.current_plate || '').trim())
  return !isDamaged && !isReserved && !hasCurrentPlate
}

async function pickRandomAvailableSpot(preferredFloor = '') {
  const floors = preferredFloor ? [preferredFloor] : ['B2', 'B1', '1F']

  for (const floor of floors) {
    const res = await getSpacesByFloor(floor)
    const rows = Array.isArray(res?.data) ? res.data : (Array.isArray(res) ? res : [])
    const candidates = rows.filter(isSpotAvailableForEntry)
    if (candidates.length > 0) {
      const randomIndex = Math.floor(Math.random() * candidates.length)
      return candidates[randomIndex]
    }
  }

  return null
}

function normalizePlate(value) {
  return String(value || '').toUpperCase().replace(/\s+/g, '').trim()
}

function handleEntrySimulationPlateInput(value) {
  entrySimulationPlate.value = normalizePlate(value)
}

function getEntrySimulationPlate() {
  if (entryPlateSourceMode.value === 'my_vehicle') {
    const selectedVehicle = myVehicles.value.find((car) => Number(car.id) === Number(entryVehicleId.value))
    return normalizePlate(selectedVehicle?.plate_number || '')
  }
  return normalizePlate(entrySimulationPlate.value)
}

function handleEntryImageChange(event) {
  const file = event?.target?.files?.[0]
  if (!file) {
    entryImageFile.value = null
    entryImageName.value = ''
    return
  }
  entryImageFile.value = file
  entryImageName.value = file.name
}

function extractPlateFromRecognizeResult(res) {
  const candidates = [
    res?.plate_number,
    res?.license_plate,
    res?.data?.plate_number,
    res?.data?.license_plate,
    Array.isArray(res?.results) && res.results.length ? res.results[0]?.plate_number : '',
    Array.isArray(res?.detections) && res.detections.length ? res.detections[0]?.plate_number : '',
  ]
  const matched = candidates.find((item) => normalizePlate(item))
  return normalizePlate(matched || '')
}

async function recognizeEntryPlateFromImage() {
  if (entryPlateSourceMode.value !== 'image') {
    ElMessage.warning('请切换到上传识别模式')
    return
  }
  if (!entryImageFile.value) {
    ElMessage.warning('请先选择图片')
    return
  }

  entryRecognitionLoading.value = true
  try {
    const res = await recognizePlateFromImage(entryImageFile.value, 'entry')
    const plate = extractPlateFromRecognizeResult(res)
    if (!plate) {
      ElMessage.warning('未识别到车牌，请重试或手动输入')
      return
    }
    entrySimulationPlate.value = plate
    ElMessage.success(`识别成功：${plate}`)
  } catch (err) {
    console.error('图片识别失败', err)
    ElMessage.error('图片识别失败，请稍后重试')
  } finally {
    entryRecognitionLoading.value = false
  }
}

async function simulateVehicleEntry() {
  const plate = getEntrySimulationPlate()
  if (!plate) {
    ElMessage.warning('请先选择或输入车牌号')
    return
  }

  markEntryLoading.value = true
  try {
    // 检查车辆是否已在场：by-plate 返回 200 且 found=true 表示已在场，404/400 表示未在场
    let alreadyInLot = false
    try {
      const quote = await quickPayQuoteNoLogin(plate)
      if (quote?.found === true) {
        alreadyInLot = true
        quickPayQuote.value = {
          session_id: quote.session_id,
          duration_text: quote.duration_text || '--',
          chargeable_hours: quote.chargeable_hours ?? 0,
          amount: quote.amount || '0.00',
          payment_state: quote.payment_state || 'charging',
          leave_tip: quote.leave_tip || '',
        }
      }
    } catch (quoteErr) {
      const code = Number(quoteErr?.response?.status || 0)
      if (![400, 404].includes(code)) {
        throw quoteErr
      }
      // 404/400 = 车辆未在场，继续执行入场
    }

    if (alreadyInLot) {
      ElMessage.warning('该车辆已在场，无需重复入场')
      return
    }

    const targetSpot = await pickRandomAvailableSpot(entrySimulationFloor.value)
    if (!targetSpot?.space_id) {
      ElMessage.error(`所选楼层 ${entrySimulationFloor.value} 无可用车位，无法模拟入场`)
      return
    }

    await sendWebhookEvent({
      event_type: 'space_occupied',
      space_id: targetSpot.space_id,
      plate_number: plate,
      timestamp: new Date().toISOString(),
    })

    const displaySpotId = String(targetSpot.space_id || '').replace(/^space_/, '')
    const displayFloor = targetSpot.floor || entrySimulationFloor.value || '--'
    ElMessage.success(`已模拟车辆入场，随机分配车位：${displayFloor}-${displaySpotId}`)

    plateSourceMode.value = 'manual'
    quickPayForm.value.plate_number = plate
    plateStore.setPlateNumber(plate)
    await Promise.all([
      loadHomeStats(),
      queryQuickPayQuote(false),
    ])
  } catch (err) {
    console.error('模拟入场失败', err)
    ElMessage.error('模拟入场失败，请稍后重试')
  } finally {
    markEntryLoading.value = false
  }
}

async function confirmQuickPayPaid() {
  const plate = getCurrentPlateNumber()
  try {
    await confirmQuickPay(quickPayQuote.value?.session_id, plate)
    quickPayDialogVisible.value = false
    ElMessage.success('已模拟扫码支付成功，请在30分钟内离场')
    await queryQuickPayQuote(false)
  } catch (err) {
    console.error('确认支付失败', err)
    ElMessage.error('确认支付失败，请重试')
  }
}

async function queryQuickPayQuote(showToast = true) {
  const plate = getCurrentPlateNumber()
  if (!plate) {
    ElMessage.warning('请输入车牌号')
    return
  }

  quickPayQuoteLoading.value = true
  quickPayQuote.value = null
  try {
    const res = await quickPayQuoteNoLogin(plate)
    if (res?.found === false) {
      if (showToast) {
        ElMessage.warning(res?.detail || '未找到该车牌在场停车记录')
      }
      return
    }

    quickPayQuote.value = {
      found: true,
      session_id: res?.session_id,
      duration_text: res?.duration_text || '--',
      chargeable_hours: res?.chargeable_hours ?? 0,
      amount: res?.amount || '0.00',
      payment_state: res?.payment_state || 'charging',
      leave_tip: res?.leave_tip || '',
    }
    if (showToast) {
      ElMessage.success('已查询到当前停车费用')
    }
  } catch (err) {
    const code = Number(err?.response?.status || 0)
    if (code !== 404) {
      console.error('查询停车费用失败', err)
    }
    // 404 = 车辆不在场（已出场或未入场），属于正常状态
  } finally {
    quickPayQuoteLoading.value = false
  }
}

async function handleQuickPayPlateComplete(plateNumber) {
  quickPayForm.value.plate_number = String(plateNumber || '').trim().toUpperCase()
  plateStore.setPlateNumber(quickPayForm.value.plate_number)
  plateKeyboardVisible.value = false
  await queryQuickPayQuote(false)
}

function getCurrentPlateNumber() {
  const selectedVehicle = myVehicles.value.find((car) => Number(car.id) === Number(selectedVehicleId.value))
  if (plateSourceMode.value === 'my_vehicle' && selectedVehicle?.plate_number) {
    const normalized = String(selectedVehicle.plate_number).trim().toUpperCase()
    quickPayForm.value.plate_number = normalized
    return normalized
  }

  return String(quickPayForm.value.plate_number || '').trim().toUpperCase()
}

function handleQuickPayPlateInput(value) {
  const normalized = String(value || '').toUpperCase().replace(/\s+/g, '')
  quickPayForm.value.plate_number = normalized
  plateStore.setPlateNumber(normalized)
}

function handleQuickPayPlatePaste(event) {
  event?.preventDefault?.()
  const pasted = event?.clipboardData?.getData('text') || ''
  if (!pasted) {
    return
  }
  const normalized = String(pasted).toUpperCase().replace(/\s+/g, '')
  quickPayForm.value.plate_number = normalized
  plateStore.setPlateNumber(normalized)
}

async function loadHomeStats() {
  try {
    const res = await getParkingSpaceStatistics()
    const floorStats = res?.data || {}

    const mapped = Object.entries(floorStats).map(([floor, stat]) => {
      const total = Number(stat.total || 0)
      const occupied = Number(stat.occupied || 0)
      const free = Number(stat.free_regular || 0) + Number(stat.free_charging || 0)
      const rate = total > 0 ? Math.round((occupied / total) * 100) : 0

      return {
        name: floor === '1F' ? '地面层 (1F)' : `地下一层 (${floor})`,
        rate,
        free,
        total,
      }
    })
    floorPreview.value = mapped

    let totalFree = 0
    let totalOccupied = 0
    let totalReserved = 0
    let totalMaintenance = 0

    Object.values(floorStats).forEach((f) => {
      totalFree += Number(f.free_regular || 0) + Number(f.free_charging || 0)
      totalOccupied += Number(f.occupied || 0)
      totalReserved += Number(f.reserved || 0)
      totalMaintenance += Number(f.maintenance || 0)
    })

    statsCards.value[0].value = totalFree.toString()
    statsCards.value[1].value = totalOccupied.toString()
    statsCards.value[2].value = totalReserved.toString()
    statsCards.value[3].value = totalMaintenance.toString()
  } catch (err) {
    console.error('Failed to load floor summary', err)
  }
}

onMounted(async () => {
  const defaultMethod = getDefaultPaymentMethod('wechat')
  quickPayForm.value.method = defaultMethod
  if (plateStore.plateNumber) {
    quickPayForm.value.plate_number = plateStore.plateNumber
  }
  if (authStore.isLoggedIn) {
    try {
      const res = await getVehicles()
      myVehicles.value = Array.isArray(res?.results) ? res.results : (Array.isArray(res) ? res : [])
      if (myVehicles.value.length > 0) {
        entryVehicleId.value = myVehicles.value[0].id
      }
    } catch (err) {
      myVehicles.value = []
    }
    // 预加载银行卡列表，用于判断是否已绑定银行卡
    await loadBankCards()
  }
  await loadHomeStats()
  refreshTimer = window.setInterval(loadHomeStats, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    window.clearInterval(refreshTimer)
    refreshTimer = null
  }
})

watch(
  () => quickPayForm.value.plate_number,
  (val) => {
    if (plateSourceMode.value === 'manual') {
      plateStore.setPlateNumber(val)
    }
  },
)

watch(
  () => plateSourceMode.value,
  (mode) => {
    quickPayQuote.value = null
    if (mode === 'manual') {
      if (plateStore.plateNumber && !quickPayForm.value.plate_number) {
        quickPayForm.value.plate_number = plateStore.plateNumber
      }
      return
    }

    plateKeyboardVisible.value = false
    const selectedVehicle = myVehicles.value.find((car) => Number(car.id) === Number(selectedVehicleId.value))
    quickPayForm.value.plate_number = selectedVehicle?.plate_number
      ? String(selectedVehicle.plate_number).trim().toUpperCase()
      : ''
  },
)

watch(
  () => selectedVehicleId.value,
  (vehicleId) => {
    if (plateSourceMode.value !== 'my_vehicle') return
    const selectedVehicle = myVehicles.value.find((car) => Number(car.id) === Number(vehicleId))
    quickPayForm.value.plate_number = selectedVehicle?.plate_number
      ? String(selectedVehicle.plate_number).trim().toUpperCase()
      : ''
    quickPayQuote.value = null
  },
)

watch(
  () => plateStore.plateNumber,
  (val) => {
    if (plateSourceMode.value !== 'manual') return
    if (val !== quickPayForm.value.plate_number) {
      quickPayForm.value.plate_number = val
    }
  },
)

watch(
  () => entryPlateSourceMode.value,
  (mode) => {
    if (mode === 'my_vehicle') {
      const selectedVehicle = myVehicles.value.find((car) => Number(car.id) === Number(entryVehicleId.value))
      entrySimulationPlate.value = normalizePlate(selectedVehicle?.plate_number || '')
      return
    }
    if (mode === 'image') {
      entrySimulationPlate.value = ''
      return
    }
    if (mode === 'manual' && plateStore.plateNumber && !entrySimulationPlate.value) {
      entrySimulationPlate.value = normalizePlate(plateStore.plateNumber)
    }
  },
)

watch(
  () => entryVehicleId.value,
  (vehicleId) => {
    if (entryPlateSourceMode.value !== 'my_vehicle') return
    const selectedVehicle = myVehicles.value.find((car) => Number(car.id) === Number(vehicleId))
    entrySimulationPlate.value = normalizePlate(selectedVehicle?.plate_number || '')
  },
)

watch(
  () => quickPayForm.value.method,
  (method) => {
    if (method === 'card' && authStore.isLoggedIn && bankCards.value.length === 0) {
      loadBankCards()
    }
  },
)
</script>

<style scoped>
/* ============================================================
   车辆进出场模拟控制台 — Industrial Control-Room Aesthetic
   ============================================================ */
.sim-console {
  background: linear-gradient(160deg, #0f1923 0%, #141e2b 40%, #0d1620 100%);
}

/* 网点纹理 */
.sim-bg-dots {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background-image: radial-gradient(circle, rgba(148, 163, 184, 0.08) 1px, transparent 1px);
  background-size: 18px 18px;
}

/* 水平扫描线 */
.sim-bg-scan {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(255, 255, 255, 0.004) 2px,
    rgba(255, 255, 255, 0.004) 4px
  );
}

/* 状态指示灯 */
.sim-status-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 6px #34d399, 0 0 12px rgba(52, 211, 153, 0.4);
  animation: simPulse 2s ease-in-out infinite;
}

@keyframes simPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* 车牌显示屏 */
.sim-plate-display {
  background: #0a0f14;
  border: 1px solid rgba(100, 116, 139, 0.35);
  border-radius: 10px;
  padding: 4px;
  transition: border-color 0.3s;
}
.sim-plate-display:focus-within {
  border-color: rgba(251, 191, 36, 0.5);
  box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.08);
}
.sim-plate-locked {
  opacity: 0.5;
}

.sim-plate-input {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  padding: 10px 12px;
  font-family: 'Courier New', 'Source Code Pro', 'Consolas', monospace;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #e2e8f0;
  caret-color: #fbbf24;
}
.sim-plate-input::placeholder {
  color: #475569;
  font-weight: 400;
  font-size: 13px;
  letter-spacing: 0.03em;
}
.sim-plate-input:disabled {
  color: #64748b;
  cursor: not-allowed;
}

/* 楼层选择器 */
.sim-floor-selector {
  display: flex;
  gap: 2px;
  background: #0a0f14;
  border: 1px solid rgba(100, 116, 139, 0.35);
  border-radius: 10px;
  padding: 4px;
}
.sim-floor-btn {
  flex: 1;
  padding: 10px 0;
  border: none;
  border-radius: 7px;
  background: transparent;
  color: #64748b;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: all 0.25s;
}
.sim-floor-btn:hover {
  color: #94a3b8;
  background: rgba(255, 255, 255, 0.03);
}
.sim-floor-active {
  background: rgba(251, 191, 36, 0.12);
  color: #fbbf24;
  box-shadow: inset 0 1px 0 rgba(251, 191, 36, 0.15);
}

/* 文件上传按钮 */
.sim-file-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px dashed rgba(148, 163, 184, 0.35);
  color: #94a3b8;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.sim-file-btn:hover {
  background: rgba(255, 255, 255, 0.07);
  border-color: rgba(148, 163, 184, 0.55);
  color: #cbd5e1;
}

/* 通用次级按钮 */
.sim-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(255, 255, 255, 0.04);
  color: #94a3b8;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.sim-action-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.07);
  color: #cbd5e1;
}
.sim-action-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

/* 主执行按钮 — 进场 (amber) */
.sim-launch-btn {
  position: relative;
  padding: 14px 32px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.18) 0%, rgba(245, 158, 11, 0.08) 100%);
  color: #fbbf24;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.35s;
  border: 1px solid rgba(251, 191, 36, 0.3);
}
.sim-launch-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.28) 0%, rgba(245, 158, 11, 0.14) 100%);
  box-shadow: 0 0 24px rgba(251, 191, 36, 0.18), 0 4px 16px rgba(0, 0, 0, 0.3);
  transform: translateY(-1px);
}
.sim-launch-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* 出场按钮 (cyan) */
.sim-launch-exit {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.18) 0%, rgba(8, 145, 178, 0.08) 100%);
  color: #22d3ee;
  border-color: rgba(6, 182, 212, 0.3);
}
.sim-launch-exit:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.28) 0%, rgba(8, 145, 178, 0.14) 100%);
  box-shadow: 0 0 24px rgba(6, 182, 212, 0.18), 0 4px 16px rgba(0, 0, 0, 0.3);
}

/* 按钮外圈光晕动画 */
.sim-launch-ring {
  position: absolute;
  inset: -2px;
  border-radius: 14px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.4s;
  border: 1px solid rgba(251, 191, 36, 0.25);
}
.sim-launch-exit .sim-launch-ring {
  border-color: rgba(6, 182, 212, 0.25);
}
.sim-launch-btn:hover:not(:disabled) .sim-launch-ring {
  opacity: 1;
}

/* 加载状态 */
.sim-launch-loading {
  animation: simBtnPulse 1.2s ease-in-out infinite;
}
@keyframes simBtnPulse {
  0%, 100% { opacity: 0.75; }
  50% { opacity: 0.5; }
}

/* spinner */
.sim-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.15);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: simSpin 0.7s linear infinite;
}
@keyframes simSpin {
  to { transform: rotate(360deg); }
}

/* fadeIn */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ============================================================
   Element Plus select dark theming (shallow override)
   ============================================================ */
.sim-select :deep(.el-input__wrapper) {
  background: #0a0f14;
  border: 1px solid rgba(100, 116, 139, 0.35);
  border-radius: 10px;
  box-shadow: none;
  padding: 4px 8px;
}
.sim-select :deep(.el-input__inner) {
  color: #e2e8f0;
  font-size: 14px;
}
.sim-select :deep(.el-input__inner::placeholder) {
  color: #475569;
}
</style>
