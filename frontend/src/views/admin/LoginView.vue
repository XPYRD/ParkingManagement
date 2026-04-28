<template>
  <!-- 管理员登录 — 从 stitch_/_6/code.html 转换 -->
  <div class="min-h-screen flex items-center justify-center bg-surface font-body px-4">
    <div class="w-full max-w-md relative">
      <!-- 浮动装饰 -->
      <div class="absolute -top-20 -right-20 w-60 h-60 bg-primary/5 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-20 -left-20 w-40 h-40 bg-tertiary-fixed/10 rounded-full blur-2xl"></div>

      <!-- 登录卡片 -->
      <div class="bg-surface-container-lowest rounded-2xl shadow-2xl p-10 relative overflow-hidden">
        <!-- 顶部渐变条 -->
        <div class="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-primary via-primary-container to-primary"></div>

        <!-- Logo 区域 -->
        <div class="text-center mb-10">
          <div class="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
            <span class="material-symbols-outlined text-primary text-3xl">admin_panel_settings</span>
          </div>
          <h1 class="text-2xl font-extrabold text-primary tracking-tight font-headline">Sentinel 管理后台</h1>
          <p class="text-secondary text-sm mt-2">请输入管理员凭据以访问系统</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          @submit.prevent="handleLogin"
          class="space-y-5"
        >
          <!-- 用户名 -->
          <el-form-item prop="username">
            <label class="block text-xs font-bold text-secondary uppercase tracking-widest mb-2">管理员账号</label>
            <el-input
              v-model="form.username"
              placeholder="请输入管理员账号"
              size="large"
            >
              <template #prefix>
                <span class="material-symbols-outlined text-secondary text-lg">person</span>
              </template>
            </el-input>
          </el-form-item>

          <!-- 密码 -->
          <el-form-item prop="password">
            <label class="block text-xs font-bold text-secondary uppercase tracking-widest mb-2">密码</label>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入管理员密码"
              size="large"
              show-password
              @keyup.enter="handleLogin"
            >
              <template #prefix>
                <span class="material-symbols-outlined text-secondary text-lg">lock</span>
              </template>
            </el-input>
          </el-form-item>

          <!-- 验证码 -->
          <el-form-item prop="captcha">
            <label class="block text-xs font-bold text-secondary uppercase tracking-widest mb-2">安全验证码</label>
            <div class="flex gap-3">
              <el-input
                v-model="form.captcha"
                placeholder="输入验证码"
                maxlength="4"
                size="large"
                class="flex-1"
              >
                <template #prefix>
                  <span class="material-symbols-outlined text-secondary text-lg">shield</span>
                </template>
              </el-input>
              <div
                class="w-28 h-10 rounded-lg bg-surface-container-high flex items-center justify-center cursor-pointer select-none"
                @click="refreshCaptcha"
              >
                <span class="text-xl font-black tracking-[0.3em] text-primary" style="font-family: monospace;">
                  {{ captchaCode }}
                </span>
              </div>
            </div>
          </el-form-item>

          <!-- 登录按钮 -->
          <el-button
            type="primary"
            size="large"
            class="!w-full !py-5 !rounded-xl !font-bold !text-sm !shadow-lg !shadow-primary/10"
            :loading="loading"
            @click="handleLogin"
          >
            安全登录
          </el-button>
        </el-form>

        <!-- 安全提示 -->
        <div class="mt-8 p-4 rounded-xl bg-surface-container-low">
          <div class="flex items-start gap-3">
            <span class="material-symbols-outlined text-secondary text-lg mt-0.5">info</span>
            <div>
              <p class="text-xs font-bold text-on-surface mb-1">系统安全提示</p>
              <p class="text-xs text-secondary leading-relaxed">
                请在安全网络环境下登录管理后台。连续5次输错密码将锁定账户30分钟。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 2FA 验证弹窗 -->
    <el-dialog
      v-model="showVerifyModal"
      title="两步安全验证"
      width="380px"
      :close-on-click-modal="false"
      class="rounded-2xl"
      append-to-body
    >
      <div class="flex flex-col items-center py-4">
        <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-6">
          <span class="material-symbols-outlined text-primary text-3xl">domain_verification</span>
        </div>
        <p class="text-sm font-bold text-slate-800 mb-2">输入动态验证码</p>
        <p class="text-xs text-secondary text-center mb-8">请打开您的身份验证器 App (如 Google Authenticator) 查看 6 位数字码</p>
        
        <el-input 
          v-model="otpCode" 
          placeholder="000 000" 
          maxlength="6" 
          size="large"
          class="text-center tracking-[0.5em] font-mono text-xl mb-8"
          @keyup.enter="handleVerify2FA"
        />

        <el-button 
          type="primary" 
          size="large" 
          class="!w-full !py-6 !rounded-xl !font-bold"
          :loading="verifying"
          @click="handleVerify2FA"
        >
          立即验证并进入
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>


<script setup>
/**
 * 管理员登录 — 从 stitch_/_6/code.html 重构
 */

import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const captchaCode = ref('A3X7')

const form = reactive({
  username: '',
  password: '',
  captcha: '',
})

const rules = {
  username: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captcha: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
}

/** 生成随机验证码 */
function refreshCaptcha() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  captchaCode.value = Array.from({ length: 4 }, () => chars[Math.floor(Math.random() * chars.length)]).join('')
}

onMounted(refreshCaptcha)

const showVerifyModal = ref(false)
const verifying = ref(false)
const otpCode = ref('')

async function handleLogin() {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }

  // 校验验证码（前端简单校验）
  if (form.captcha.toUpperCase() !== captchaCode.value) {
    ElMessage.error('验证码错误')
    refreshCaptcha()
    return
  }

  loading.value = true
  try {
    const res = await authStore.login({
      username: form.username,
      password: form.password,
    })
    
    // 如果需要两步验证，弹出弹窗
    if (res && res.requires_2fa) {
      showVerifyModal.value = true
      return
    }

    ElMessage.success('登录成功')
    router.push('/admin/dashboard')
  } catch {
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}

/** 提交二级验证码 */
async function handleVerify2FA() {
  if (otpCode.value.length !== 6) {
    return ElMessage.warning('请输入 6 位数字码')
  }
  
  verifying.value = true
  try {
    await authStore.verify2FA({
      username: form.username,
      password: form.password,
      code: otpCode.value
    })
    ElMessage.success('身份认证成功')
    router.push('/admin/dashboard')
    showVerifyModal.value = false
  } catch (err) {
    // 错误由拦截器处理
  } finally {
    verifying.value = false
  }
}
</script>

