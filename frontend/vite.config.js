import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

/**
 * Vite 构建配置
 * - @ 别名指向 src/
 * - API 请求代理到 Django 8000 端口
 * - Tailwind CSS v4 集成
 */
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_API_URL || 'http://127.0.0.1:8080'

  return {
    plugins: [
      vue(),
      tailwindcss(),
    ],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },
    server: {
      port: 8180, // 改为 8180，和登录页面保持一致
      // 将 /api 请求代理到 Django 后端，避免跨域问题
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          proxyTimeout: 120000,
          timeout: 120000,
        },
      },
    },
  }
})
