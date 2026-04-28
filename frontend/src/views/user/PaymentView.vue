<template>
  <!-- 支付中心 -->
  <div class="px-4 md:px-8 max-w-7xl mx-auto py-8">
    <header class="mb-8">
      <h1 class="text-3xl font-extrabold text-primary tracking-tight font-headline">支付中心</h1>
      <p class="text-secondary text-sm mt-2">缴纳停车费，管理订阅计划，查看支付历史。</p>
    </header>

    <!-- 账户余额卡片 -->
    <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-8 mb-8 shadow-lg border border-blue-200">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-blue-600 text-sm font-semibold mb-2">💰 账户余额</p>
          <p class="text-5xl font-black text-blue-700">¥ {{ userBalance.toFixed(2) }}</p>
          <p class="text-xs text-blue-500 mt-1">支持微信/支付宝/银行卡充值</p>
        </div>
        <button @click="showTopUpDialog = true" class="px-8 py-4 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 font-bold text-lg transition-all shadow-lg">
          + 充值
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- 左侧主要区域 -->
      <div class="lg:col-span-2 space-y-8">
        
        <!-- 当前停车会话卡片 -->
        <section>
          <div class="flex justify-between items-end mb-4">
            <h2 class="text-lg font-bold text-on-surface">当前停车</h2>
            <el-tag type="warning" class="!font-bold">进行中</el-tag>
          </div>
          <div class="rounded-2xl p-6 bg-gradient-to-br from-primary to-primary-container text-white shadow-lg relative overflow-hidden" v-if="currentSession">
             <!-- 背景装饰 -->
            <div class="absolute top-0 right-0 p-4 opacity-10">
              <span class="material-symbols-outlined" style="font-size: 140px;">local_parking</span>
            </div>
            
            <div class="relative z-10">
              <div class="flex justify-between items-start mb-6 border-b border-white/20 pb-6">
                <div>
                  <p class="text-white/80 text-xs font-medium uppercase tracking-wider mb-1">车牌号码</p>
                  <p class="text-2xl font-black tracking-widest font-headline">{{ currentSession.vehicle_detail?.plate_number || '--' }}</p>
                </div>
                <div class="text-right">
                  <p class="text-white/80 text-xs font-medium uppercase tracking-wider mb-1">当前产生费用</p>
                  <p class="text-3xl font-extrabold text-amber-300 font-headline">¥ <span class="text-4xl">{{ currentSession.amount }}</span></p>
                </div>
              </div>
              
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                 <div>
                    <p class="text-white/60 text-xs mb-1">停放位置</p>
                    <p class="font-semibold">{{ currentSession.spot_detail ? `${currentSession.spot_detail.floor}-${currentSession.spot_detail.spot_id}` : '--' }}</p>
                 </div>
                 <div>
                    <p class="text-white/60 text-xs mb-1">入场时间</p>
                    <p class="font-semibold">{{ new Date(currentSession.entry_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</p>
                 </div>
                 <div>
                    <p class="text-white/60 text-xs mb-1">已停时长</p>
                    <p class="font-semibold">{{ calculateDuration(currentSession.entry_time) }}</p>
                 </div>
                 <div>
                    <p class="text-white/60 text-xs mb-1">计费状态</p>
                    <p class="font-semibold">{{ currentSession.payment_status === 'paid' ? '已结清' : '计费中' }}</p>
                 </div>
              </div>
            </div>
            
            <div class="mt-8 flex gap-4">
              <el-button type="warning" size="large" class="!rounded-xl !font-bold !px-8 shadow-lg shadow-amber-500/30 border-0" @click="handlePay" :disabled="currentSession.payment_status === 'paid'">
                {{ currentSession.payment_status === 'paid' ? '已结清' : '立即缴费' }}
              </el-button>
              <el-button size="large" class="!rounded-xl !font-bold !bg-white/20 !text-white !border-0 hover:!bg-white/30 backdrop-blur-sm">
                查看明细
              </el-button>
            </div>
          </div>
          <div class="rounded-2xl p-8 bg-surface-container-low text-center text-secondary border border-outline-variant/20" v-else>
            <span class="material-symbols-outlined text-4xl mb-2 opacity-50">directions_car</span>
            <p>目前没有正在进行的停车会话</p>
          </div>
        </section>

        <!-- 历史账单表格 -->
        <section>
          <div class="flex justify-between items-end mb-4">
            <h2 class="text-lg font-bold text-on-surface">历史记录</h2>
          </div>
          <div class="bg-surface-container-lowest rounded-2xl border border-outline-variant/20 shadow-sm overflow-hidden" v-loading="loadingRecords">
            <el-table :data="historyRecords" style="width: 100%" stripe>
              <el-table-column prop="created_at" label="日期" width="160">
                <template #default="{ row }">
                  {{ new Date(row.created_at).toLocaleString() }}
                </template>
              </el-table-column>
              <el-table-column prop="payment_type_label" label="用途" width="140" />
              <el-table-column prop="method_label" label="支付方式" width="120">
                <template #default="{ row }">
                  {{ row.method_label || mapMethodLabel(row.method || row.payment_method) }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'success' ? 'success' : 'info'" size="small">
                    {{ row.status === 'success' ? '成功' : '处理中' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="金额 (¥)" font-weight="bold" align="right">
                <template #default="{ row }">
                  <span class="font-bold text-on-surface">¥ {{ row.amount }}</span>
                </template>
              </el-table-column>
            </el-table>
            <div class="p-4 flex justify-end" v-if="historyRecords.length > 0">
               <el-pagination size="small" layout="prev, pager, next" :total="historyRecords.length" />
            </div>
          </div>
        </section>
      </div>

      <!-- 右侧区域 -->
      <div class="space-y-8">
         <!-- 订阅套餐 -->
        <section>
          <h2 class="text-lg font-bold text-on-surface mb-4">我的订阅</h2>
          <div class="rounded-2xl p-6 bg-surface-container-low border border-outline-variant/20 relative" v-if="activeSubscription">
            <div class="absolute top-3 right-3">
               <el-tag type="success" effect="dark" round size="small" class="!font-bold">生效中</el-tag>
            </div>
            
            <div class="flex items-center gap-3 mb-6">
               <div class="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center text-primary">
                  <span class="material-symbols-outlined text-2xl">card_membership</span>
               </div>
               <div>
                  <h3 class="font-bold text-on-surface text-lg">{{ activeSubscription.plan_name || activeSubscription.plan_label || '订阅套餐' }}</h3>
                  <p class="text-xs text-secondary">套餐编码: {{ activeSubscription.plan || '--' }}</p>
               </div>
            </div>
            
            <div class="space-y-3 border-t border-outline-variant/20 pt-4 mb-6">
               <div class="flex justify-between text-sm">
                  <span class="text-secondary">有效期至</span>
                  <span class="font-semibold text-on-surface">{{ new Date(activeSubscription.end_date).toLocaleDateString() }}</span>
               </div>
               <div class="flex justify-between text-sm">
                  <span class="text-secondary">本周期剩余天数</span>
                  <span class="font-bold text-primary">{{ Math.ceil((new Date(activeSubscription.end_date) - new Date()) / 86400000) }} 天</span>
               </div>
            </div>
            
            <div class="grid grid-cols-2 gap-3">
              <el-button class="!rounded-xl" @click="openPlanDialog">续费/升级</el-button>
              <el-button type="danger" plain class="!rounded-xl" @click="handleDeactivateSubscription">停用订阅</el-button>
            </div>
          </div>
          <div class="rounded-2xl p-6 bg-surface-container-low text-center border border-outline-variant/20" v-else>
             <p class="text-secondary mb-4">您当前没有生效的订阅</p>
             <el-button plain type="primary" class="!rounded-xl" @click="openPlanDialog">购买套餐</el-button>
          </div>
        </section>

        <!-- 常用支付方式 -->
        <section>
          <h2 class="text-lg font-bold text-on-surface mb-4">支付方式</h2>
          <div class="rounded-2xl p-5 bg-surface-container-lowest border border-outline-variant/20 space-y-4">
             <div class="flex items-center justify-between p-3 border border-blue-300 bg-blue-50 rounded-xl cursor-pointer hover:bg-blue-100 transition-all"
               @click="selectedPaymentMethod = 'balance'">
                <div class="flex items-center gap-3">
                   <div class="w-10 h-10 rounded flex items-center justify-center">
                       <img :src="paymentMethodIcons.balance" alt="余额支付" class="w-6 h-6 object-contain" />
                   </div>
                   <div>
                     <p class="font-bold text-sm text-on-surface">余额支付</p>
                     <p class="text-xs text-secondary">当前余额: ¥{{ userBalance.toFixed(2) }}</p>
                   </div>
                </div>
                <span class="text-xl" :class="selectedPaymentMethod === 'balance' ? 'text-blue-500' : 'text-gray-300'">
                  {{ selectedPaymentMethod === 'balance' ? '✓' : '○' }}
                </span>
             </div>
             <div class="flex items-center justify-between p-3 border border-outline-variant/30 bg-white/5 hover:bg-green-50 rounded-xl cursor-pointer transition-all"
               @click="selectedPaymentMethod = 'wechat'">
                <div class="flex items-center gap-3">
                   <div class="w-10 h-10 rounded flex items-center justify-center">
                       <img :src="paymentMethodIcons.wechat" alt="微信支付" class="w-6 h-6 object-contain" />
                   </div>
                   <div>
                     <p class="font-bold text-sm text-on-surface">微信支付</p>
                     <p class="text-xs text-secondary">扫码支付</p>
                   </div>
                </div>
                <span class="text-xl" :class="selectedPaymentMethod === 'wechat' ? 'text-green-500' : 'text-gray-300'">
                  {{ selectedPaymentMethod === 'wechat' ? '✓' : '○' }}
                </span>
             </div>
             <div class="flex items-center justify-between p-3 border border-outline-variant/30 bg-white/5 hover:bg-cyan-50 rounded-xl cursor-pointer transition-all"
               @click="selectedPaymentMethod = 'alipay'">
                <div class="flex items-center gap-3">
                   <div class="w-10 h-10 rounded flex items-center justify-center">
                       <img :src="paymentMethodIcons.alipay" alt="支付宝" class="w-6 h-6 object-contain" />
                   </div>
                   <div>
                     <p class="font-bold text-sm text-on-surface">支付宝</p>
                     <p class="text-xs text-secondary">扫码支付</p>
                   </div>
                </div>
                <span class="text-xl" :class="selectedPaymentMethod === 'alipay' ? 'text-cyan-500' : 'text-gray-300'">
                  {{ selectedPaymentMethod === 'alipay' ? '✓' : '○' }}
                </span>
             </div>
             <div class="flex items-center justify-between p-3 border border-outline-variant/30 bg-white/5 rounded-xl transition-all"
               :class="hasBankCard ? 'hover:bg-purple-50 cursor-pointer' : 'opacity-60 cursor-not-allowed'"
               @click="selectMainPaymentMethod('card')">
                <div class="flex items-center gap-3">
                   <div class="w-10 h-10 rounded flex items-center justify-center">
                       <img :src="paymentMethodIcons.card" alt="银行卡" class="w-6 h-6 object-contain" />
                   </div>
                   <div>
                     <p class="font-bold text-sm text-on-surface">银行卡</p>
                     <p class="text-xs text-secondary">{{ hasBankCard ? '已添加银行卡' : '请先添加银行卡' }}</p>
                   </div>
                </div>
                <span class="text-xl" :class="selectedPaymentMethod === 'card' && hasBankCard ? 'text-purple-500' : 'text-gray-300'">
                  {{ selectedPaymentMethod === 'card' && hasBankCard ? '✓' : '○' }}
                </span>
             </div>
             <div v-if="!hasBankCard" class="text-right">
               <el-button type="primary" link @click="openAddCardDialog">添加银行卡</el-button>
             </div>
          </div>
        </section>
      </div>
    </div>

    <!-- 充值对话框 -->
    <el-dialog v-model="showTopUpDialog" title="账户充值" width="90%" max-width="500px" :close-on-click-modal="false">
      <div class="space-y-6">
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-3">选择充值金额</label>
          <div class="grid grid-cols-3 gap-3">
            <button
              v-for="amount in quickTopUpAmounts"
              :key="amount"
              @click="topUpAmount = amount; customTopUpAmount = null"
              :class="[
                'py-3 rounded-lg font-semibold transition-all',
                topUpAmount === amount && !customTopUpAmount
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              ¥{{ amount }}
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-2">自定义金额</label>
          <div class="flex gap-2">
            <span class="text-xl font-bold text-slate-700 px-4 py-2 bg-gray-100 rounded-lg">¥</span>
            <input
              v-model.number="customTopUpAmount"
              type="number"
              placeholder="输入充值金额"
              min="0"
              step="0.01"
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
          </div>
          <p class="mt-2 text-xs text-slate-500">优惠规则：1-100 打9折，100-500 打8折，500以上打7.5折。</p>
          <p class="mt-1 text-xs font-semibold text-emerald-600">
            当前充值 ¥{{ finalTopUpAmount.toFixed(2) }}，折后实付 ¥{{ topUpPayableAmount.toFixed(2) }}，到账 ¥{{ finalTopUpAmount.toFixed(2) }}
          </p>
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-3">选择充值方式</label>
          <div class="space-y-2">
            <label v-for="method in [
              { value: 'wechat', label: '微信支付' },
              { value: 'alipay', label: '支付宝' },
              { value: 'card', label: '银行卡' }
            ]" :key="method.value" class="flex items-center gap-3 p-3 border rounded-lg"
              :class="method.value === 'card' && !hasBankCard ? 'opacity-60 cursor-not-allowed bg-gray-50' : 'cursor-pointer hover:bg-gray-50'">
              <input type="radio" :value="method.value" v-model="topUpPaymentMethod" class="w-4 h-4" :disabled="method.value === 'card' && !hasBankCard"/>
              <span class="font-semibold">{{ method.label }}</span>
            </label>
            <p v-if="!hasBankCard" class="text-xs text-slate-500">银行卡充值需先添加银行卡。</p>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex gap-3">
          <el-button @click="showTopUpDialog = false">取消</el-button>
          <el-button type="primary" @click="handleTopUp" :loading="isTopUpProcessing">
            确认支付 ¥{{ topUpPayableAmount.toFixed(2) }}（到账 ¥{{ finalTopUpAmount.toFixed(2) }}）
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 沙箱二维码支付弹窗 -->
    <el-dialog
      v-model="showSandboxQrDialog"
      :title="sandboxPayTitle"
      width="90%"
      max-width="420px"
      :close-on-click-modal="false"
    >
      <div class="text-center space-y-4">
        <p class="text-sm text-slate-500">请使用{{ sandboxPayMethodLabel }}扫码完成支付（沙箱模拟）</p>
        <img
          v-if="sandboxQrImage"
          :src="sandboxQrImage"
          alt="沙箱支付二维码"
          class="w-64 h-64 mx-auto rounded-xl border border-slate-200"
        />
        <div class="bg-slate-50 rounded-lg p-3 text-left text-sm space-y-1">
          <p><span class="text-slate-500">订单号：</span>{{ sandboxTransactionId }}</p>
          <p><span class="text-slate-500">支付金额：</span>¥{{ sandboxPayAmount }}</p>
        </div>
      </div>
      <template #footer>
        <div class="flex gap-3">
          <el-button @click="showSandboxQrDialog = false">取消</el-button>
          <el-button type="primary" :loading="isSandboxConfirming" @click="confirmSandboxSuccess">
            我已扫码并完成支付
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 添加银行卡弹窗 -->
    <el-dialog
      v-model="showAddCardDialog"
      title="添加银行卡"
      width="90%"
      max-width="460px"
      :close-on-click-modal="false"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-2">持卡人姓名</label>
          <input
            v-model="bankCardForm.holder"
            type="text"
            placeholder="请输入姓名"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          />
        </div>
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-2">银行卡号</label>
          <input
            v-model="bankCardForm.number"
            type="text"
            placeholder="请输入16-19位银行卡号"
            maxlength="19"
            @input="bankCardForm.number = String(bankCardForm.number || '').replace(/\D/g, '')"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-2">预留手机号</label>
          <input
            v-model="bankCardForm.phone"
            type="text"
            placeholder="请输入11位手机号"
            maxlength="11"
            @input="bankCardForm.phone = String(bankCardForm.phone || '').replace(/\D/g, '')"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-2">人机验证</label>
          <div class="rounded-lg border border-slate-300 p-3 bg-slate-50">
            <div class="relative h-12 rounded-md bg-gradient-to-r from-slate-100 to-slate-200 overflow-hidden mb-3">
              <div
                class="absolute top-2 w-8 h-8 rounded-md border-2 border-dashed border-slate-400 bg-white/70"
                :style="{ left: `${bankCardPuzzleTarget}px` }"
              />
              <div
                class="absolute top-2 w-8 h-8 rounded-md bg-blue-500/90 border border-white shadow transition-all duration-75"
                :style="{ left: `${bankCardPuzzleValue}px` }"
              />
            </div>
            <div class="flex gap-2 items-center">
              <input
                v-model.number="bankCardPuzzleValue"
                type="range"
                min="0"
                :max="bankCardPuzzleMax"
                class="w-full"
                :disabled="bankCardHumanVerified"
                @input="handleBankCardPuzzleSlide"
              />
              <el-button @click="resetBankCardPuzzleCaptcha">重置</el-button>
            </div>
          </div>
          <p class="text-xs mt-1" :class="bankCardHumanVerified ? 'text-emerald-600' : 'text-slate-500'">
            {{ bankCardHumanVerified ? '拼图校验通过' : '拖动滑块，让蓝色拼图块对齐虚线缺口。' }}
          </p>
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-2">验证码</label>
          <div class="flex gap-2">
            <input
              v-model="bankCardForm.code"
              type="text"
              placeholder="请输入6位验证码"
              maxlength="6"
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
            <el-button :disabled="!bankCardHumanVerified" @click="requestBankCardCode">发送验证码</el-button>
          </div>
          <p class="text-xs text-slate-500 mt-1">需先通过拖动拼图验证，才可发送短信验证码。</p>
        </div>
      </div>
      <template #footer>
        <div class="flex gap-3">
          <el-button @click="showAddCardDialog = false">取消</el-button>
          <el-button type="primary" @click="handleAddBankCard">确认添加并验证</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 订阅套餐选择弹窗 -->
    <el-dialog
      v-model="showPlanDialog"
      title="选择订阅套餐"
      width="90%"
      max-width="620px"
      :close-on-click-modal="false"
    >
      <div class="space-y-4" v-loading="loadingPlanOptions">
        <div
          v-for="plan in subscriptionPlans"
          :key="plan.id"
          class="rounded-xl border p-4 cursor-pointer transition-all"
          :class="selectedPlanId === plan.id ? 'border-primary bg-primary/5' : 'border-outline-variant/30 hover:border-primary/40'"
          @click="selectedPlanId = plan.id"
        >
          <div class="flex items-center justify-between mb-2">
            <p class="text-base font-bold text-on-surface">{{ plan.name }}</p>
            <el-tag v-if="plan.recommended" type="success" size="small" effect="dark">推荐</el-tag>
          </div>
          <p class="text-2xl font-extrabold text-primary">¥{{ plan.price }}</p>
          <p class="text-xs text-emerald-600 font-semibold mt-1">约 ¥{{ calcDailyPrice(plan.price, plan.durationDays) }}/天</p>
          <p class="text-xs text-secondary mt-1">{{ plan.description }}</p>
        </div>
        <div v-if="!loadingPlanOptions && subscriptionPlans.length === 0" class="text-sm text-secondary text-center py-4">
          暂无可购买套餐
        </div>

        <div class="rounded-xl border border-outline-variant/30 p-4 bg-slate-50/60">
          <p class="text-sm font-bold text-on-surface mb-3">套餐支付方式</p>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div
              class="flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-all"
              :class="planPaymentMethod === 'wechat' ? 'border-emerald-400 bg-emerald-50' : 'border-outline-variant/30 bg-white hover:border-emerald-300'"
              @click="planPaymentMethod = 'wechat'"
            >
              <div class="flex items-center gap-2">
                <img :src="paymentMethodIcons.wechat" alt="微信支付" class="w-5 h-5 object-contain" />
                <span class="text-sm font-semibold">微信</span>
              </div>
              <span class="text-xs text-slate-500">扫码</span>
            </div>
            <div
              class="flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-all"
              :class="planPaymentMethod === 'alipay' ? 'border-cyan-400 bg-cyan-50' : 'border-outline-variant/30 bg-white hover:border-cyan-300'"
              @click="planPaymentMethod = 'alipay'"
            >
              <div class="flex items-center gap-2">
                <img :src="paymentMethodIcons.alipay" alt="支付宝支付" class="w-5 h-5 object-contain" />
                <span class="text-sm font-semibold">支付宝</span>
              </div>
              <span class="text-xs text-slate-500">扫码</span>
            </div>
            <div
              class="flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-all"
              :class="!hasBankCard
                ? 'border-outline-variant/30 bg-gray-50 opacity-60 cursor-not-allowed'
                : (planPaymentMethod === 'card' ? 'border-purple-400 bg-purple-50' : 'border-outline-variant/30 bg-white hover:border-purple-300')"
              @click="hasBankCard ? (planPaymentMethod = 'card') : openAddCardDialog()"
            >
              <div class="flex items-center gap-2">
                <img :src="paymentMethodIcons.card" alt="银行卡支付" class="w-5 h-5 object-contain" />
                <span class="text-sm font-semibold">银行卡</span>
              </div>
              <span class="text-xs text-slate-500">{{ hasBankCard ? '扫码' : '先添加' }}</span>
            </div>
          </div>
          <p class="mt-2 text-xs text-slate-500">套餐仅支持微信/支付宝/银行卡扫码支付，不支持余额支付。</p>
        </div>
      </div>
      <template #footer>
        <div class="flex gap-3">
          <el-button @click="showPlanDialog = false">取消</el-button>
          <el-button type="primary" :loading="isPurchasingPlan" :disabled="subscriptionPlans.length === 0" @click="handlePurchasePlan">
            确认购买并支付
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getPayments,
  getTopUpRecords,
  getSubscriptions,
  getSubscriptionPlans,
  createSubscription,
  updateSubscription,
  getUserBalance,
  topupBalance,
  confirmTopup,
  payWithBalance,
  createSandboxPayment,
  confirmSandboxPayment,
} from '@/api/payment'
import { getCurrentSessions } from '@/api/parking'
import { hasBoundBankCard, setBankCardBound } from '@/utils/bankCard'
import { getDefaultPaymentMethod } from '@/utils/paymentPreference'

const router = useRouter()

const currentSession = ref(null)
const historyRecords = ref([])
const activeSubscription = ref(null)
const loadingRecords = ref(false)
const showPlanDialog = ref(false)
const selectedPlanId = ref(null)
const isPurchasingPlan = ref(false)
const loadingPlanOptions = ref(false)

const subscriptionPlans = ref([])

// 余额相关
const userBalance = ref(0)
const loadingBalance = ref(false)
const showTopUpDialog = ref(false)
const topUpAmount = ref(50)
const customTopUpAmount = ref(null)
const topUpPaymentMethod = ref('wechat')
const isTopUpProcessing = ref(false)
const quickTopUpAmounts = [50, 100, 200, 500, 1000]

// 支付方式选择
const selectedPaymentMethod = ref('balance')

// 沙箱扫码支付状态
const showSandboxQrDialog = ref(false)
const sandboxQrImage = ref('')
const sandboxTransactionId = ref('')
const sandboxPayAmount = ref('0.00')
const sandboxPayTitle = ref('扫码支付')
const sandboxPayMethodLabel = ref('支付方式')
const sandboxContext = ref('') // topup | parking
const isSandboxConfirming = ref(false)
const pendingSubscriptionPayload = ref(null)
const pendingSubscriptionPlanName = ref('')
const planPaymentMethod = ref('wechat')
const paymentMethodIcons = {
  balance: '/余额.svg',
  wechat: '/微信支付.svg',
  alipay: '/支付宝支付.svg',
  card: '/银行卡.svg',
}
const hasBankCard = ref(false)
const showAddCardDialog = ref(false)
const bankCardForm = ref({
  phone: '',
  holder: '',
  number: '',
  code: '',
})
const bankCardHumanVerified = ref(false)
const bankCardPuzzleMax = 220
const bankCardPuzzleTarget = ref(0)
const bankCardPuzzleValue = ref(0)
const mockCardVerifyCode = ref('')

const finalTopUpAmount = computed(() => {
  return customTopUpAmount.value && customTopUpAmount.value > 0
    ? customTopUpAmount.value
    : topUpAmount.value
})

const topUpDiscountRate = computed(() => {
  const amount = Number(finalTopUpAmount.value || 0)
  if (amount <= 0) return 1
  if (amount <= 100) return 0.9
  if (amount <= 500) return 0.8
  return 0.75
})

const topUpPayableAmount = computed(() => {
  const amount = Number(finalTopUpAmount.value || 0)
  if (amount <= 0) return 0
  return Number((amount * topUpDiscountRate.value).toFixed(2))
})

function mapMethodLabel(method) {
  const map = {
    wechat: '微信支付',
    alipay: '支付宝支付',
    card: '银行卡',
    balance: '余额支付',
    cash: '现金',
  }
  return map[method] || method || '--'
}

function normalizeHistoryRow(row, sourceType) {
  return {
    ...row,
    _source_type: sourceType,
    method: row.method || row.payment_method || '',
    method_label: row.method_label || row.payment_method_label || mapMethodLabel(row.method || row.payment_method),
    payment_type: row.payment_type || (sourceType === 'topup' ? 'topup' : 'other'),
    payment_type_label: row.payment_type_label || (sourceType === 'topup' ? '余额充值' : '其他支付'),
  }
}

async function loadHistoryRecords() {
  loadingRecords.value = true
  try {
    const [pays, topups] = await Promise.all([
      getPayments(),
      getTopUpRecords(),
    ])

    const paymentRows = (pays?.results || pays || []).map((item) => normalizeHistoryRow(item, 'payment'))
    const topupRows = (topups?.results || topups || []).map((item) => normalizeHistoryRow(item, 'topup'))

    historyRecords.value = [...paymentRows, ...topupRows].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  } catch (err) {
    historyRecords.value = []
    console.error('获取账单失败', err)
  } finally {
    loadingRecords.value = false
  }
}

async function loadUserBalance() {
  loadingBalance.value = true
  try {
    const response = await getUserBalance()
    userBalance.value = parseFloat(response.data?.balance || response.balance || 0)
  } catch (err) {
    console.error('获取余额失败', err)
    userBalance.value = 0
  } finally {
    loadingBalance.value = false
  }
}

onMounted(async () => {
  hasBankCard.value = hasBoundBankCard()
  const defaultMethod = getDefaultPaymentMethod('balance')
  selectedPaymentMethod.value = (!hasBankCard.value && defaultMethod === 'card') ? 'wechat' : defaultMethod
  // 获取用户余额
  await loadUserBalance()
  // 获取当前停车
  try {
    const sessions = await getCurrentSessions()
    if (sessions.length > 0) {
      currentSession.value = sessions[0]
    }
  } catch (err) {
    console.error('获取停车记录失败', err)
  }

  // 获取支付与充值历史记录
  await loadHistoryRecords()

  // 获取当前订阅
  try {
    const subs = await getSubscriptions({ is_active: true })
    const activeSubs = subs.results || subs
    if (activeSubs.length > 0) {
      activeSubscription.value = activeSubs[0]
    }
  } catch (err) {
    console.error('获取订阅失败', err)
  }
})

function selectMainPaymentMethod(method) {
  if (method === 'card' && !hasBankCard.value) {
    ElMessage.warning('请先添加银行卡后再使用银行卡支付')
    openAddCardDialog()
    return
  }
  selectedPaymentMethod.value = method
}

function openAddCardDialog() {
  bankCardForm.value = {
    phone: '',
    holder: '',
    number: '',
    code: '',
  }
  bankCardHumanVerified.value = false
  resetBankCardPuzzleCaptcha()
  mockCardVerifyCode.value = ''
  showAddCardDialog.value = true
}

function resetBankCardPuzzleCaptcha() {
  bankCardHumanVerified.value = false
  bankCardPuzzleValue.value = 0
  bankCardPuzzleTarget.value = Math.floor(20 + Math.random() * (bankCardPuzzleMax - 40))
}

function handleBankCardPuzzleSlide() {
  if (bankCardHumanVerified.value) return
  const delta = Math.abs(Number(bankCardPuzzleValue.value || 0) - Number(bankCardPuzzleTarget.value || 0))
  if (delta <= 4) {
    bankCardHumanVerified.value = true
    ElMessage.success('人机验证通过')
  }
}

function handleAddBankCard() {
  const phone = String(bankCardForm.value.phone || '').replace(/\D/g, '')
  const holder = String(bankCardForm.value.holder || '').trim()
  const number = String(bankCardForm.value.number || '').replace(/\D/g, '')
  const code = String(bankCardForm.value.code || '').trim()

  if (!/^1\d{10}$/.test(phone)) {
    ElMessage.warning('请输入正确的11位手机号')
    return
  }
  if (!bankCardHumanVerified.value) {
    ElMessage.warning('请先完成人机验证')
    return
  }

  if (!holder) {
    ElMessage.warning('请输入持卡人姓名')
    return
  }
  if (!/^\d{16,19}$/.test(number)) {
    ElMessage.warning('银行卡号需为16到19位数字')
    return
  }
  if (!mockCardVerifyCode.value) {
    ElMessage.warning('请先发送验证码')
    return
  }
  if (code !== mockCardVerifyCode.value) {
    ElMessage.error('验证码错误，请重新输入')
    return
  }

  setBankCardBound(true)
  hasBankCard.value = true
  selectedPaymentMethod.value = 'card'
  bankCardForm.value = { phone: '', holder: '', number: '', code: '' }
  bankCardHumanVerified.value = false
  resetBankCardPuzzleCaptcha()
  mockCardVerifyCode.value = ''
  showAddCardDialog.value = false
  ElMessage.success('银行卡添加并验证成功')
}

function requestBankCardCode() {
  const phone = String(bankCardForm.value.phone || '').replace(/\D/g, '')
  const holder = String(bankCardForm.value.holder || '').trim()
  const number = String(bankCardForm.value.number || '').replace(/\D/g, '')

  if (!bankCardHumanVerified.value) {
    ElMessage.warning('请先完成人机验证')
    return
  }
  if (!/^1\d{10}$/.test(phone)) {
    ElMessage.warning('请输入正确的11位手机号')
    return
  }
  if (!holder) {
    ElMessage.warning('请输入持卡人姓名')
    return
  }
  if (!/^\d{16,19}$/.test(number)) {
    ElMessage.warning('银行卡号需为16到19位数字')
    return
  }

  mockCardVerifyCode.value = String(Math.floor(100000 + Math.random() * 900000))
  ElMessage.success(`验证码已发送（模拟）：${mockCardVerifyCode.value}`)
}

async function loadSubscriptionPlans() {
  loadingPlanOptions.value = true
  try {
    const res = await getSubscriptionPlans({ is_active: true })
    const rows = res?.results || res || []
    subscriptionPlans.value = rows.map((item) => ({
      id: item.id,
      code: item.code,
      name: item.name || item.code_label || '套餐',
      price: item.price,
      durationDays: Number(item.duration_days || 0),
      description: item.description || '暂无描述',
      recommended: Boolean(item.is_recommended),
    }))
    const preferred = subscriptionPlans.value.find((p) => p.recommended)
    selectedPlanId.value = preferred
      ? preferred.id
      : (subscriptionPlans.value.length ? subscriptionPlans.value[0].id : null)
  } catch (err) {
    subscriptionPlans.value = []
    selectedPlanId.value = null
    ElMessage.error('加载套餐失败: ' + (err.response?.data?.detail || err.message))
  } finally {
    loadingPlanOptions.value = false
  }
}

async function openPlanDialog() {
  planPaymentMethod.value = 'wechat'
  showPlanDialog.value = true
  await loadSubscriptionPlans()
}

function toDateString(date) {
  return date.toISOString().slice(0, 10)
}

function calcDailyPrice(price, durationDays) {
  const days = Number(durationDays || 0)
  const amount = Number(price || 0)
  if (days <= 0 || amount <= 0) {
    return '--'
  }
  return (amount / days).toFixed(2)
}

async function handlePurchasePlan() {
  const plan = subscriptionPlans.value.find((p) => p.id === selectedPlanId.value)
  if (!plan) {
    ElMessage.warning('请选择订阅套餐')
    return
  }

  isPurchasingPlan.value = true
  try {
    const start = new Date()
    const end = new Date(start)
    end.setDate(end.getDate() + plan.durationDays)

    const payload = {
      plan_ref_id: plan.id,
      plan: plan.code,
      price: plan.price,
      start_date: toDateString(start),
      end_date: toDateString(end),
      is_active: true,
    }

    const planAmount = Number(plan.price || 0)
    if (!planAmount || planAmount <= 0) {
      ElMessage.error('套餐金额异常，无法购买')
      return
    }

    if (!['wechat', 'alipay', 'card'].includes(planPaymentMethod.value)) {
      ElMessage.warning('套餐仅支持扫码支付，请选择微信/支付宝/银行卡')
      return
    }

    const res = await createSandboxPayment(
      planAmount,
      planPaymentMethod.value,
      null,
      `订阅套餐购买:${plan.name}`
    )

    pendingSubscriptionPayload.value = payload
    pendingSubscriptionPlanName.value = plan.name
    sandboxContext.value = 'subscription'
    sandboxTransactionId.value = res.transaction_id
    sandboxQrImage.value = res.qr_code_url
    sandboxPayAmount.value = planAmount.toFixed(2)
    sandboxPayMethodLabel.value = planPaymentMethod.value === 'wechat'
      ? '微信支付'
      : planPaymentMethod.value === 'alipay'
        ? '支付宝'
        : '银行卡'
    sandboxPayTitle.value = '订阅套餐扫码支付'
    showSandboxQrDialog.value = true
  } catch (err) {
    ElMessage.error('购买失败: ' + (err.response?.data?.detail || err.message))
  } finally {
    isPurchasingPlan.value = false
  }
}

async function handleDeactivateSubscription() {
  if (!activeSubscription.value?.id) {
    ElMessage.warning('当前没有可管理的生效订阅')
    return
  }

  try {
    await ElMessageBox.confirm(
      '确认停用当前订阅吗？停用后将不再按订阅权益计费。',
      '停用订阅',
      {
        confirmButtonText: '确认停用',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const updated = await updateSubscription(activeSubscription.value.id, { is_active: false })
    activeSubscription.value = null
    ElMessage.success(`订阅已停用：${updated?.plan_label || updated?.plan_name || updated?.plan || ''}`)
  } catch (err) {
    if (err === 'cancel') return
    ElMessage.error('停用订阅失败: ' + (err.response?.data?.detail || err.message))
  }
}

function calculateDuration(startTime) {
  const diffMs = new Date() - new Date(startTime)
  const diffHrs = Math.floor(diffMs / 3600000)
  const diffMins = Math.floor((diffMs % 3600000) / 60000)
  return `${diffHrs}h ${diffMins}m`
}

async function handleTopUp() {
  if (finalTopUpAmount.value <= 0) {
    ElMessage.warning('请输入有效的充值金额')
    return
  }

  if (topUpPaymentMethod.value === 'card' && !hasBankCard.value) {
    ElMessage.warning('请先添加银行卡后再使用银行卡充值')
    showAddCardDialog.value = true
    return
  }

  isTopUpProcessing.value = true
  try {
    const res = await topupBalance(finalTopUpAmount.value, topUpPaymentMethod.value)

    sandboxContext.value = 'topup'
    sandboxTransactionId.value = res.transaction_id
    sandboxQrImage.value = res.qr_code_url
    sandboxPayAmount.value = String(res?.payable_amount || topUpPayableAmount.value.toFixed(2))
    sandboxPayMethodLabel.value = topUpPaymentMethod.value === 'wechat'
      ? '微信支付'
      : topUpPaymentMethod.value === 'alipay'
        ? '支付宝'
        : '银行卡'
    sandboxPayTitle.value = '充值扫码支付'

    showTopUpDialog.value = false
    showSandboxQrDialog.value = true
  } catch (err) {
    ElMessage.error('充值失败: ' + (err.response?.data?.detail || err.message))
  } finally {
    isTopUpProcessing.value = false
  }
}

async function confirmSandboxSuccess() {
  if (!sandboxTransactionId.value || !sandboxContext.value) {
    ElMessage.error('支付上下文丢失，请重新发起支付')
    return
  }

  isSandboxConfirming.value = true
  try {
    if (sandboxContext.value === 'topup') {
      const topupResult = await confirmTopup(sandboxTransactionId.value, true)
      await loadUserBalance()
      const credited = Number(topupResult?.recharge_amount || topupResult?.amount || finalTopUpAmount.value || 0)
      ElMessage.success(`充值成功！已添加 ¥${credited.toFixed(2)} 到账户`)

      // 充值成功后重置表单
      topUpAmount.value = 50
      customTopUpAmount.value = null
    } else if (sandboxContext.value === 'parking') {
      await confirmSandboxPayment(sandboxTransactionId.value, true)
      if (currentSession.value) {
        currentSession.value.payment_status = 'paid'
      }
      ElMessage.success('支付成功！15分钟内离场免费。')
    } else if (sandboxContext.value === 'subscription') {
      await confirmSandboxPayment(sandboxTransactionId.value, true)
      if (!pendingSubscriptionPayload.value) {
        throw new Error('套餐订单信息丢失，请重新发起购买')
      }

      const created = await createSubscription(pendingSubscriptionPayload.value)
      activeSubscription.value = created
      showPlanDialog.value = false
      ElMessage.success(`${pendingSubscriptionPlanName.value || '订阅套餐'} 购买成功`)
      pendingSubscriptionPayload.value = null
      pendingSubscriptionPlanName.value = ''
    }

    showSandboxQrDialog.value = false
    await loadHistoryRecords()
  } catch (err) {
    ElMessage.error('确认支付失败: ' + (err.response?.data?.detail || err.message))
  } finally {
    isSandboxConfirming.value = false
  }
}

const handlePay = async () => {
  if (!currentSession.value) return

  const amount = Number(currentSession.value.amount)
  if (!amount || amount <= 0) {
    ElMessage.warning('当前账单金额异常')
    return
  }

  if (selectedPaymentMethod.value === 'balance') {
    if (userBalance.value < amount) {
      ElMessage.error('余额不足，请先充值')
      return
    }

    await ElMessageBox.confirm(
      `本次结账金额 ¥${amount.toFixed(2)}，确认使用余额支付吗？`,
      '确认支付',
      {
        confirmButtonText: '确认支付',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    try {
      await payWithBalance(amount, currentSession.value.id, '停车费')
      await loadUserBalance()
      currentSession.value.payment_status = 'paid'
      ElMessage.success('余额支付成功！15分钟内离场免费。')
    } catch (err) {
      ElMessage.error('余额支付失败: ' + (err.response?.data?.detail || err.message))
    }
    return
  }

  try {
    const res = await createSandboxPayment(
      amount,
      selectedPaymentMethod.value,
      currentSession.value.id,
      '停车费支付'
    )

    sandboxContext.value = 'parking'
    sandboxTransactionId.value = res.transaction_id
    sandboxQrImage.value = res.qr_code_url
    sandboxPayAmount.value = amount.toFixed(2)
    sandboxPayMethodLabel.value = selectedPaymentMethod.value === 'wechat'
      ? '微信支付'
      : selectedPaymentMethod.value === 'alipay'
        ? '支付宝'
        : '银行卡'
    sandboxPayTitle.value = '停车费扫码支付'
    showSandboxQrDialog.value = true
  } catch (err) {
    ElMessage.error('创建支付订单失败: ' + (err.response?.data?.detail || err.message))
  }
}
</script>
