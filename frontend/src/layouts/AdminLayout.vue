<template>
  <!-- 管理端布局：左侧边栏 + 主内容区 -->
  <div class="min-h-screen bg-surface flex">
    <!-- ===== 侧边导航栏（桌面端固定 256px） ===== -->
    <aside
      class="hidden md:flex h-screen w-64 fixed left-0 top-0 bg-slate-50 flex-col p-4 border-r border-slate-200 z-40"
    >
      <!-- 品牌区域 -->
      <div class="mb-10 px-2">
        <span class="text-lg font-black text-primary uppercase tracking-wider font-headline">
          停车系统后台
        </span>
        <p class="text-xs text-secondary mt-1 font-medium">系统控制台</p>
      </div>

      <!-- 导航菜单 -->
      <nav class="flex-1 space-y-1">
        <router-link
          v-for="item in sideNavItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-4 py-3 text-slate-500 hover:bg-slate-200 rounded-xl hover:translate-x-1 transition-transform duration-200 font-medium"
          active-class="!bg-white !text-primary !font-semibold shadow-sm"
        >
          <span class="material-symbols-outlined">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- 底部操作区 -->
      <div class="mt-auto border-t border-slate-200 pt-4 space-y-1">
        <button
          class="w-full bg-primary text-white py-3 rounded-xl font-bold text-sm mb-4 active:scale-95 duration-150"
        >
          生成报表
        </button>
        <a
          href="#"
          class="flex items-center gap-3 px-4 py-2 text-slate-500 hover:bg-slate-200 rounded-xl"
        >
          <span class="material-symbols-outlined">help</span>
          <span class="font-medium text-sm">帮助中心</span>
        </a>
        <button
          class="flex items-center gap-3 px-4 py-2 text-slate-500 hover:bg-slate-200 rounded-xl w-full"
          @click="handleLogout"
        >
          <span class="material-symbols-outlined">logout</span>
          <span class="font-medium text-sm">退出登录</span>
        </button>
      </div>
    </aside>

    <!-- ===== 移动端底部导航（简化版） ===== -->
    <nav
      class="md:hidden fixed bottom-0 left-0 w-full z-50 bg-white/90 backdrop-blur-md flex justify-around items-center px-4 pt-2 pb-6 border-t border-slate-200"
    >
      <router-link
        v-for="tab in mobileTabs"
        :key="tab.path"
        :to="tab.path"
        class="flex flex-col items-center justify-center text-slate-400"
        active-class="!text-primary"
      >
        <span class="material-symbols-outlined">{{ tab.icon }}</span>
        <span class="text-[10px] font-semibold">{{ tab.label }}</span>
      </router-link>
    </nav>

    <!-- ===== 主内容区 ===== -->
    <main class="md:ml-64 min-h-screen pb-24 md:pb-8 flex-1">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

/**
 * 管理端通用布局
 *
 * 结构来源：Stitch 页面 _7 ~ _11, center 中共享的 SideNavBar
 */

const router = useRouter()
const authStore = useAuthStore()

/** 侧边栏导航项 */
const sideNavItems = [
  { path: '/admin/dashboard', icon: 'dashboard', label: '仪表盘' },
  { path: '/admin/spaces', icon: 'local_parking', label: '停车区域' },
  { path: '/admin/users', icon: 'group', label: '用户管理' },
  { path: '/admin/billing', icon: 'payments', label: '营收统计' },
  { path: '/admin/devices', icon: 'router', label: '设备管理' },
  { path: '/admin/ai-vision', icon: 'neurology', label: 'AI 视觉监测' },
  { path: '/admin/profile', icon: 'account_circle', label: '个人资料' },
]

/** 移动端底部导航（简化核心功能） */
const mobileTabs = [
  { path: '/admin/dashboard', icon: 'dashboard', label: '概览' },
  { path: '/admin/spaces', icon: 'local_parking', label: '车位' },
  { path: '/admin/users', icon: 'group', label: '用户' },
]

/** 退出登录 */
function handleLogout() {
  authStore.logout()
  ElMessage.success('已安全退出管理后台')
  router.push('/login')
}
</script>
