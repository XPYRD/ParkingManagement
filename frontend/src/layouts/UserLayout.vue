<template>
  <!-- 用户端布局：顶部导航 + 内容区 + 移动端底部导航 -->
  <div class="min-h-screen bg-surface">
    <!-- ===== 顶部导航栏 ===== -->
    <header
      class="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200/50 shadow-sm"
    >
      <div class="flex justify-between items-center px-6 py-3 max-w-full">
        <!-- 品牌标识 -->
        <router-link
          to="/"
          class="text-xl font-bold tracking-tight text-primary font-headline"
        >
          Sentinel Parking
        </router-link>

        <!-- 桌面端导航菜单 -->
        <nav class="hidden md:flex gap-8 items-center">
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="text-secondary hover:text-primary transition-colors font-label font-medium text-sm"
            exact-active-class="!text-primary font-bold border-b-2 border-primary pb-1"
          >
            {{ item.label }}
          </router-link>
        </nav>

        <!-- 右侧操作区 -->
        <div class="flex gap-2 items-center">
          <template v-if="authStore.isLoggedIn">
            <button
              class="material-symbols-outlined text-secondary hover:bg-surface-container p-2 rounded-lg transition-all active:scale-95"
            >
              notifications
            </button>
            <el-dropdown trigger="hover" @command="handleCommand">
              <div class="material-symbols-outlined text-secondary hover:bg-surface-container p-2 rounded-lg transition-all active:scale-95 cursor-pointer outline-none">
                account_circle
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <span class="material-symbols-outlined text-sm mr-2">person</span>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided class="!text-error">
                    <span class="material-symbols-outlined text-sm mr-2 text-error">logout</span>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <router-link to="/login">
              <el-button type="primary" plain class="!rounded-full !font-bold">登录</el-button>
            </router-link>
          </template>
        </div>
      </div>
    </header>

    <!-- ===== 主内容区 ===== -->
    <main class="pt-16 pb-24 md:pb-8">
      <router-view />
    </main>

    <!-- ===== 移动端底部导航栏 ===== -->
    <nav
      class="md:hidden fixed bottom-0 left-0 w-full z-50 bg-white/90 backdrop-blur-md flex justify-around items-center px-4 pt-2 pb-6 border-t border-slate-200 shadow-[0_-4px_20px_rgba(0,0,0,0.05)]"
    >
      <router-link
        v-for="tab in bottomTabs"
        :key="tab.path"
        :to="tab.path"
        class="flex flex-col items-center justify-center text-slate-400 px-3 py-1 rounded-2xl transition-colors"
        active-class="!bg-primary-fixed/30 !text-primary"
      >
        <span class="material-symbols-outlined text-[22px]">{{ tab.icon }}</span>
        <span class="text-[10px] font-semibold mt-0.5">{{ tab.label }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
/**
 * 用户端通用布局
 *
 * 结构来源：Stitch 页面 _1 ~ _5, _12, _13 中共享的 TopNavBar + BottomNavBar
 */

import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

/** 桌面端顶部导航项 */
const navItems = [
  { path: '/', label: '系统首页' },
  { path: '/map', label: '停车场地图' },
  { path: '/reserve', label: '预约车位' },
  { path: '/payment', label: '支付账单' },
  { path: '/profile', label: '个人中心' },
]

/** 移动端底部导航项 */
const bottomTabs = [
  { path: '/', icon: 'explore', label: '首页' },
  { path: '/map', icon: 'location_on', label: '地图' },
  { path: '/reserve', icon: 'calendar_today', label: '预约' },
  { path: '/profile', icon: 'person', label: '我的' },
]

/** 处理下拉菜单指令 */
const handleCommand = (command) => {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    authStore.logout()
    ElMessage.success('已安全退出登录')
    router.push('/login')
  }
}
</script>
