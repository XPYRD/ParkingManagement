<template>
  <div class="space-y-4">
    <!-- 车牌号显示 -->
    <div class="bg-primary/5 border-2 border-primary rounded-lg p-4 text-center">
      <div class="text-xs text-secondary mb-1">车牌号</div>
      <div class="text-2xl font-black font-headline text-on-surface tracking-widest">
        {{ plateDisplay }}
      </div>
    </div>

    <!-- 虚拟键盘 -->
    <div class="space-y-3">
      <!-- 第一位：省份选择 -->
      <div v-if="currentPosition === 0">
        <div class="text-xs text-secondary font-semibold mb-2">第1位 - 选择省份</div>
        <div class="grid grid-cols-5 gap-2">
          <button
            v-for="province in provinces"
            :key="province"
            @click="selectProvince(province)"
            class="py-2 rounded-lg font-semibold text-sm transition-all active:scale-95"
            :class="plate[0] === province 
              ? 'bg-primary text-white' 
              : 'bg-surface-container-high text-on-surface hover:bg-primary/20'"
          >
            {{ province }}
          </button>
        </div>
      </div>

      <!-- 绿牌第三位：D/F 选择 -->
      <div v-else-if="currentPosition === 2 && energyType === 'new_energy'">
        <div class="text-xs text-secondary font-semibold mb-2">第3位 - 新能源标识</div>
        <div class="grid grid-cols-5 gap-2">
          <button
            v-for="letter in ['D', 'F']"
            :key="letter"
            @click="selectChar(letter)"
            class="py-3 rounded-lg font-semibold text-base transition-all active:scale-95"
            :class="plate[currentPosition] === letter 
              ? 'bg-primary text-white' 
              : 'bg-surface-container-high text-on-surface hover:bg-primary/20'"
          >
            {{ letter }}
          </button>
        </div>
      </div>

      <!-- 其他位数：大写字母 + 数字 -->
      <div v-else>
        <div class="text-xs text-secondary font-semibold mb-2">
          第{{ currentPosition + 1 }}位 - 选择字符
        </div>
        
        <!-- 大写字母 -->
        <div class="mb-2">
          <div class="grid grid-cols-8 gap-1">
            <button
              v-for="letter in letters"
              :key="letter"
              @click="selectChar(letter)"
              class="py-1.5 rounded-lg font-semibold text-xs transition-all active:scale-95"
              :class="plate[currentPosition] === letter 
                ? 'bg-primary text-white' 
                : 'bg-surface-container-high text-on-surface hover:bg-primary/20'"
            >
              {{ letter }}
            </button>
          </div>
        </div>

        <!-- 数字 -->
        <div>
          <div class="grid grid-cols-5 gap-2">
            <button
              v-for="digit in digits"
              :key="digit"
              @click="selectChar(digit)"
              class="py-2 rounded-lg font-semibold text-sm transition-all active:scale-95"
              :class="plate[currentPosition] === digit 
                ? 'bg-primary text-white' 
                : 'bg-surface-container-high text-on-surface hover:bg-primary/20'"
            >
              {{ digit }}
            </button>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="flex gap-2 mt-4">
        <button
          @click="backspace"
          class="flex-1 py-2 rounded-lg bg-error/20 text-error hover:bg-error/30 font-semibold transition-all active:scale-95"
        >
          <span class="material-symbols-outlined text-sm mr-1">backspace</span>
          退格
        </button>
        <button
          v-if="currentPosition < totalLength - 1"
          @click="nextPosition"
          :disabled="!plate[currentPosition]"
          class="flex-1 py-2 rounded-lg font-semibold transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          :class="plate[currentPosition] 
            ? 'bg-primary text-white hover:shadow-md' 
            : 'bg-surface-container-high text-secondary'"
        >
          下一位 →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  energyType: {
    type: String,
    default: 'ice', // 'ice' | 'new_energy'
  }
})

