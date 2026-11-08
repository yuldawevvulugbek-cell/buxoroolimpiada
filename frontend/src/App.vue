<template>
  <div class="xz" :class="{ 'sky-theme': skyMode }">
    <SkyScenes v-if="skyMode" :key="skyMode" :still="skyMode === 'still'" scene="night" />
    <AntalyaBackdrop v-else-if="backdrop" :variant="backdrop" />
    <router-view />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AntalyaBackdrop from './components/AntalyaBackdrop.vue'
import SkyScenes from './components/SkyScenes.vue'

const route = useRoute()

// O'quvchi sahifalari va admin kirishi: osmon manzaralari. Kirish sahifalarida manzaralar almashadi,
// test paytida esa bitta tinch manzara turadi, diqqat savollarda qolsin.
const skyMode = computed(() => {
  if (route.path === '/student' || route.path === '/' || route.path === '/admin/login' || route.path === '/code') return 'cycle'
  if (route.path === '/exam') return 'still'
  return ''
})

// Admin panel va Hacker konsolida eski fon chizilmaydi.
const backdrop = computed(() => {
  if (route.path === '/admin/hacker' || route.path === '/sekret') return ''
  // Admin panelning o'z fonı bor (admin-buxoro.css), eski fon kerak emas.
  if (route.path.startsWith('/admin/')) return ''
  return 'full'
})
</script>
