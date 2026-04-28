<template>
  <!-- 故障/投诉反馈 -->
  <div class="px-4 md:px-8 max-w-7xl mx-auto py-8">
    <header class="mb-8 text-center max-w-2xl mx-auto">
      <h1 class="text-3xl font-extrabold text-primary tracking-tight font-headline">服务反馈</h1>
      <p class="text-secondary text-sm mt-2">设备故障、服务投诉或建议，您的每一次反馈都帮助我们做得更好。</p>
    </header>

    <section class="bg-surface-container-lowest p-6 md:p-10 rounded-2xl border border-outline-variant/20 shadow-sm text-center">
      <span class="material-symbols-outlined text-5xl text-secondary">info</span>
      <h2 class="text-xl font-bold font-headline text-on-surface mt-4">反馈工单功能已下线</h2>
      <p class="text-secondary text-sm mt-2">
        系统已停止使用工单模块，当前页面仅保留说明。
      </p>
    </section>
  </div>
</template>

<script setup>
// 反馈工单功能已下线，页面仅保留说明。
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
