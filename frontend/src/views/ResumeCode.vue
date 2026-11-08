<template>
  <div class="student-entry-page xz-entry resume-page">
    <section class="xz-entry-grid xz-entry-single">
      <div class="xz-entry-copy">
        <span class="xz-kicker"><b>★</b> Buxoro · Respublika olimpiadasi</span>
        <h1 class="xz-title">Testni<span>davom ettirish</span></h1>

        <div class="xz-stage-login">
          <form class="student-card entry-card xz-login-card resume-card" @submit.prevent="resume">
            <h2>6 xonali kodingizni kiriting</h2>
            <p class="entry-subtitle">
              Test oxirigacha yakunlanmagan bo‘lsa, belgilagan javoblaringiz va qolgan vaqtingiz saqlangan.
              Kodni kiritsangiz, test to‘xtagan joyidan davom etadi.
            </p>

            <input
              ref="inputRef"
              v-model="code"
              class="resume-code-input"
              type="text"
              inputmode="numeric"
              autocomplete="one-time-code"
              maxlength="6"
              placeholder="••••••"
              aria-label="6 xonali kod"
              @input="onInput"
            />

            <button type="submit" class="primary-btn entry-start-btn" :disabled="code.length !== 6 || loading">
              {{ loading ? 'Tekshirilmoqda...' : 'Davom ettirish' }}
            </button>

            <p v-if="error" class="error-box">{{ error }}</p>

            <RouterLink to="/student" class="admin-login-link entry-admin-link">Bosh sahifaga qaytish</RouterLink>
          </form>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'

const router = useRouter()
const code = ref('')
const loading = ref(false)
const error = ref('')
const inputRef = ref(null)

function onInput() {
  code.value = code.value.replace(/\D/g, '').slice(0, 6)
  error.value = ''
}

function errorText(e) {
  const status = e?.response?.status
  const detail = e?.response?.data?.detail || ''
  if (status === 429) return 'Juda ko‘p noto‘g‘ri urinish. Biroz kutib, qayta urinib ko‘ring.'
  if (status === 404) return 'Bunday kod topilmadi. Raqamlarni tekshirib qayta kiriting.'
  if (/ishlatilgan/i.test(detail)) return 'Bu kod bilan test allaqachon yakunlangan. Natija va sertifikat adminda saqlangan.'
  return detail || 'Kirib bo‘lmadi. Internetni tekshirib, qayta urinib ko‘ring.'
}

async function resume() {
  if (code.value.length !== 6) return
  loading.value = true
  error.value = ''
  try {
    const start = await api.post('/exam/start/', { code: code.value })
    sessionStorage.setItem('exam_payload', JSON.stringify({ ...start.data, code: code.value }))
    router.push('/exam')
  } catch (e) {
    error.value = errorText(e)
  } finally {
    loading.value = false
  }
}

onMounted(() => nextTick(() => inputRef.value?.focus()))
</script>

<style scoped>
.resume-card {
  display: grid;
  gap: 14px;
  text-align: center;
  width: min(460px, 100%);
}

.resume-card h2 {
  margin: 0;
}

.resume-code-input {
  width: 100%;
  min-height: 64px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.45);
  background: rgba(255, 255, 255, 0.95);
  color: #0b1b4d;
  text-align: center;
  font-size: 34px;
  font-weight: 800;
  letter-spacing: 0.45em;
  padding: 0 0 0 0.45em;
  font-variant-numeric: tabular-nums;
}

.resume-code-input:focus {
  outline: 3px solid rgba(227, 194, 90, 0.7);
  outline-offset: 2px;
}
</style>
