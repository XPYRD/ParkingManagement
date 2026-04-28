<template>
  <!-- 管理员个人资料页面 -->
  <div class="px-6 py-8 max-w-4xl mx-auto">
    <header class="mb-10">
      <h1 class="text-3xl font-extrabold text-primary tracking-tight font-headline">管理员个人设置</h1>
      <p class="text-secondary text-sm mt-2">管理您的管理员账号凭据与系统通知偏好。</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-12 gap-8">
      <!-- 左侧：头像与概览 -->
      <div class="md:col-span-4 gap-6 flex flex-col">
        <div class="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm text-center">
          <el-avatar :size="100" src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png" class="border-4 border-slate-50 shadow-md mb-6" />
          <h2 class="text-xl font-bold text-slate-800">{{ profile.username }}</h2>
          <div class="mt-3 inline-flex items-center gap-1.5 bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
            <span class="material-symbols-outlined text-sm">shield</span>
            超级管理员
          </div>
          <p class="text-[10px] text-slate-400 mt-6 uppercase font-bold tracking-widest">最后登录</p>
          <p class="text-xs text-slate-600 mt-1">{{ profile.last_login || '刚刚' }}</p>
        </div>

        <div class="bg-slate-900 rounded-2xl p-6 text-white shadow-xl">
          <h3 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">系统安全摘要</h3>
          <div class="space-y-4">
            <div class="flex justify-between items-center text-sm">
              <span class="text-slate-400">账号状态</span>
              <span class="text-green-400 flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                已激活
              </span>
            </div>
            <div class="flex justify-between items-center text-sm">
              <span class="text-slate-400">两步验证 (2FA)</span>
              <span :class="profile.two_factor_enabled ? 'text-primary font-bold' : 'text-slate-500'">
                {{ profile.two_factor_enabled ? '已开启' : '未开启' }}
              </span>
            </div>
          </div>
        </div>

        <!-- 2FA 控制卡片 -->
        <div class="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
          <div class="flex items-center gap-3 mb-4">
            <span class="material-symbols-outlined text-primary">verified_user</span>
            <h3 class="text-sm font-bold text-slate-800 uppercase tracking-widest">安全增强</h3>
          </div>
          <p class="text-xs text-secondary leading-relaxed mb-6">
            开启两步验证后，登录需要输入 Google Authenticator 等应用生成的 6 位动态验证码。
          </p>
          <el-button 
            :type="profile.two_factor_enabled ? 'danger' : 'primary'" 
            plain 
            class="!w-full !rounded-xl !py-5"
            @click="handleToggle2FA"
          >
            {{ profile.two_factor_enabled ? '注销两步验证' : '立即去开启' }}
          </el-button>
        </div>
      </div>

      <!-- 2FA 绑定弹窗 -->
      <el-dialog
        v-model="show2FAModal"
        title="绑定两步验证"
        width="400px"
        append-to-body
        class="rounded-2xl"
      >
        <div class="flex flex-col items-center">
          <p class="text-xs text-secondary mb-6 text-center px-4">
            请使用 Google Authenticator 或 Microsoft Authenticator 扫描下方二维码：
          </p>
          
          <div class="p-4 bg-white border rounded-xl mb-6">
            <qrcode-vue v-if="setupData.otpauth_url" :value="setupData.otpauth_url" :size="200" level="H" />
          </div>

          <div class="w-full space-y-4">
            <div>
              <label class="block text-[10px] font-bold text-secondary uppercase tracking-widest mb-2 ml-1">输入 6 位验证码以激活</label>
              <el-input 
                v-model="activationCode" 
                placeholder="000000" 
                maxlength="6" 
                size="large"
                class="text-center tracking-[0.5em] font-mono"
              />
            </div>
            <el-button 
              type="primary" 
              class="!w-full !rounded-xl !py-6" 
              :loading="activating"
              @click="confirmActivate2FA"
            >
              验证并开启
            </el-button>
          </div>
        </div>
      </el-dialog>

      <!-- 右侧：表单设置 -->
      <div class="md:col-span-8">
        <div class="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm h-full">
          <h3 class="text-sm font-bold text-slate-800 uppercase tracking-widest mb-6">基本信息设置</h3>
          
          <el-form label-position="top" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <el-form-item label="管理员用户名">
                <el-input v-model="profile.username" size="large" readonly disabled />
              </el-form-item>
              <el-form-item label="联系手机号">
                <el-input v-model="profile.phone" size="large" />
              </el-form-item>
            </div>

            <el-form-item label="工作邮箱">
              <el-input v-model="profile.email" size="large" placeholder="admin@example.com">
                <template #prefix>
                  <span class="material-symbols-outlined text-slate-400">mail</span>
                </template>
              </el-input>
            </el-form-item>

            <el-divider class="!my-8" />

            <h3 class="text-sm font-bold text-slate-800 uppercase tracking-widest mb-6">安全选项</h3>
            
            <div class="space-y-6">
              <div class="flex items-center justify-between group">
                <div>
                  <p class="text-sm font-bold text-slate-700">紧急停场通知</p>
                  <p class="text-xs text-slate-500 mt-0.5">当发生火灾或安全闯入时立即推送</p>
                </div>
                <el-switch v-model="notifications.emergency" />
              </div>
              
              <div class="flex items-center justify-between group">
                <div>
                  <p class="text-sm font-bold text-slate-700">日度营收报告</p>
                  <p class="text-xs text-slate-500 mt-0.5">每天凌晨 2:00 发送至您的邮箱</p>
                </div>
                <el-switch v-model="notifications.dailyReport" />
              </div>
            </div>

            <div class="pt-8">
              <el-button type="primary" size="large" class="!w-full !py-6 !text-sm !font-bold !rounded-xl !shadow-lg !shadow-primary/20" :loading="saving" @click="handleSave">
                保存管理员设置
              </el-button>
            </div>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getProfile, updateProfile } from '@/api/user'
