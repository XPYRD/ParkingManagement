<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 py-12 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- 页面头部 -->
      <header class="text-center mb-12">
        <h1 class="text-4xl font-extrabold text-slate-900 mb-2">选择支付方式</h1>
        <p class="text-slate-600">安全便捷的支付体验</p>
      </header>

      <!-- 账户余额卡片 -->
      <div class="bg-white rounded-2xl shadow-lg p-8 mb-8">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-slate-600 text-sm mb-2">账户余额</p>
            <p class="text-4xl font-bold text-blue-600">¥ {{ userBalance.toFixed(2) }}</p>
          </div>
          <button @click="showTopUpDialog = true" class="px-6 py-3 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 font-semibold transition-all">
            + 充值
          </button>
        </div>
      </div>

      <!-- 支付金额说明 -->
      <div class="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-6 mb-8">
        <p class="text-slate-700 font-semibold">需支付金额</p>
        <p class="text-3xl font-bold text-blue-600 mt-2">¥ {{ paymentAmount.toFixed(2) }}</p>
      </div>

      <!-- 支付方式选择 -->
      <div class="space-y-4 mb-8">
        <h2 class="text-xl font-bold text-slate-900 mb-6">选择支付方式</h2>

        <!-- 余额支付 -->
        <div
          v-if="userBalance >= paymentAmount"
          @click="selectedPaymentMethod = 'balance'"
          class="cursor-pointer p-6 rounded-2xl border-2 transition-all"
          :class="
            selectedPaymentMethod === 'balance'
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          "
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-full flex items-center justify-center">
                <img :src="paymentMethodIcons.balance" alt="余额支付" class="w-7 h-7 object-contain" />
              </div>
              <div>
                <p class="font-semibold text-slate-900">余额支付</p>
                <p class="text-sm text-slate-600 mt-1">直接使用账户余额</p>
              </div>
            </div>
            <div v-if="selectedPaymentMethod === 'balance'" class="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
              <span class="text-white text-sm">✓</span>
            </div>
          </div>
        </div>

        <!-- 微信支付 -->
        <div
          @click="selectedPaymentMethod = 'wechat'"
          class="cursor-pointer p-6 rounded-2xl border-2 transition-all"
          :class="
            selectedPaymentMethod === 'wechat'
              ? 'border-emerald-500 bg-emerald-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          "
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-full flex items-center justify-center">
                <img :src="paymentMethodIcons.wechat" alt="微信支付" class="w-7 h-7 object-contain" />
              </div>
              <div>
                <p class="font-semibold text-slate-900">微信支付</p>
                <p class="text-sm text-slate-600 mt-1">使用微信扫码支付</p>
              </div>
            </div>
            <div v-if="selectedPaymentMethod === 'wechat'" class="w-6 h-6 bg-emerald-500 rounded-full flex items-center justify-center">
              <span class="text-white text-sm">✓</span>
            </div>
          </div>
        </div>

        <!-- 支付宝 -->
        <div
          @click="selectedPaymentMethod = 'alipay'"
          class="cursor-pointer p-6 rounded-2xl border-2 transition-all"
          :class="
            selectedPaymentMethod === 'alipay'
              ? 'border-blue-400 bg-blue-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          "
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-full flex items-center justify-center">
                <img :src="paymentMethodIcons.alipay" alt="支付宝" class="w-7 h-7 object-contain" />
              </div>
              <div>
                <p class="font-semibold text-slate-900">支付宝</p>
                <p class="text-sm text-slate-600 mt-1">使用支付宝扫码支付</p>
              </div>
            </div>
            <div v-if="selectedPaymentMethod === 'alipay'" class="w-6 h-6 bg-blue-400 rounded-full flex items-center justify-center">
              <span class="text-white text-sm">✓</span>
            </div>
          </div>
        </div>

        <!-- 银行卡 -->
        <div
          @click="selectedPaymentMethod = 'card'"
          class="cursor-pointer p-6 rounded-2xl border-2 transition-all"
          :class="
            selectedPaymentMethod === 'card'
              ? 'border-purple-500 bg-purple-50'
              : 'border-gray-200 bg-white hover:border-gray-300'
          "
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-full flex items-center justify-center">
                <img :src="paymentMethodIcons.card" alt="银行卡" class="w-7 h-7 object-contain" />
              </div>
              <div>
                <p class="font-semibold text-slate-900">银行卡</p>
                <p class="text-sm text-slate-600 mt-1">绑定的银行卡支付</p>
              </div>
            </div>
            <div v-if="selectedPaymentMethod === 'card'" class="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center">
              <span class="text-white text-sm">✓</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="flex gap-4">
        <button @click="$router.back()" class="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 font-semibold transition-all">
          返回
        </button>
        <button
          @click="handlePay"
          :disabled="!selectedPaymentMethod || isProcessing"
          class="flex-1 px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-gray-400 font-semibold transition-all"
        >
          <span v-if="!isProcessing">立即支付 ¥{{ paymentAmount.toFixed(2) }}</span>
          <span v-else>处理中...</span>
        </button>
      </div>

      <!-- 安全说明 -->
      <div class="mt-8 text-center text-sm text-slate-600">
        <p>🔒 所有交易均经过加密处理，确保您的资金安全</p>
      </div>
    </div>

    <!-- 充值对话框 -->
    <el-dialog v-model="showTopUpDialog" title="账户充值" width="90%" max-width="500px">
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
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-3">选择充值方式</label>
          <el-radio-group v-model="topUpPaymentMethod" class="!flex !gap-4 !flex-wrap">
            <el-radio label="wechat">微信支付</el-radio>
            <el-radio label="alipay">支付宝</el-radio>
            <el-radio label="card">银行卡</el-radio>
          </el-radio-group>
        </div>
      </div>

      <template #footer>
        <div class="flex gap-3">
          <el-button @click="showTopUpDialog = false">取消</el-button>
          <el-button type="primary" @click="handleTopUp" :loading="isTopUpProcessing">
            确认充值 ¥{{ finalTopUpAmount.toFixed(2) }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getUserBalance, topupBalance, payWithBalance } from '@/api/payment'

