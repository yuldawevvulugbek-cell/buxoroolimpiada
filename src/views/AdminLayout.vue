<template>
  <div class="admin-shell" :class="isHackerRoute ? 'hacker-admin-shell hacker-fullscreen-shell' : ['bx-admin', isLightMode ? 'bx-light' : 'bx-dark']">
    <div class="hacker-matrix-layer" aria-hidden="true"></div>
    <aside v-if="!isHackerRoute" class="sidebar hacker-sidebar" :class="{ open: menuOpen }">
      <div class="sidebar-brand bx-brand">
        <div class="bx-emblem" aria-hidden="true">
          <svg viewBox="0 0 48 48"><polygon points="24,2 29.5,14.6 43.2,13.2 35,24 43.2,34.8 29.5,33.4 24,46 18.5,33.4 4.8,34.8 13,24 4.8,13.2 18.5,14.6" /><circle cx="24" cy="24" r="7" /></svg>
        </div>
        <div>
          <h2>Buxoro olimpiadasi</h2>
          <span>{{ adminTitle }}</span>
        </div>
      </div>

      <nav @click="menuOpen = false">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to">
          <svg viewBox="0 0 24 24" class="bx-nav-icon" aria-hidden="true"><path :d="item.icon" /></svg>
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <div class="hacker-side-status">
        <span></span> Olimpiada faol
      </div>
      <button class="ghost-btn logout" @click="logout">⏻ Chiqish</button>
    </aside>
    <div v-if="menuOpen && !isHackerRoute" class="xz-menu-overlay" @click="menuOpen = false"></div>

    <main class="admin-main">
      <header v-if="!isHackerRoute" class="topbar hacker-topbar">
        <button class="menu-btn" @click="menuOpen = !menuOpen">☰</button>
        <div class="hacker-title-block bx-title-block">
          <span class="hacker-eyebrow">Buxoro Respublika olimpiadasi</span>
          <h1>Xush kelibsiz, {{ adminTitle }}</h1>
          <p>{{ todayText }}</p>
        </div>
        <div class="hacker-top-actions">
          <RouterLink v-if="mainAdmin" to="/admin/hacker" class="hacker-top-link">Hacker</RouterLink>
          <button class="theme-toggle-btn" type="button" @click="toggleTheme" :title="isLightMode ? 'Kechki rejimga o‘tish' : 'Kunduzgi rejimga o‘tish'">
            <span class="moon-icon">{{ isLightMode ? '🌙' : '☀️' }}</span>
            <b>{{ isLightMode ? 'Tungi rejim' : 'Kunduzgi rejim' }}</b>
          </button>
          <RouterLink to="/student" class="student-link">O‘quvchi kirishi</RouterLink>
        </div>
      </header>

      <section class="content-wrap">
        <RouterView />
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { clearAuthStorage, fetchCurrentAdmin, getStoredAdminProfile, isMainAdmin } from '../utils/auth'

const route = useRoute()
const router = useRouter()
const menuOpen = ref(false)
const isLightMode = ref(false)
const currentAdmin = ref(getStoredAdminProfile())
const mainAdmin = computed(() => isMainAdmin(currentAdmin.value))
const adminTitle = computed(() => currentAdmin.value?.center_name || currentAdmin.value?.assigned_center_name || currentAdmin.value?.branch || 'Bosh admin')
const isHackerRoute = computed(() => route.path === '/admin/hacker')

// Yon menyu: har bir bo'lim uchun oddiy chiziqli belgi (SVG path).
const ICONS = {
  dashboard: 'M4 13h7V4H4zm0 7h7v-5H4zm9 0h7v-9h-7zm0-16v5h7V4z',
  admins: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm-7 8c0-3.3 3.1-6 7-6s7 2.7 7 6',
  create: 'M10 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm-7 9c0-3.3 3.1-6 7-6 1.4 0 2.6.3 3.7.9M18 14v6m-3-3h6',
  codes: 'M8 7l-5 5 5 5m8-10l5 5-5 5M14 4l-4 16',
  excel: 'M6 3h9l5 5v13H6zm8 0v6h6M9 13l4 5m0-5l-4 5',
  students: 'M9 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zm-6 9c0-3 2.7-5.5 6-5.5s6 2.5 6 5.5m1-9a3 3 0 1 0 0-6m2 15c0-2.4-1.2-4.4-3-5.3',
  tests: 'M7 3h10a1 1 0 0 1 1 1v17l-6-3-6 3V4a1 1 0 0 1 1-1zm2 5h6m-6 4h6',
  results: 'M4 20V10m6 10V4m6 16v-7m4 7H2',
  upload: 'M12 16V4m0 0l-5 5m5-5l5 5M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3',
}
const navItems = computed(() => {
  const canCreate = currentAdmin.value?.can_create_students
  return [
    { to: '/admin/dashboard', label: 'Bosh sahifa', icon: ICONS.dashboard, show: true },
    { to: '/admin/results', label: 'Natijalar', icon: ICONS.results, show: true },
    { to: '/admin/students', label: 'O‘quvchilar', icon: ICONS.students, show: true },
    { to: '/admin/questions', label: 'Testlar', icon: ICONS.tests, show: true },
    { to: '/admin/tests/upload', label: 'Test yuklash', icon: ICONS.upload, show: mainAdmin.value },
    { to: '/admin/students/create', label: 'O‘quvchi yaratish', icon: ICONS.create, show: canCreate },
    { to: '/admin/students/codes', label: 'Code yaratish', icon: ICONS.codes, show: canCreate },
    { to: '/admin/students/import', label: 'Excel yuklash', icon: ICONS.excel, show: canCreate },
    { to: '/admin/admins', label: 'Adminlar', icon: ICONS.admins, show: mainAdmin.value },
  ].filter(item => item.show)
})

const PAGE_TITLES = {
  '/admin/dashboard': 'Bosh sahifa',
  '/admin/results': 'Natijalar',
  '/admin/students': 'O‘quvchilar',
  '/admin/questions': 'Testlar',
  '/admin/tests/upload': 'Test yuklash',
  '/admin/students/create': 'O‘quvchi yaratish',
  '/admin/students/codes': 'Code yaratish',
  '/admin/students/import': 'Excel yuklash',
  '/admin/admins': 'Adminlar',
}
const pageTitle = computed(() => PAGE_TITLES[route.path] || 'Admin panel')
const MONTHS = ['yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun', 'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr']
const todayText = computed(() => {
  const d = new Date()
  return `Bugun: ${d.getDate()}-${MONTHS[d.getMonth()]}, ${d.getFullYear()} · ${pageTitle.value}`
})

function toggleTheme() {
  isLightMode.value = !isLightMode.value
  localStorage.setItem('admin-theme', isLightMode.value ? 'light' : 'dark')
}

function logout() {
  clearAuthStorage()
  router.push('/admin/login')
}

onMounted(async () => {
  // Standart: kunduzgi (yorug') rejim. Faqat foydalanuvchi tungi rejimni tanlagan bo'lsa qorong'i.
  isLightMode.value = localStorage.getItem('admin-theme') !== 'dark'

  try {
    currentAdmin.value = await fetchCurrentAdmin()
  } catch {
    clearAuthStorage()
    router.push('/admin/login')
  }
})
</script>
