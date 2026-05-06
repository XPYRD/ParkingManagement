<template>
  <!-- 用户登录 — 独立全屏页面，从 stitch_/_15/code.html 转换 -->
  <div class="min-h-screen flex flex-col font-body bg-surface text-on-surface">
    <!-- 顶部导航 -->
    <nav class="fixed top-0 w-full z-50 bg-surface">
      <div class="flex justify-between items-center px-8 py-4 max-w-7xl mx-auto">
        <router-link to="/" class="text-xl font-bold tracking-tighter text-primary font-headline">
          Sentinel
        </router-link>
        <router-link to="/login" class="text-sm font-semibold text-primary border-b-2 border-primary pb-1">
          Sign In
        </router-link>
      </div>
    </nav>

    <!-- 主体：分栏卡片 -->
    <main class="min-h-screen flex items-center justify-center pt-16 px-4 md:px-0">
      <div class="w-full max-w-5xl grid grid-cols-1 md:grid-cols-12 overflow-hidden rounded-xl shadow-2xl bg-surface-container-lowest">

        <!-- 左侧：品牌视觉 -->
        <div
          class="hidden md:block md:col-span-6 relative min-h-[500px] bg-cover bg-center"
          :style="{ backgroundImage: `url(${heroBg})` }"
        >
          <div class="absolute inset-0 bg-primary/40"></div>
          <div class="absolute bottom-12 left-12 right-12 text-on-primary z-10">
            <h2 class="text-4xl font-bold font-headline leading-tight tracking-tight mb-4">
              城市流动的<br/>智能守护者
            </h2>
            <p class="text-white/80 text-sm max-w-xs leading-relaxed">
              利用 Sentinel 的高精度感应系统，重新定义城市停车的效率与安全。
            </p>
          </div>
          <div class="absolute top-12 left-12 w-16 h-1 bg-white/30"></div>
        </div>

        <!-- 右侧：登录表单 -->
        <div class="col-span-1 md:col-span-6 p-8 md:p-16 flex flex-col justify-center">
          <div class="max-w-md w-full mx-auto">
            <header class="mb-10">
              <h1 class="text-3xl font-extrabold font-headline text-primary tracking-tight mb-2">欢迎回来</h1>
              <p class="text-secondary text-sm">请输入您的凭据以访问控制中心</p>
            </header>

            <el-form
              ref="loginFormRef"
              :model="loginForm"
              :rules="loginRules"
              @submit.prevent="handleLogin"
              class="space-y-6"
            >
              <!-- 手机号/邮箱 -->
              <el-form-item prop="username">
                <label class="block text-xs font-bold text-secondary uppercase tracking-widest ml-1 mb-2">手机号 / 邮箱</label>
                <el-input
                  v-model="loginForm.username"
                  placeholder="输入手机号或常用邮箱"
                  size="large"
                  :prefix-icon="UserIcon"
                />
              </el-form-item>

              <!-- 密码 -->
              <el-form-item prop="password">
                <div class="flex justify-between items-center px-1 mb-2">
                  <label class="block text-xs font-bold text-secondary uppercase tracking-widest">密码</label>
                </div>
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入您的登录密码"
                  size="large"
                  show-password
                  :prefix-icon="LockIcon"
                  @keyup.enter="handleLogin"
                />
              </el-form-item>

              <!-- 记住我 -->
              <div class="flex items-center gap-2 px-1">
                <el-checkbox v-model="rememberMe" label="记住我的登录状态" />
              </div>

              <!-- 登录按钮 -->
              <el-button
                type="primary"
                size="large"
                class="!w-full !py-5 !rounded-xl !font-bold !tracking-tight !text-sm !shadow-lg !shadow-primary/10"
                :loading="loading"
                @click="handleLogin"
              >
                登 录
              </el-button>
            </el-form>

            <!-- 注册跳转 -->
            <footer class="text-center">
              <p class="text-sm text-secondary">
                还没有账号？
                <router-link to="/register" class="text-primary font-bold hover:underline">立即注册</router-link>
              </p>
            </footer>
          </div>
        </div>
      </div>
    </main>

    <!-- 底部 -->
    <footer class="w-full border-t border-outline-variant/15 bg-surface-container-low mt-12">
      <div class="flex flex-col md:flex-row justify-between items-center px-12 py-8 max-w-7xl mx-auto">
        <div class="mb-4 md:mb-0">
          <span class="text-lg font-black text-on-surface font-headline tracking-tighter">Sentinel</span>
          <p class="text-xs text-secondary mt-1">© 2024 Sentinel Parking Systems. All rights reserved.</p>
        </div>
        <div class="flex gap-6">
          <router-link to="/admin/login" class="text-xs text-primary font-bold hover:opacity-80 transition-opacity flex items-center gap-1">
            <span class="material-symbols-outlined text-[14px]">admin_panel_settings</span>
            管理员入口
          </router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
/**
 * 用户登录 — 从 stitch_/_15/code.html 重构
 *
 * 功能：
 * 1. 手机号/邮箱 + 密码登录（JWT）
 * 2. 记住我（localStorage 持久化）
 * 3. 微信/验证码登录占位
 */

import { ref, reactive, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User as UserIcon, Lock as LockIcon } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 左侧背景图 — 对应 Stitch 设计中的停车场建筑图片
const heroBg = 'https://lh3.googleusercontent.com/aida-public/AB6AXuDoabIxhfe0g8-xe3onz8N-uGnQRpWkSM6ZdsRWKAY8A7A5L_K3hSUKxDvfGY1sZtT_o7RKDHBswVSbTKkRFSYVIYwiq7OHkacA3OxfpRFxvkOpcsbEUJXHpWPO37u5lBXmyrLoXiehn-yoqLWjrzvWn6zqEobDDroi7a8imZlmeyODidaCb5FdKoTkup1gVt3OqjhyNF8PV6voB-tuOtHFwxz2cFhMnJCPR8nOsWLH1uQaVW0LDEHKmr_xXH13-Q9GDVhTQ6iLeM4'

const loginFormRef = ref(null)
const loading = ref(false)
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
})

const loginRules = {
  username: [
    { required: true, message: '请输入手机号或邮箱', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
}

/** 处理登录 */
async function handleLogin() {
  if (!loginFormRef.value) return
  try {
    await loginFormRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    await authStore.login({
      username: loginForm.username,
      password: loginForm.password,
    })
    ElMessage.success('登录成功，欢迎回来')
    router.push('/')
  } catch (err) {
    // 错误已由 Axios 拦截器处理
  } finally {
    loading.value = false
  }
}
</script>