const router = useRouter()
const route = useRoute()

// 用户余额（从后端获取）
const userBalance = ref(0)

// 支付金额（从路由参数获取，如果没有则使用默认值）
const paymentAmount = ref(parseFloat(route.query.amount) || 35.00)

// 支付方式选择
const selectedPaymentMethod = ref(null)

// 充值相关
const showTopUpDialog = ref(false)
const topUpAmount = ref(50)
const customTopUpAmount = ref(null)
const topUpPaymentMethod = ref('wechat')
const quickTopUpAmounts = [50, 100, 200, 500, 1000]

// 处理中标志
const isProcessing = ref(false)
const isTopUpProcessing = ref(false)
const paymentMethodIcons = {
  balance: '/余额.svg',
  wechat: '/微信支付.svg',
  alipay: '/支付宝支付.svg',
  card: '/银行卡.svg',
}

// 最终充值金额计算
const finalTopUpAmount = computed(() => {
  return customTopUpAmount.value && customTopUpAmount.value > 0
    ? customTopUpAmount.value
    : topUpAmount.value
})

// 加载用户余额
async function loadUserBalance() {
  try {
    const response = await getUserBalance()
    userBalance.value = parseFloat(response.data.balance) || 0
  } catch (error) {
    console.error('Failed to load balance:', error)
    ElMessage.error('加载余额失败，请重试')
  }
}

// 支付处理
async function handlePay() {
  if (!selectedPaymentMethod.value) {
    ElMessage.warning('请选择支付方式')
    return
  }

  isProcessing.value = true

  try {
    if (selectedPaymentMethod.value === 'balance') {
      // 使用余额支付
      if (userBalance.value < paymentAmount.value) {
        ElMessage.error('余额不足')
        isProcessing.value = false
        return
      }

      await payWithBalance(paymentAmount.value, null, '订单支付')
      userBalance.value -= paymentAmount.value
      ElMessage.success('支付成功！')
    } else if (selectedPaymentMethod.value === 'wechat') {
      ElMessage.success('请扫描微信二维码完成支付')
    } else if (selectedPaymentMethod.value === 'alipay') {
      ElMessage.success('请扫描支付宝二维码完成支付')
    } else if (selectedPaymentMethod.value === 'card') {
      ElMessage.success('正在跳转至银行卡支付页面...')
    }

    isProcessing.value = false

    // 1.5秒后返回
    setTimeout(() => {
      router.back()
    }, 1500)
  } catch (error) {
    console.error('Payment failed:', error)
    ElMessage.error('支付失败，请重试')
    isProcessing.value = false
  }
}

// 充值处理
async function handleTopUp() {
  if (finalTopUpAmount.value <= 0) {
    ElMessage.warning('请输入有效的充值金额')
    return
  }

  isTopUpProcessing.value = true

  try {
    await topupBalance(finalTopUpAmount.value, topUpPaymentMethod.value)
    userBalance.value += finalTopUpAmount.value
    ElMessage.success(`充值成功！已添加 ¥${finalTopUpAmount.value.toFixed(2)} 到账户`)

    // 重置表单
    topUpAmount.value = 50
    customTopUpAmount.value = null
    showTopUpDialog.value = false
    isTopUpProcessing.value = false
  } catch (error) {
    console.error('Top-up failed:', error)
    ElMessage.error('充值失败，请重试')
    isTopUpProcessing.value = false
  }
}

// 页面加载时获取用户余额
onMounted(() => {
  loadUserBalance()
})
</script>

<style scoped>
/* 平滑过渡 */
* {
  transition: all 0.3s ease;
}
</style>
