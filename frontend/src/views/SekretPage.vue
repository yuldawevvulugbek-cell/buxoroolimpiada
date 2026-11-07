<template>
  <div class="bx-admin bx-light sekret-page">
    <!-- Parol oynasi -->
    <div v-if="!token" class="sk-login-wrap">
      <form class="panel sk-login" @submit.prevent="login">
        <div class="sk-lock" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M7 11V8a5 5 0 0 1 10 0v3M5 11h14v10H5z" /></svg>
        </div>
        <h2>Maxfiy bo‘lim</h2>
        <p>Davom etish uchun parolni kiriting.</p>
        <input v-model="password" type="password" autocomplete="current-password" placeholder="Parol" autofocus />
        <button type="submit" class="primary-btn" :disabled="!password || loading">
          {{ loading ? 'Tekshirilmoqda...' : 'Kirish' }}
        </button>
        <p v-if="error" class="error-box">{{ error }}</p>
      </form>
    </div>

    <!-- Natijalar -->
    <div v-else class="sk-main">
      <div class="page-head">
        <div>
          <h2>Barcha natijalar</h2>
          <p>To‘g‘ri javoblar sonini o‘zgartirsangiz, foiz o‘zi qayta hisoblanadi va admin panelda ham, sertifikatda ham yangilanadi.</p>
        </div>
        <div class="sk-head-actions">
          <button type="button" class="secondary-btn" :disabled="loading" @click="load">Yangilash</button>
          <button type="button" class="danger-btn" @click="logout">Chiqish</button>
        </div>
      </div>

      <div class="sk-filters">
        <input v-model.trim="search" placeholder="Ism, telefon yoki fan bo‘yicha qidirish" />
        <select v-model="subjectFilter">
          <option value="">Barcha fanlar</option>
          <option v-for="s in subjectOptions" :key="s" :value="s">{{ s }}</option>
        </select>
        <span class="sk-count">{{ filtered.length }} ta natija</span>
      </div>

      <p v-if="error" class="error-box">{{ error }}</p>
      <p v-if="success" class="success-box">{{ success }}</p>

      <div class="panel">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>№</th>
                <th>O‘quvchi</th>
                <th>Telefon</th>
                <th>Fan</th>
                <th>Daraja</th>
                <th>O‘quv markaz</th>
                <th>To‘g‘ri</th>
                <th>Foiz</th>
                <th>Sana</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!filtered.length">
                <td colspan="10" class="sk-empty">{{ loading ? 'Yuklanmoqda...' : 'Natija topilmadi' }}</td>
              </tr>
              <tr v-for="(r, i) in filtered" :key="r.id" :class="{ editing: editId === r.id }">
                <td>{{ i + 1 }}</td>
                <td><b>{{ r.full_name }}</b><small v-if="r.age">{{ r.age }} yosh</small></td>
                <td>{{ r.phone || '—' }}</td>
                <td>{{ r.subject_name }}</td>
                <td>{{ r.level_name }}</td>
                <td>{{ r.center_name }}</td>
                <td>
                  <div v-if="editId === r.id" class="sk-edit">
                    <input
                      v-model.number="editValue"
                      type="number"
                      min="0"
                      :max="r.total_questions"
                      @keyup.enter="saveEdit(r)"
                      @keyup.esc="cancelEdit"
                    />
                    <span>/ {{ r.total_questions }}</span>
                  </div>
                  <template v-else><b>{{ r.correct_count }}</b> / {{ r.total_questions }}</template>
                </td>
                <td>
                  <span class="sk-percent">{{ editId === r.id ? previewPercent(r) : formatPercent(r.percent) }}%</span>
                </td>
                <td>{{ formatDate(r.finished_at) }}</td>
                <td class="sk-actions">
                  <template v-if="editId === r.id">
                    <button type="button" class="primary-btn sk-small" :disabled="saving" @click="saveEdit(r)">
                      {{ saving ? '...' : 'Saqlash' }}
                    </button>
                    <button type="button" class="secondary-btn sk-small" :disabled="saving" @click="cancelEdit">Bekor</button>
                  </template>
                  <button v-else type="button" class="secondary-btn sk-small" @click="startEdit(r)">Tahrirlash</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../api/axios'

const STORAGE_KEY = 'sekret-token'

function readToken() {
  try {
    return sessionStorage.getItem(STORAGE_KEY) || ''
  } catch {
    return ''
  }
}

const token = ref(readToken())
const password = ref('')
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const results = ref([])
const search = ref('')
const subjectFilter = ref('')
const editId = ref(null)
const editValue = ref(0)

const subjectOptions = computed(() => [...new Set(results.value.map(r => r.subject_name).filter(Boolean))].sort())

const filtered = computed(() => {
  const q = search.value.toLowerCase()
  return results.value.filter(r => {
    if (subjectFilter.value && r.subject_name !== subjectFilter.value) return false
    if (!q) return true
    return [r.full_name, r.phone, r.phone2, r.subject_name, r.level_name, r.center_name]
      .some(v => String(v || '').toLowerCase().includes(q))
  })
})

