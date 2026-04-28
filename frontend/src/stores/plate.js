import { defineStore } from 'pinia'
import { ref } from 'vue'

export const usePlateStore = defineStore('plate', () => {
  // 仅保存在内存中：页面刷新后自动清空
  const plateNumber = ref('')

  function setPlateNumber(value) {
    const normalized = String(value || '').trim().toUpperCase().replace(/\s+/g, '')
    plateNumber.value = normalized
  }

  return {
    plateNumber,
    setPlateNumber,
  }
})