import request from '@/api/request' // 用于调用 2FA 接口
import { ElMessage, ElMessageBox } from 'element-plus'
import QrcodeVue from 'qrcode.vue'

const profile = ref({
  username: '',
  phone: '',
  email: '',
  last_login: ''
})

const notifications = reactive({
  emergency: true,
  dailyReport: true
})

const saving = ref(false)

onMounted(async () => {
  try {
    const data = await getProfile()
    profile.value = data
  } catch (err) {
    ElMessage.error('无法获取管理员资料')
  }
})

async function handleSave() {
  saving.value = true
  try {
    await updateProfile({
      phone: profile.value.phone,
      email: profile.value.email
    })
    ElMessage.success('配置已更新')
  } catch (err) {
    ElMessage.error('更新失败')
  } finally {
    saving.value = false
  }
}

// ---- 2FA 逻辑 ----
const show2FAModal = ref(false)
const activating = ref(false)
const activationCode = ref('')
const setupData = ref({ secret: '', otpauth_url: '' })

async function handleToggle2FA() {
  if (profile.value.two_factor_enabled) {
    ElMessageBox.confirm('确定要关闭两步验证吗？这将降低账号安全性。', '安全警告', {
      type: 'warning',
      confirmButtonText: '确定关闭',
      confirmButtonClass: 'el-button--danger'
    }).then(async () => {
      // 此处简化处理：直接调用后端关闭（实际生产可能需要验证密码或验证码）
      await updateProfile({ two_factor_enabled: false })
      profile.value.two_factor_enabled = false
      ElMessage.success('两步验证已关闭')
    })
    return
  }

  // 获取设置信息
  try {
    const res = await request.post('/accounts/2fa/setup/')
    setupData.value = res
    show2FAModal.value = true
  } catch (err) {
    ElMessage.error('无法初始化 2FA 设置')
  }
}

async function confirmActivate2FA() {
  if (activationCode.value.length !== 6) {
    return ElMessage.warning('请输入 6 位验证码')
  }
  activating.value = true
  try {
    await request.post('/accounts/2fa/activate/', { code: activationCode.value })
    ElMessage.success('两步验证已成功开启')
    show2FAModal.value = false
    profile.value.two_factor_enabled = true
    activationCode.value = ''
  } catch (err) {
    // 错误已拦截
  } finally {
    activating.value = false
  }
}
</script>

