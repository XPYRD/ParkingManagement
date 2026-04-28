<template>
  <!-- 收费管理 -->
  <div class="p-6 lg:p-10">
    <header class="mb-8">
      <h1 class="text-3xl font-extrabold text-primary tracking-tight font-headline">收费管理</h1>
      <p class="text-secondary text-sm mt-1">定价策略配置与账务流水审查</p>
    </header>

    <!-- 顶部聚合统计 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8" v-loading="loadingSummary">
       <div class="bg-gradient-to-br from-primary to-primary-container text-white p-6 rounded-2xl shadow-lg relative overflow-hidden">
          <div class="absolute -right-4 -top-4 opacity-10">
             <span class="material-symbols-outlined" style="font-size: 100px;">account_balance_wallet</span>
          </div>
          <p class="text-white/80 text-xs font-bold uppercase tracking-widest mb-2">累计营收</p>
          <p class="text-4xl font-black font-headline mb-4">¥ {{ (summary.total_revenue || 0).toFixed(2) }}</p>
       </div>

       <!-- 支付方式占比图 -->
       <div class="bg-surface-container-lowest p-6 rounded-2xl shadow-sm border border-outline-variant/20 flex flex-col justify-center">
          <p class="text-sm font-bold text-on-surface mb-4">支付方式分布</p>
          <div class="flex items-center gap-6">
             <div class="relative w-24 h-24 flex-shrink-0">
                <svg viewBox="0 0 100 100" class="transform -rotate-90 w-full h-full">
                   <circle cx="50" cy="50" r="40" fill="none" class="stroke-slate-200" stroke-width="15"/>
                   <!-- 简易分段演示，生产中应使用 echarts -->
                   <circle cx="50" cy="50" r="40" fill="none" class="stroke-green-500" stroke-width="15" stroke-linecap="butt" :stroke-dasharray="`${getPercent('wechat') * 2.51} 251`"/>
                   <circle cx="50" cy="50" r="40" fill="none" class="stroke-blue-500" stroke-width="15" stroke-linecap="butt" :stroke-dasharray="`${getPercent('alipay') * 2.51} 251`" :stroke-dashoffset="`-${getPercent('wechat') * 2.51}`"/>
                </svg>
             </div>
             <div class="space-y-2 text-xs flex-1">
                <div class="flex justify-between items-center"><div class="flex items-center gap-1.5"><div class="w-2.5 h-2.5 bg-green-500 rounded-sm"></div><span>微信</span></div><span class="font-bold">{{ getPercent('wechat') }}%</span></div>
                <div class="flex justify-between items-center"><div class="flex items-center gap-1.5"><div class="w-2.5 h-2.5 bg-blue-500 rounded-sm"></div><span>支付宝</span></div><span class="font-bold">{{ getPercent('alipay') }}%</span></div>
                <div class="flex justify-between items-center"><div class="flex items-center gap-1.5"><div class="w-2.5 h-2.5 bg-primary/20 rounded-sm"></div><span>其他</span></div><span class="font-bold">{{ getPercent('balance') + getPercent('cash') }}%</span></div>
             </div>
          </div>
       </div>

       <div class="bg-surface-container-lowest p-6 rounded-2xl shadow-sm border border-outline-variant/20">
          <p class="text-sm font-bold text-on-surface mb-4">客单价 (ARPU)</p>
          <p class="text-3xl font-black font-headline text-primary mb-2">¥ {{ (summary.avg_amount || 0).toFixed(2) }}</p>
          <p class="text-xs text-secondary leading-relaxed">
             基于当前计费规则下的平均每车次收益，建议适时调整高峰时段附加费率以优化整体运营收入。
          </p>
       </div>
    </div>

    <!-- 定价规则配置区 -->
    <div class="mb-8" v-loading="loadingRules">
       <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-bold text-on-surface">定价规则</h2>
          <el-button type="primary" plain size="small"><span class="material-symbols-outlined text-sm mr-1">add</span>新增规则</el-button>
       </div>
       <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="rule in pricingRules" :key="rule.id" class="bg-surface-container-lowest p-5 rounded-xl border border-outline-variant/20 hover:border-primary/50 transition-colors cursor-pointer group">
             <div class="flex justify-between items-start mb-3">
                <span class="font-bold text-sm text-on-surface">{{ rule.name }}</span>
                <el-switch v-model="rule.is_active" size="small" @change="toggleRule(rule)" />
             </div>
             <p class="text-2xl font-extrabold text-primary font-headline mb-1">¥ {{ rule.price }}</p>
             <p class="text-xs text-secondary">{{ rule.rate_type === 'hourly' ? '按小时' : (rule.rate_type === 'daily' ? '按天' : '按月') }}</p>
          </div>
       </div>
    </div>

    <!-- 交易明细表格 -->
    <div class="bg-surface-container-lowest p-5 rounded-2xl border border-outline-variant/20" v-loading="loadingTransactions">
       <div class="flex justify-between items-center mb-4">
          <h2 class="text-lg font-bold text-on-surface">近期交易日志</h2>
          <el-input v-model="searchTx" placeholder="搜索交易单号..." size="small" class="w-64" clearable @change="loadTransactions">
             <template #prefix><span class="material-symbols-outlined text-sm">search</span></template>
          </el-input>
       </div>
       <el-table :data="transactions" style="width: 100%" stripe size="small">
          <el-table-column prop="transaction_id" label="交易单号" width="180" />
          <el-table-column prop="created_at" label="交易时间" width="160">
             <template #default="{ row }">{{ new Date(row.created_at).toLocaleString() }}</template>
          </el-table-column>
          <el-table-column prop="payment_type" label="业务类型" width="100">
             <template #default="{ row }">{{ row.payment_type_label || (row.payment_type === 'parking' ? '临时停车' : '包月续费') }}</template>
          </el-table-column>
          <el-table-column prop="amount" label="金额(¥)" width="120">
             <template #default="{ row }"><span class="font-bold">¥ {{ row.amount }}</span></template>
          </el-table-column>
          <el-table-column prop="method_label" label="支付渠道">
             <template #default="{ row }">
               {{ row.method_label || (row.method === 'wechat' ? '微信支付' : (row.method === 'alipay' ? '支付宝' : row.method)) }}
             </template>
          </el-table-column>
          <el-table-column prop="status" label="状态">
             <template #default="{ row }">
                <el-tag size="small" :type="row.status === 'success' ? 'success' : (row.status === 'pending' ? 'warning' : 'danger')">
                   {{ row.status_label || (row.status === 'success' ? '成功' : '处理中') }}
                </el-tag>
             </template>
          </el-table-column>
       </el-table>
       <div class="p-4 flex justify-end">
          <el-pagination 
             v-model:current-page="txPage" 
             layout="prev, pager, next" 
             :total="txTotal"
             @current-change="loadTransactions"
          />
       </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 收费管理后台 — 接入 API 真实数据
 */
