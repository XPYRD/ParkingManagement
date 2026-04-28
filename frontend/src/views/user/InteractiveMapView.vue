<template>
  <div class="interactive-map-view">
    <InteractiveMapWithNavigation />
  </div>
</template>

<script setup>
import InteractiveMapWithNavigation from '@/components/InteractiveMapWithNavigation.vue'
</script>

<style scoped>
.interactive-map-view {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>
