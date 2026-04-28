/**
 * Sentinel Parking — Vue Router 路由配置
 *
 * 路由结构：
 * - 用户端 (/) — TopNavBar + BottomNavBar 布局
 * - 管理端 (/admin) — SideNavBar 布局
 * - 独立页面 (登录/注册) — 无布局
 */

import { createRouter, createWebHistory } from 'vue-router'

// ============================================================
// 用户端页面 — 懒加载
// ============================================================
const userRoutes = [
  {
    path: '/',
    component: () => import('@/layouts/UserLayout.vue'),
    meta: { requiresAuth: false },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/user/HomeView.vue'),
        meta: { title: '首页 | Sentinel Parking', requiresAuth: false },
      },
      {
        path: 'map',
        name: 'Map',
        component: () => import('@/views/user/MapView.vue'),
        meta: { title: '智能地图 | Sentinel Parking', requiresAuth: true },
      },
      {
        path: 'parking-management',
        name: 'ParkingManagement',
        component: () => import('@/views/ParkingManagementView.vue'),
        meta: { title: '多楼层停车管理 | Sentinel Parking' },
      },
      {
        path: 'find-car',
        redirect: '/map',
      },
      {
        path: 'payment',
        name: 'Payment',
        component: () => import('@/views/user/PaymentView.vue'),
        meta: { title: '安全支付 | Sentinel Parking', requiresAuth: true },
      },
      {
        path: 'payment-method-select',
        name: 'PaymentMethodSelect',
        component: () => import('@/views/user/PaymentMethodSelectView.vue'),
        meta: { title: '选择支付方式 | Sentinel Parking' },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/user/ProfileView.vue'),
        meta: { title: '个人中心 | Sentinel Parking', requiresAuth: true },
      },
      {
        path: 'feedback',
        name: 'Feedback',
        component: () => import('@/views/user/FeedbackView.vue'),
        meta: { title: '故障/投诉反馈 | Sentinel Parking' },
      },
      {
        path: 'reserve',
        name: 'Reserve',
        component: () => import('@/views/user/ReserveView.vue'),
        meta: { title: '预约车位 | Sentinel Parking', requiresAuth: true },
      },
    ],
  },
]

// ============================================================
// 管理端页面 — 懒加载
// ============================================================
const adminRoutes = [
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard',
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/DashboardView.vue'),
        meta: { title: '仪表盘 | Sentinel Admin' },
      },
      {
        path: 'spaces',
        name: 'AdminSpaces',
        component: () => import('@/views/admin/SpacesView.vue'),
        meta: { title: '车位管理 | Sentinel Admin' },
      },
      {
        path: 'billing',
        name: 'AdminBilling',
        component: () => import('@/views/admin/BillingView.vue'),
        meta: { title: '收费管理 | Sentinel Admin' },
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/UsersView.vue'),
        meta: { title: '用户管理 | Sentinel Admin' },
      },
      {
        path: 'devices',
        name: 'AdminDevices',
        component: () => import('@/views/admin/DevicesView.vue'),
        meta: { title: '设备管理 | Sentinel Admin' },
      },
      {
        path: 'ai-vision',
        name: 'AdminAIVision',
        component: () => import('@/views/admin/AIVisionView.vue'),
        meta: { title: 'AI 视觉感知 | Sentinel Admin' },
      },
      {
        path: 'profile',
        name: 'AdminProfile',
        component: () => import('@/views/admin/AdminProfileView.vue'),
        meta: { title: '个人资料 | Sentinel Admin' },
      },
    ],
  },
]

// ============================================================
// 独立页面（无通用布局）
// ============================================================
const authRoutes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/user/LoginView.vue'),
    meta: { title: '登录 | Sentinel Parking' },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/user/RegisterView.vue'),
    meta: { title: '注册 | Sentinel Parking' },
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/views/admin/LoginView.vue'),
    meta: { title: '管理员登录 | Sentinel Admin' },
  },
  {
    path: '/diagnostic',
    name: 'Diagnostic',
    component: () => import('@/components/DiagnosticTool.vue'),
    meta: { title: '诊断工具 | Sentinel Parking' },
  },
  {
    path: '/map-test',
    name: 'MapTest',
    component: () => import('@/views/MapTestView.vue'),
    meta: { title: '地图测试 | Sentinel Parking' },
  },
  {
    path: '/simple-map',
    name: 'SimpleMap',
    component: () => import('@/components/SimpleMapTest.vue'),
    meta: { title: '简单地图测试 | Sentinel Parking' },
  },
]

import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

// ============================================================
// 创建路由实例
// ============================================================
const router = createRouter({
  history: createWebHistory(),
  routes: [...userRoutes, ...adminRoutes, ...authRoutes],
  // 页面切换时滚动到顶部
  scrollBehavior() {
    return { top: 0 }
  },
})

// 全局前置守卫
router.beforeEach(async (to) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title
  }

  const authStore = useAuthStore()
  const { isLoggedIn, userInfo } = authStore
  const isAdmin = !!(userInfo && userInfo.is_staff)

  // 1. 检查是否需要登录
  if (to.meta.requiresAuth && !isLoggedIn) {
    ElMessage.warning('请先登录后访问')
    return { name: 'Login', query: { redirect: to.fullPath } }
  }

  // 2. 检查是否需要管理员权限
  if (to.meta.requiresAdmin) {
    if (!isAdmin) {
      ElMessage.error('权限不足，仅管理员可访问')
      return { name: 'Home' }
    }
  }

  // 3. 角色分流：管理员账号禁止进入用户端页面
  if (isLoggedIn && isAdmin && !to.path.startsWith('/admin')) {
    return { name: 'AdminDashboard' }
  }

  // 4. 已登录用户访问登录页时按角色跳转
  if (isLoggedIn && (to.name === 'Login' || to.name === 'AdminLogin')) {
    return isAdmin ? { name: 'AdminDashboard' } : { name: 'Home' }
  }
})

export default router