import { ref, onMounted } from 'vue'
import { getPricingRules, getRevenueSummary, getPayments, updatePricingRule } from '@/api/payment'
import { ElMessage } from 'element-plus'

const loadingSummary = ref(false)
const loadingRules = ref(false)
const loadingTransactions = ref(false)

const summary = ref({})
const pricingRules = ref([])
const transactions = ref([])
const searchTx = ref('')

const txPage = ref(1)
const txTotal = ref(0)

onMounted(() => {
  loadSummary()
  loadRules()
  loadTransactions()
})

const loadSummary = async () => {
   loadingSummary.value = true
   try {
      const res = await getRevenueSummary()
      summary.value = res
   } catch(e) {
      console.error(e)
   } finally {
      loadingSummary.value = false
   }
}

const getPercent = (method) => {
   if (!summary.value.method_breakdown) return 0
   const item = summary.value.method_breakdown.find(m => m.method === method)
   if (!item || !summary.value.total_revenue) return 0
   return Math.round((item.total / summary.value.total_revenue) * 100)
}

const loadRules = async () => {
   loadingRules.value = true
   try {
      const res = await getPricingRules()
      pricingRules.value = res.results || res
   } catch(e) {
      console.error(e)
   } finally {
      loadingRules.value = false
   }
}

const toggleRule = async (rule) => {
   try {
      // 可以在此处调用 API
      await updatePricingRule(rule.id, { is_active: rule.is_active })
      ElMessage.success('状态已更改')
   } catch (e) {
      rule.is_active = !rule.is_active
      ElMessage.error('更改失败')
   }
}

const loadTransactions = async () => {
   loadingTransactions.value = true
   try {
      const params = { page: txPage.value }
      if (searchTx.value) params.search = searchTx.value
      const res = await getPayments(params)
      
      if (res.results) {
         transactions.value = res.results
         txTotal.value = res.count
      } else {
         transactions.value = res
         txTotal.value = res.length
      }
   } catch(e) {
      ElMessage.error('无法加载交易记录')
   } finally {
      loadingTransactions.value = false
   }
}
</script>