const emit = defineEmits(['update:modelValue', 'complete'])

// 省份列表
const provinces = ['豫', '京', '沪', '粤', '浙', '苏', '鲁', '渝', '川', '云', '陕', '甘', '晋', '冀', '吉', '黑', '辽', '宁', '蒙', '桂', '贵', '琼', '青', '新', '藏', '台', '港', '澳']

// 大写字母 A-Z
const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

// 数字 0-9
const digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

// 根据能源类型确定总长度
const totalLength = computed(() => {
  return props.energyType === 'new_energy' ? 8 : 7
})

const plate = ref([])
const currentPosition = ref(0)

// 初始化或重置车牌数组
const initPlate = () => {
  if (props.modelValue && props.modelValue.length > 0) {
    const chars = props.modelValue.split('').concat(Array(8).fill('')).slice(0, 8)
    plate.value = chars

    // 粘贴/同步后将定位停在最后一个已输入字符位置，便于继续编辑
    const effectiveLength = totalLength.value
    let lastFilledIndex = -1
    for (let i = 0; i < effectiveLength; i++) {
      if (chars[i]) {
        lastFilledIndex = i
      }
    }
    currentPosition.value = lastFilledIndex >= 0 ? lastFilledIndex : 0
  } else {
    plate.value = Array(8).fill('')
    currentPosition.value = 0
  }
}

// 组件挂载时初始化
onMounted(() => {
  initPlate()
})

watch(
  () => props.modelValue,
  (newVal) => {
    const next = String(newVal || '')
    const current = plate.value.slice(0, totalLength.value).join('')
    if (next !== current) {
      initPlate()
    }
  },
)

watch(
  () => props.energyType,
  () => {
    initPlate()
  },
)

const isComplete = computed(() => {
  return plate.value.slice(0, totalLength.value).every(char => char)
})

const plateDisplay = computed(() => {
  if (props.energyType === 'new_energy') {
    // 绿牌格式：豫 A · D12345 (8位)
    const displayChars = plate.value.slice(0, 8).map(char => char || '·')
    return `${displayChars[0]}${displayChars[1]}·${displayChars[2]}${displayChars.slice(3).join('')}`
  } else {
    // 蓝牌格式：豫 A · 12345 (7位)
    const displayChars = plate.value.slice(0, 7).map(char => char || '·')
    return `${displayChars[0]}${displayChars[1]}·${displayChars.slice(2).join('')}`
  }
})

const selectProvince = (province) => {
  plate.value[0] = province
  currentPosition.value = 1
}

const selectChar = (char) => {
  if (currentPosition.value >= totalLength.value) return
  plate.value[currentPosition.value] = char
  
  // 检查是否已输入完整
  const isLastPosition = currentPosition.value === totalLength.value - 1
  
  // 输入一位后自动进入下一位
  if (currentPosition.value < totalLength.value - 1) {
    currentPosition.value++
  }
  
  // 最后一位输入完成后立即触发完成
  if (isLastPosition) {
    // 延迟一点点时间，确保 UI 更新后再触发
    setTimeout(() => {
      complete()
    }, 100)
  }
}

const nextPosition = () => {
  if (currentPosition.value < totalLength.value - 1 && plate.value[currentPosition.value]) {
    currentPosition.value++
  }
}

const backspace = () => {
  if (currentPosition.value > 0) {
    plate.value[currentPosition.value] = ''
    currentPosition.value--
  } else if (currentPosition.value === 0 && plate.value[0]) {
    plate.value[0] = ''
  }
}

const complete = () => {
  // 检查是否所有必要位数都已填充
  const filledPlate = plate.value.slice(0, totalLength.value).filter(c => c)
  if (filledPlate.length === totalLength.value) {
    const plateNumber = filledPlate.join('')
    emit('update:modelValue', plateNumber)
    emit('complete', plateNumber)
  }
}
</script>

<style scoped>
</style>
