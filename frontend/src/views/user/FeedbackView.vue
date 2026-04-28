<template>
  <!-- 故障/投诉反馈 -->
  <div class="px-4 md:px-8 max-w-7xl mx-auto py-8">
    <header class="mb-8 text-center max-w-2xl mx-auto">
      <h1 class="text-3xl font-extrabold text-primary tracking-tight font-headline">服务反馈</h1>
      <p class="text-secondary text-sm mt-2">设备故障、服务投诉或建议，您的每一次反馈都帮助我们做得更好。</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
      <!-- 左侧：工单列表 -->
      <div class="md:col-span-5 lg:col-span-4 space-y-4">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-on-surface">我的反馈记录</h2>
        </div>
        
        <div v-loading="loadingTickets">
          <div 
             v-for="ticket in tickets" 
             :key="ticket.id"
             class="bg-surface-container-lowest p-4 rounded-2xl border border-outline-variant/20 hover:shadow-md transition-shadow cursor-pointer mb-4"
             :class="{'border-primary bg-primary/5': selectedTicket?.id === ticket.id}"
             @click="selectedTicket = ticket"
             >
             <div class="flex justify-between items-start mb-2">
                <span class="text-xs font-bold uppercase tracking-widest text-secondary">#{{ ticket.ticket_id || ticket.id }}</span>
                <el-tag size="small" :type="ticket.status === 'resolved' ? 'success' : (ticket.status === 'in_progress' ? 'warning' : 'info')" effect="plain" class="!font-bold rounded-full">
                   {{ ticket.status_label || (ticket.status === 'pending' ? '待处理' : (ticket.status === 'in_progress' ? '处理中' : '已解决')) }}
                </el-tag>
             </div>
             <h3 class="font-bold text-on-surface text-sm mb-1 leading-snug">{{ ticket.title }}</h3>
             <p class="text-xs text-secondary mb-3">{{ new Date(ticket.created_at).toLocaleDateString() }}</p>
             <div class="flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full" :class="ticket.ticket_type === 'fault' ? 'bg-error' : (ticket.ticket_type === 'complaint' ? 'bg-amber-500' : 'bg-primary')"></span>
                <span class="text-xs font-semibold text-on-surface">
                  {{ ticket.ticket_type === 'fault' ? '设备故障' : (ticket.ticket_type === 'complaint' ? '服务投诉' : '功能建议') }}
                </span>
             </div>
          </div>
          
          <div v-if="tickets.length === 0" class="text-center p-8 bg-surface-container-lowest border border-dashed rounded-2xl text-secondary">
            暂无反馈记录
          </div>
        </div>
      </div>

      <!-- 右侧：提交新反馈 / 查看详情 -->
      <div class="md:col-span-7 lg:col-span-8 bg-surface-container-lowest p-6 md:p-10 rounded-2xl border border-outline-variant/20 shadow-sm">
        
        <div class="flex justify-between items-center mb-8 pb-4 border-b border-outline-variant/20">
           <h2 class="text-xl font-bold font-headline text-on-surface">{{ selectedTicket ? '反馈详情' : '提交新反馈' }}</h2>
           <el-button type="primary" plain size="small" @click="selectedTicket = null" v-if="selectedTicket">
              + 新建反馈
           </el-button>
        </div>

        <el-form v-if="!selectedTicket" :model="form" class="space-y-6" label-position="top">
           <el-form-item label="反馈类型">
              <el-select v-model="form.ticket_type" placeholder="请选择类型" size="large" class="w-full">
                 <el-option label="设备故障 (例如：道闸不抬杆、车位锁故障)" value="fault" />
                 <el-option label="服务投诉 (例如：现场人员态度、计费异常)" value="complaint" />
                 <el-option label="功能建议 (例如：改进 App 界面)" value="suggestion" />
                 <el-option label="其他" value="other" />
              </el-select>
           </el-form-item>

           <el-form-item label="简短标题">
              <el-input v-model="form.title" placeholder="如：北入口A车位充电桩无法扫码" size="large" />
           </el-form-item>

           <el-form-item label="详细描述">
              <el-input 
                v-model="form.description" 
                type="textarea" 
                rows="4" 
                placeholder="请详细描述您遇到的问题发生的时间、位置及具体表现，以便我们快速排查。"
              />
           </el-form-item>

           <el-button type="primary" size="large" class="!px-10 !rounded-xl !font-bold" :loading="submitting" @click="submitTicket">
              提交反馈
           </el-button>
        </el-form>

        <!-- 查看详情状态 -->
        <div v-else class="space-y-6 animate-fade-in">
           <div class="flex items-center gap-3">
             <div class="w-12 h-12 bg-primary/10 rounded-full flex flex-shrink-0 items-center justify-center">
                <span class="material-symbols-outlined text-primary text-xl">confirmation_number</span>
             </div>
             <div>
                <h3 class="text-xl font-bold font-headline text-on-surface">{{ selectedTicket.title }}</h3>
                <p class="text-sm text-secondary">#{{ selectedTicket.ticket_id || selectedTicket.id }} · {{ new Date(selectedTicket.created_at).toLocaleString() }}</p>
             </div>
           </div>

           <div class="p-4 bg-surface-container-low rounded-xl text-sm leading-relaxed text-on-surface">
              {{ selectedTicket.description }}
           </div>

           <div class="border-t border-outline-variant/20 pt-6">
              <h4 class="font-bold text-sm text-on-surface mb-4">处理进度</h4>
              <el-timeline>
                 <el-timeline-item :timestamp="new Date(selectedTicket.created_at).toLocaleString()" type="primary" :hollow="true">工单已提交，等待排查处理。</el-timeline-item>
                 <el-timeline-item v-if="selectedTicket.status !== 'pending' && selectedTicket.status !== 'closed'" :timestamp="new Date(selectedTicket.updated_at).toLocaleString()" type="warning" :hollow="true">人员正在跟进处理中。</el-timeline-item>
                 <el-timeline-item v-if="selectedTicket.status === 'resolved' || selectedTicket.status === 'closed'" :timestamp="new Date(selectedTicket.updated_at).toLocaleString()" type="success">工单已关闭/解决。</el-timeline-item>
              </el-timeline>
           </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getTickets, createTicket } from '@/api/alert'

const form = reactive({
  ticket_type: '',
  title: '',
  description: '',
})

const tickets = ref([])
const selectedTicket = ref(null)
const loadingTickets = ref(false)
const submitting = ref(false)

onMounted(() => {
  loadTickets()
})

const loadTickets = async () => {
  loadingTickets.value = true
  try {
    const res = await getTickets()
    tickets.value = res.results || res
  } catch (err) {
    ElMessage.error('获取工单失败')
  } finally {
    loadingTickets.value = false
  }
}

const submitTicket = async () => {
  if (!form.ticket_type || !form.title || !form.description) {
    ElMessage.warning('请完整填写反馈内容')
    return
  }
  
  submitting.value = true
  try {
    await createTicket({
      ticket_type: form.ticket_type,
      title: form.title,
      description: form.description
    })
    ElMessage.success('提交成功！')
    form.type = ''
    form.title = ''
    form.description = ''
    await loadTickets()
  } catch (err) {
    ElMessage.error('提交失败，请稍后再试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
