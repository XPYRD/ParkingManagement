<template>
  <div 
    class="absolute p-0.5 transition-all duration-300 transform -translate-x-1/2 -translate-y-1/2 z-10"
    :style="{ 
      left: `${x}%`, 
      top: `${y}%`,
    }"
  >
    <!-- 车位主体单元 (更小更精细的比例) -->
    <div
      class="w-4 h-7 md:w-5 md:h-8 rounded-sm flex flex-col items-center justify-center cursor-pointer shadow-sm border border-white/50 relative group overflow-visible transition-all duration-300"
      :class="[statusClasses, spot.zone === 'B' ? 'rotate-[32deg]' : '']"
      @click="$emit('select', spot)"
    >
      <!-- 呼吸灯光效渲染 -->
      <div v-if="spot.status === 'free'" class="absolute inset-0 rounded-sm ring-offset-1 animate-breathe opacity-50"></div>


      
      <!-- 类型图标 -->
      <span class="material-symbols-outlined text-base md:text-lg mb-0.5 relative z-10">
        {{ typeIcon }}
      </span>
      
      <!-- 编号 -->
      <span class="text-[8px] md:text-[10px] font-black uppercase tracking-tighter relative z-10 leading-none">
        {{ spot.spot_id.split('-').pop() }}
      </span>

      <!-- 选中状态高亮 -->
      <div v-if="selected" class="absolute -inset-1.5 border-2 border-primary rounded-xl animate-pulse z-0"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  spot: { type: Object, required: true },
  x: { type: Number, required: true },
  y: { type: Number, required: true },
  selected: { type: Boolean, default: false }
})

defineEmits(['select'])

/** 图标根据类型映射 */
const typeIcon = computed(() => {
  switch (props.spot.spot_type) {
    case 'ev': return 'ev_station'
    case 'vip': return 'workspace_premium'
    case 'accessible': return 'accessible'
    case 'compact': return 'minor_crash'
    default: return 'local_parking'
  }
})

/** 状态样式机 */
const statusClasses = computed(() => {
  const base = 'transition-transform hover:scale-110 active:scale-95 '
  switch (props.spot.status) {
    case 'free': 
      return base + 'bg-green-500/10 border-green-500 text-green-600'
    case 'occupied':
    case 'overstay':
      return base + 'bg-primary border-primary text-white shadow-md'
    case 'reserved':
      return base + 'bg-amber-500 border-amber-500 text-white'
    case 'maintenance':
      return base + 'bg-slate-200 border-slate-300 text-slate-400 cursor-not-allowed opacity-60'
    default:
      return base + 'bg-white border-slate-200 text-slate-400'
  }
})
</script>

<style scoped>
@keyframes breathe {
  0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
  70% { box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
  100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
}
.animate-breathe {
  animation: breathe 2.5s infinite cubic-bezier(0.4, 0, 0.6, 1);
}
</style>