function detail(e, fallback) {
  return e?.response?.data?.detail || fallback
}

function formatPercent(value) {
  const n = Number(value || 0)
  return Number.isInteger(n) ? String(n) : n.toFixed(1)
}

function previewPercent(r) {
  const total = Number(r.total_questions || 0)
  const value = Math.min(Math.max(Number(editValue.value) || 0, 0), total)
  return total ? formatPercent(Math.round((value / total) * 10000) / 100) : '0'
}

function formatDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  const pad = n => String(n).padStart(2, '0')
  return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function setToken(value) {
  token.value = value
  try {
    if (value) sessionStorage.setItem(STORAGE_KEY, value)
    else sessionStorage.removeItem(STORAGE_KEY)
  } catch {
    // brauzer saqlashga ruxsat bermasa ham sahifa ishlayveradi
  }
}

function handleAuthError(e) {
  if (e?.response?.status === 401) {
    setToken('')
    error.value = detail(e, 'Parolni qayta kiriting.')
    return true
  }
  return false
}

async function login() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.post('/sekret/login/', { password: password.value })
    setToken(res.data.token)
    password.value = ''
    await load()
  } catch (e) {
    error.value = e?.response?.status === 429 ? 'Juda ko‘p urinish. Bir daqiqadan keyin qayta urinib ko‘ring.' : detail(e, 'Kirib bo‘lmadi.')
  } finally {
    loading.value = false
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.post('/sekret/results/', { token: token.value })
    results.value = res.data.results
  } catch (e) {
    if (!handleAuthError(e)) error.value = detail(e, 'Natijalarni yuklab bo‘lmadi.')
  } finally {
    loading.value = false
  }
}

function startEdit(r) {
  editId.value = r.id
  editValue.value = r.correct_count
  success.value = ''
  error.value = ''
}

function cancelEdit() {
  editId.value = null
}

async function saveEdit(r) {
  const value = Number(editValue.value)
  if (!Number.isInteger(value) || value < 0 || value > r.total_questions) {
    error.value = `To‘g‘ri javoblar soni 0 dan ${r.total_questions} gacha bo‘lishi kerak.`
    return
  }
  saving.value = true
  error.value = ''
  try {
    const res = await api.post('/sekret/results/update/', { token: token.value, id: r.id, correct_count: value })
    Object.assign(r, res.data)
    editId.value = null
    success.value = `${r.full_name}: ${r.correct_count}/${r.total_questions}, ${formatPercent(r.percent)}% saqlandi.`
  } catch (e) {
    if (!handleAuthError(e)) error.value = detail(e, 'Saqlab bo‘lmadi.')
  } finally {
    saving.value = false
  }
}

function logout() {
  setToken('')
  results.value = []
  editId.value = null
}

onMounted(() => {
  if (token.value) load()
})
</script>

<style scoped>
.sekret-page {
  min-height: 100vh;
  padding: 32px clamp(14px, 3vw, 40px) 48px;
}

.sk-login-wrap {
  min-height: calc(100vh - 80px);
  display: grid;
  place-items: center;
}

.sk-login {
  width: min(400px, 100%);
  display: grid;
  gap: 12px;
  text-align: center;
  padding: 32px 28px !important;
}

.sk-login h2 { margin: 0; font-size: 24px; color: var(--bx-text); }
.sk-login p { margin: 0; color: var(--bx-muted); }
.sk-login input { min-height: 46px; padding: 0 14px; text-align: center; }
.sk-login .primary-btn { min-height: 46px; }

.sk-lock {
  justify-self: center;
  width: 60px;
  height: 60px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: linear-gradient(145deg, #0f2b4f, #0a1d37);
  box-shadow: 0 10px 24px rgba(15, 43, 79, 0.3);
}

.sk-lock svg {
  width: 28px;
  height: 28px;
  fill: none;
  stroke: #e3c25a;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.sk-main { max-width: 1400px; margin: 0 auto; }

.sk-head-actions { display: flex; gap: 10px; }
.sk-head-actions button { min-height: 42px; padding: 0 16px; }

.sk-filters {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.sk-filters input,
.sk-filters select { min-height: 44px; padding: 0 12px; }
.sk-count { color: var(--bx-muted); font-weight: 700; white-space: nowrap; }

td small { display: block; color: var(--bx-muted); font-size: 12px; }
.sk-empty { text-align: center; color: var(--bx-muted) !important; padding: 28px !important; }

.sk-edit { display: flex; align-items: center; gap: 6px; }
.sk-edit input { width: 72px; min-height: 36px; padding: 0 8px; text-align: center; font-weight: 700; }

.sk-percent { font-weight: 800; color: var(--bx-primary); }

.sk-actions { display: flex; gap: 6px; }
.sk-small { min-height: 34px; padding: 0 12px !important; font-size: 13px !important; }

tr.editing td { background: var(--bx-gold-soft) !important; }

@media (max-width: 720px) {
  .sk-filters { grid-template-columns: 1fr; }
  .page-head { flex-direction: column; align-items: flex-start !important; }
}
</style>
