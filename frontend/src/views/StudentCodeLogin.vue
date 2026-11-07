<template>
  <div class="student-entry-page xz-entry">
    <section class="xz-entry-grid xz-entry-single">
      <div class="xz-entry-copy">
        <span class="xz-kicker"><b>★</b> Buxoro · Respublika olimpiadasi</span>
        <h1 class="xz-title">Buxoro<span>Olimpiadasi</span></h1>
        <Transition name="sky-caption" mode="out-in">
          <p :key="sceneIndex" class="sky-caption">{{ captions[sceneIndex] }}</p>
        </Transition>

        <div class="xz-stage-login">
          <div v-tilt="6" class="student-card entry-card xz-login-card">
            <div class="xz-card-badges">
              <span>O‘QUVCHI</span>
              <span>★ RESPUBLIKA</span>
            </div>

            <h2>Olimpiadaga xush kelibsiz</h2>
            <p class="entry-subtitle">Ro‘yxatdan o‘ting, fan va darajani tanlang, test darhol boshlanadi. Yakunda sertifikat olasiz.</p>

            <button type="button" class="primary-btn entry-start-btn xz-open-register" @click="openRegister">
              Ro‘yxatdan o‘tish
            </button>

            <p v-if="error" class="error-box">{{ error }}</p>

            <RouterLink to="/admin/login" class="admin-login-link entry-admin-link">
              Admin panelga kirish
            </RouterLink>
          </div>
        </div>
      </div>

    </section>

    <div v-if="showRegister" class="modal-backdrop" @click.self="closeRegister">
      <div class="answer-modal xz-register-modal">
        <button type="button" class="modal-close-btn" @click="closeRegister">×</button>
        <h2>Ro‘yxatdan o‘tish</h2>
        <p>Ma’lumotlaringizni kiriting, so‘ng fan va darajani tanlang.</p>

        <form @submit.prevent="register" class="xz-register-form">
          <label>
            Ism familiya
            <input v-model.trim="reg.full_name" autocomplete="name" placeholder="Masalan: Alisher Navoiy" required />
          </label>
          <label class="xz-register-age">
            Yosh
            <input v-model.number="reg.age" type="number" min="4" max="99" inputmode="numeric" placeholder="12" required />
          </label>
          <div class="xz-register-row">
            <label>
              Telefon raqam
              <input :value="reg.phone" type="tel" inputmode="numeric" autocomplete="tel" placeholder="+998 90 123 45 67" required @focus="phoneFocus('phone')" @blur="phoneBlur('phone')" @input="phoneInput('phone', $event)" />
            </label>
            <label>
              Qo‘shimcha telefon raqam
              <input :value="reg.phone2" type="tel" inputmode="numeric" placeholder="+998 91 765 43 21" required @focus="phoneFocus('phone2')" @blur="phoneBlur('phone2')" @input="phoneInput('phone2', $event)" />
            </label>
          </div>
          <div class="xz-register-row">
            <label>
              Fan
              <select v-model="reg.subject" required @change="reg.level = ''">
                <option value="" disabled>Fanni tanlang</option>
                <option v-for="subject in catalog.subjects" :key="subject.id" :value="subject.id">{{ subject.name }}</option>
              </select>
            </label>
            <label>
              Daraja
              <select v-model="reg.level" required :disabled="!selectedSubject">
                <option value="" disabled>{{ selectedSubject ? 'Darajani tanlang' : 'Avval fanni tanlang' }}</option>
                <option v-for="level in selectedSubject?.levels || []" :key="level.id" :value="level.id">{{ level.name }}</option>
              </select>
            </label>
          </div>
          <button class="primary-btn entry-start-btn" :disabled="loading || catalogLoading">
            {{ loading ? 'Test tayyorlanmoqda...' : 'Testni boshlash' }}
          </button>
        </form>

        <p v-if="regError" class="error-box">{{ regError }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/axios'
import { useSceneClock } from '../composables/useSceneClock'

const router = useRouter()
// Fon manzarasi bilan birga almashadigan yozuvlar.
const { sceneIndex } = useSceneClock({ run: false })
const captions = [
  'Ilm – nurli yo‘l',
  'IT · Ingliz tili · Rus tili · Koreys tili · Hamshiralik',
  'Har bir savol – oldinga bir qadam. Sizning vaqtingiz keldi!',
]
const loading = ref(false)
const error = ref('')
const regError = ref('')

// Ro'yxatdan o'tish modal oynada: ism, yosh, 2 ta telefon, fan va daraja.
const showRegister = ref(false)
const catalog = reactive({ subjects: [] })
const catalogLoading = ref(false)
const reg = reactive({ full_name: '', age: '', phone: '', phone2: '', subject: '', level: '' })
const selectedSubject = computed(() => catalog.subjects.find(item => item.id === reg.subject))

// Backend xabarlari o'zbekcha, ular to'g'ridan-to'g'ri ko'rsatiladi.
function errorText(e, fallback) {
  if (e.response?.status === 429) return 'Juda ko‘p urinish. 10 daqiqadan keyin qayta urinib ko‘ring.'
  return e.response?.data?.detail || fallback
}

async function openRegister() {
  showRegister.value = true
  regError.value = ''
  if (catalog.subjects.length) return
  catalogLoading.value = true
  try {
    const res = await api.get('/exam/catalog/')
    catalog.subjects = res.data.subjects || []
  } catch (e) {
    regError.value = 'Fanlar ro‘yxatini yuklab bo‘lmadi. Sahifani yangilang.'
  } finally {
    catalogLoading.value = false
  }
}

function closeRegister() {
  if (loading.value) return
  showRegister.value = false
}

// Telefon maskasi: bosilganda "+998 " o'zi chiqadi, raqam yozilgach bo'shliqlar
// "+998 99 999 99 99" ko'rinishida o'zi qo'yiladi.
const PHONE_PREFIX = '+998 '

function formatPhone(value) {
  let digits = String(value || '').replace(/\D/g, '')
  // "+998 " turgan joyga to'liq raqam (+998...) qo'yilsa ham prefiks ikki marta tushmasin.
  if (digits.startsWith('998')) digits = digits.slice(3)
  while (digits.length > 9 && digits.startsWith('998')) digits = digits.slice(3)
  digits = digits.slice(0, 9)
  const parts = [digits.slice(0, 2), digits.slice(2, 5), digits.slice(5, 7), digits.slice(7, 9)].filter(Boolean)
  return PHONE_PREFIX + parts.join(' ')
}

function phoneFocus(field) {
  if (!reg[field]) reg[field] = PHONE_PREFIX
}

function phoneBlur(field) {
  if (reg[field].trim() === PHONE_PREFIX.trim()) reg[field] = ''
}

function phoneInput(field, event) {
  const input = event.target
  const raw = input.value
  const caret = input.selectionStart ?? raw.length
  let digitsBefore = raw.slice(0, caret).replace(/\D/g, '').length
  if (!raw.replace(/\D/g, '').startsWith('998')) digitsBefore += 3
  const formatted = formatPhone(raw)
  reg[field] = formatted
  input.value = formatted
  // Kursor o'rnini saqlaymiz: o'rtadan tahrirlanganda oxiriga sakrab ketmasin.
  let pos = formatted.length
  if (caret < raw.length) {
    let seen = 0
    for (let i = 0; i < formatted.length; i += 1) {
      if (seen >= Math.max(digitsBefore, 3)) { pos = i; break }
      if (/\d/.test(formatted[i])) seen += 1
    }
  }
  pos = Math.max(pos, PHONE_PREFIX.length)
  input.setSelectionRange(pos, pos)
}

function phoneComplete(value) {
  return String(value || '').replace(/\D/g, '').length === 12
}

async function register() {
  if (!phoneComplete(reg.phone) || !phoneComplete(reg.phone2)) {
    regError.value = 'Telefon raqamni to‘liq kiriting: +998 99 999 99 99'
    return
  }
  loading.value = true
  regError.value = ''
  try {
    const res = await api.post('/exam/register/', {
      full_name: reg.full_name,
      age: reg.age,
      phone: reg.phone,
      phone2: reg.phone2,
      level: reg.level,
    })
    // Kod o'quvchiga ko'rsatilmaydi, faqat testni ochish uchun ichkarida ishlatiladi.
    const finalCode = res.data.code
    const start = await api.post('/exam/start/', { code: finalCode })
    sessionStorage.setItem('exam_payload', JSON.stringify({ ...start.data, code: finalCode }))
    router.push('/exam')
  } catch (e) {
    regError.value = errorText(e, 'Ro‘yxatdan o‘tib bo‘lmadi. Qaytadan urinib ko‘ring.')
  } finally {
    loading.value = false
  }
}
</script>

<style>
/* 3D rasm olib tashlangan: sarlavha va code kartasi sahifa o'rtasida bitta ustunda. */
.xz-entry-grid.xz-entry-single {
  grid-template-columns: minmax(0, 1fr);
  justify-items: center;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

.xz-entry-single .xz-entry-copy {
  width: 100%;
  grid-template-columns: minmax(0, 1fr);
  justify-items: center;
  text-align: center;
}

.xz-open-register {
  display: block;
  width: 100%;
  margin: 18px 0 14px;
}

.xz-register-modal {
  width: min(560px, calc(100vw - 32px));
  max-height: calc(100vh - 32px);
  overflow-y: auto;
  text-align: left;
}

.xz-entry-single .xz-stage-login {
  margin: 0 auto;
  text-align: center;
}

.xz-entry-single .xz-card-badges {
  justify-content: center;
}

.xz-entry-single .xz-login-card,
.xz-entry-single .xz-login-card h2,
.xz-entry-single .xz-login-card .entry-subtitle {
  text-align: center !important;
}

.xz-entry-single .entry-admin-link {
  display: table !important;
  margin-left: auto !important;
  margin-right: auto !important;
}
</style>
