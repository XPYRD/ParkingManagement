<template>
  <!-- 用户注册 — 从 stitch_/_14/code.html 转换 -->
  <div class="min-h-screen flex items-center justify-center px-4 py-12 bg-surface font-body">
    <div class="w-full max-w-5xl grid grid-cols-1 md:grid-cols-12 rounded-xl shadow-2xl overflow-hidden bg-surface-container-lowest">

      <!-- 左侧品牌视觉区 -->
      <div
        class="hidden md:flex md:col-span-6 flex-col justify-between p-12 relative overflow-hidden min-h-[640px] bg-cover bg-center"
        :style="{ backgroundImage: `url(${heroBg})` }"
      >
        <div class="absolute inset-0 bg-primary/50"></div>
        <div class="relative z-10">
          <div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center mb-6">
            <span class="text-white text-2xl font-black font-headline">S</span>
          </div>
          <h2 class="text-5xl font-extrabold text-white font-headline leading-tight tracking-tight mb-4">
            开启高效停车<br/>管理新纪元
          </h2>
          <p class="text-white/80 text-lg max-w-xs leading-relaxed">
            加入 Sentinel 停车系统，体验前所未有的智慧城市流动。
          </p>
        </div>
        <div class="relative z-10 flex gap-3 items-center text-white/60 text-xs">
          <span class="material-symbols-outlined text-sm">shield</span>
          <span>数据加密传输 · 隐私安全保障</span>
        </div>
      </div>

      <!-- 右侧注册表单 -->
      <div class="col-span-1 md:col-span-6 p-8 md:p-14 flex flex-col justify-center">
        <div class="max-w-md w-full mx-auto">
          <header class="mb-10">
            <h1 class="text-3xl font-extrabold font-headline text-primary tracking-tight mb-2">创建您的账户</h1>
            <p class="text-secondary text-sm">请填写以下信息以完成注册。</p>
          </header>

          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            @submit.prevent="handleRegister"
            class="space-y-5"
          >
            <!-- 手机号 -->
            <el-form-item prop="phone">
              <label class="block text-xs font-bold text-secondary uppercase tracking-widest ml-1 mb-2">手机号</label>
              <el-input
                v-model="form.phone"
                placeholder="请输入11位手机号码"
                maxlength="11"
                size="large"
              >
                <template #prefix>
                  <span class="material-symbols-outlined text-secondary">smartphone</span>
                </template>
              </el-input>
            </el-form-item>

            <!-- 验证码 -->
            <el-form-item prop="smsCode">
              <label class="block text-xs font-bold text-secondary uppercase tracking-widest ml-1 mb-2">验证码</label>
              <div class="flex gap-3">
                <el-input
                  v-model="form.smsCode"
                  placeholder="请输入验证码"
                  maxlength="6"
                  size="large"
                  class="flex-1"
                >
                  <template #prefix>
                    <span class="material-symbols-outlined text-secondary">verified_user</span>
                  </template>
                </el-input>
                <el-button
                  size="large"
                  :disabled="smsCountdown > 0"
                  @click="handleSendSms"
                  class="!min-w-[120px]"
                >
                  {{ smsCountdown > 0 ? `${smsCountdown}s 后重发` : '发送验证码' }}
                </el-button>
              </div>
            </el-form-item>

            <!-- 密码 -->
            <el-form-item prop="password">
              <label class="block text-xs font-bold text-secondary uppercase tracking-widest ml-1 mb-2">设置密码</label>
              <el-input
                v-model="form.password"
                type="password"
                placeholder="设置8-16位强密码"
                size="large"
                show-password
              >
                <template #prefix>
                  <span class="material-symbols-outlined text-secondary">lock</span>
                </template>
              </el-input>
            </el-form-item>

            <!-- 确认密码 -->
            <el-form-item prop="password_confirm">
              <label class="block text-xs font-bold text-secondary uppercase tracking-widest ml-1 mb-2">确认密码</label>
              <el-input
                v-model="form.password_confirm"
                type="password"
                placeholder="请再次输入密码"
                size="large"
                show-password
              >
                <template #prefix>
                  <span class="material-symbols-outlined text-secondary">lock</span>
                </template>
              </el-input>
            </el-form-item>

            <!-- 协议 -->
            <el-form-item prop="agreement">
              <el-checkbox v-model="form.agreement">
                <span class="text-xs text-secondary">
                  我已阅读并同意
                  <a class="text-primary font-semibold">服务条款</a>
                  和
                  <a class="text-primary font-semibold">隐私政策</a>
                </span>
              </el-checkbox>
            </el-form-item>

            <!-- 注册按钮 -->
            <el-button
              type="primary"
              size="large"
              class="!w-full !py-5 !rounded-xl !font-bold !text-sm !shadow-lg !shadow-primary/10"
              :loading="loading"
              @click="handleRegister"
            >
              注 册
            </el-button>
          </el-form>

          <!-- 登录跳转 -->
          <footer class="text-center mt-8">
            <p class="text-sm text-secondary">
              已有账号？
              <router-link to="/login" class="text-primary font-bold hover:underline">返回登录</router-link>
            </p>
          </footer>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 用户注册 — 从 stitch_/_14/code.html 重构
 */

import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '@/api/user'

const router = useRouter()

const heroBg = 'https://lh3.googleusercontent.com/aida-public/AB6AXuBS7XN1oY_iJRzPWnB905TXcq4u2F6JvYDxzg7cN6Pf7yiw-aEuM1Fs88HRBbk_5GWZmunACVqjJfYfqn-V0o0nlolp_DFIVJUiCXuVjT1hcO-7XT-JVbXPGSdhDhSGON0IHSIJoSYjCMFRSidHEhtZ2F2OU7nEj9KWFBpxMgaYIdmE3R6LrcPfNaSUF2fpVILqVrNGiAzHaH2bkpR1M2huxgQAk4g3gTl_h4V0OGmr2vWPKQO75VQwycCk9Q3cK-CJ2xCWUkiJiMi'

const formRef = ref(null)
const loading = ref(false)
const smsCountdown = ref(0)

const form = reactive({
  phone: '',
  smsCode: '',
  password: '',
  password_confirm: '',
  agreement: false,
})

/** 密码一致性校验 */
const validatePasswordConfirm = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  smsCode: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请设置密码', trigger: 'blur' },
    { min: 8, max: 16, message: '密码长度 8-16 位', trigger: 'blur' },
  ],
  password_confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePasswordConfirm, trigger: 'blur' },
  ],
  agreement: [
    { validator: (r, v, cb) => v ? cb() : cb(new Error('请阅读并同意服务条款')), trigger: 'change' },
  ],
}

/** 发送短信验证码 */
function handleSendSms() {
  if (!form.phone || !/^1[3-9]\d{9}$/.test(form.phone)) {
    ElMessage.warning('请先输入正确的手机号')
    return
  }
  // TODO: 调用后端短信接口
  ElMessage.success('验证码已发送（开发模式：123456）')
  smsCountdown.value = 60
  const timer = setInterval(() => {
    smsCountdown.value--
    if (smsCountdown.value <= 0) clearInterval(timer)
  }, 1000)
}

/** 处理注册 */
async function handleRegister() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    await register({
      phone: form.phone,
      password: form.password,
      password_confirm: form.password_confirm,
    })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (err) {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}
</script>
