<template>
  <div class="test-upload">
    <div class="page-head">
      <div>
        <h2>Test yuklash</h2>
        <p>Fan va darajani tanlang (yo‘q bo‘lsa shu yerda yarating), keyin Word (.docx) faylni yuklang. Saqlangan test o‘quvchilarga darhol chiqadi.</p>
      </div>
      <button type="button" class="secondary-btn" :disabled="templateLoading" @click="downloadTemplate">
        {{ templateLoading ? 'Yuklanmoqda...' : 'Namuna Word fayl' }}
      </button>
    </div>

    <div class="tu-steps">
      <!-- 1. Fan -->
      <section class="panel tu-step" :class="{ done: subjectId }">
        <div class="tu-step-head"><span class="tu-num">1</span><h3>Fan</h3></div>
        <select v-model="subjectChoice" @change="onSubjectChange">
          <option value="">Fanni tanlang</option>
          <option v-for="s in subjects" :key="s.id" :value="String(s.id)">{{ s.name }}</option>
          <option value="new">+ Yangi fan qo‘shish</option>
        </select>
        <div v-if="subjectChoice === 'new'" class="tu-new">
          <input v-model.trim="newSubject" placeholder="Masalan: Matematika" @keyup.enter="createSubject" />
          <button type="button" class="primary-btn" :disabled="!newSubject || busy" @click="createSubject">Fanni yaratish</button>
        </div>
      </section>

      <!-- 2. Daraja -->
      <section class="panel tu-step" :class="{ done: levelId, locked: !subjectId }">
        <div class="tu-step-head"><span class="tu-num">2</span><h3>Daraja</h3></div>
        <p v-if="!subjectId" class="tu-muted">Avval fanni tanlang yoki yarating.</p>
        <template v-else>
          <select v-model="levelChoice" @change="onLevelChange">
            <option value="">Darajani tanlang</option>
            <option v-for="l in levels" :key="l.id" :value="String(l.id)">
              {{ l.name }} — {{ countFor(l.id) }} ta savol, {{ l.duration_minutes }} daqiqa
            </option>
            <option value="new">+ Yangi daraja qo‘shish</option>
          </select>
          <div v-if="levelChoice === 'new'" class="tu-new tu-new-level">
            <input v-model.trim="newLevel" placeholder="Masalan: 5-sinf yoki Advanced" @keyup.enter="createLevel" />
            <label class="tu-minutes">
              <input v-model.number="newMinutes" type="number" min="1" max="300" />
              <span>daqiqa</span>
            </label>
            <button type="button" class="primary-btn" :disabled="!newLevel || busy" @click="createLevel">Darajani yaratish</button>
          </div>
        </template>
      </section>

      <!-- 3. Word fayl -->
      <section class="panel tu-step" :class="{ locked: !levelId }">
        <div class="tu-step-head"><span class="tu-num">3</span><h3>Word fayl</h3></div>
        <p v-if="!levelId" class="tu-muted">Avval darajani tanlang yoki yarating.</p>
        <template v-else>
          <label class="tu-drop" :class="{ has: file }">
            <input type="file" accept=".docx" @change="onFile" />
            <strong>{{ file ? file.name : 'Word faylni tanlang (.docx)' }}</strong>
            <span>Savol, A) B) C) D) variantlar va "Javob: B" qatori</span>
          </label>
          <div v-if="countFor(levelId)" class="tu-mode">
            <label><input v-model="mode" type="radio" value="append" /> Mavjud {{ countFor(levelId) }} ta savolga qo‘shish</label>
            <label><input v-model="mode" type="radio" value="replace" /> Eski savollarni o‘chirib, yangisini qo‘yish</label>
          </div>
          <button type="button" class="primary-btn" :disabled="!file || busy" @click="preview">
            {{ busy ? 'O‘qilmoqda...' : 'Faylni tekshirish' }}
          </button>
        </template>
      </section>
    </div>

    <p v-if="error" class="error-box">{{ error }}</p>
    <p v-if="success" class="success-box">{{ success }}</p>

    <!-- Oldindan ko'rish -->
    <section v-if="parsed" class="panel tu-preview">
      <div class="tu-preview-head">
        <div>
          <h3>{{ parsed.subject }} · {{ parsed.level }}</h3>
          <p>
            Topildi: <b>{{ parsed.questions.length }}</b> ta savol
            <template v-if="parsed.errors.length"> · <span class="tu-bad">{{ parsed.errors.length }} ta savolda xato</span></template>
          </p>
        </div>
        <button type="button" class="primary-btn" :disabled="!parsed.questions.length || busy" @click="save">
          {{ busy ? 'Saqlanmoqda...' : `${parsed.questions.length} ta savolni saqlash` }}
        </button>
      </div>

      <p v-if="mode === 'replace' && parsed.existing_count" class="tu-warn">
        Diqqat: bu darajadagi eski {{ parsed.existing_count }} ta savol o‘chiriladi. Shu savollarga oldin berilgan o‘quvchi javoblari ham o‘chadi.
      </p>

      <div v-if="parsed.errors.length" class="tu-errors">
        <b>Bu savollar saqlanmaydi, Word faylda tuzatib qayta yuklang:</b>
        <ul><li v-for="e in parsed.errors" :key="e">{{ e }}</li></ul>
      </div>
      <details v-if="parsed.skipped.length" class="tu-skipped">
        <summary>Variantsiz {{ parsed.skipped.length }} ta matn test sifatida olinmadi (sarlavha yoki izoh)</summary>
        <ul><li v-for="(s, i) in parsed.skipped" :key="i">{{ s }}</li></ul>
      </details>

      <ol class="tu-list">
        <li v-for="(q, i) in parsed.questions" :key="i" class="tu-q">
          <p class="tu-q-text">{{ q.text }}</p>
          <div class="tu-opts">
            <span
              v-for="letter in ['A', 'B', 'C', 'D']"
              v-show="q['option_' + letter.toLowerCase()]"
              :key="letter"
              :class="{ correct: q.correct_answer === letter }"
            >
              <b>{{ letter }})</b> {{ q['option_' + letter.toLowerCase()] }}
            </span>
          </div>
        </li>
      </ol>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api from '../api/axios'

const subjects = ref([])
const allLevels = ref([])
const counts = ref({})
const subjectChoice = ref('')
const levelChoice = ref('')
const newSubject = ref('')
const newLevel = ref('')
const newMinutes = ref(30)
const file = ref(null)
const mode = ref('append')
const parsed = ref(null)
const busy = ref(false)
const templateLoading = ref(false)
const error = ref('')
const success = ref('')

const subjectId = computed(() => (/^\d+$/.test(subjectChoice.value) ? Number(subjectChoice.value) : null))
const levelId = computed(() => (/^\d+$/.test(levelChoice.value) ? Number(levelChoice.value) : null))
const levels = computed(() => allLevels.value.filter(l => l.subject === subjectId.value))

function detail(e, fallback) {
  const data = e?.response?.data
  if (typeof data?.detail === 'string') return data.detail
  if (data && typeof data === 'object') {
    const first = Object.values(data).flat()[0]
    if (typeof first === 'string') return first
  }
  return fallback
}

function countFor(id) {
  return counts.value[id] || 0
}

async function loadAll() {
  const [s, l, q] = await Promise.all([api.get('/subjects/'), api.get('/levels/'), api.get('/questions/')])
  subjects.value = s.data.results || s.data
  allLevels.value = l.data.results || l.data
  const map = {}
  for (const item of q.data.results || q.data) map[item.level] = (map[item.level] || 0) + 1
  counts.value = map
}

function resetAfterLevel() {
  parsed.value = null
  file.value = null
  mode.value = 'append'
  success.value = ''
}

function onSubjectChange() {
  levelChoice.value = ''
  error.value = ''
  resetAfterLevel()
}

function onLevelChange() {
  error.value = ''
  resetAfterLevel()
}

async function createSubject() {
  if (!newSubject.value) return
  const existing = subjects.value.find(s => s.name.toLowerCase() === newSubject.value.toLowerCase())
  if (existing) {
    subjectChoice.value = String(existing.id)
    newSubject.value = ''
    return
  }
  busy.value = true
  error.value = ''
  try {
    const res = await api.post('/subjects/', { name: newSubject.value })
    await loadAll()
    subjectChoice.value = String(res.data.id)
    newSubject.value = ''
    levelChoice.value = 'new'
  } catch (e) {
    error.value = detail(e, 'Fanni yaratib bo‘lmadi.')
  } finally {
    busy.value = false
  }
}

async function createLevel() {
  if (!newLevel.value || !subjectId.value) return
  const existing = levels.value.find(l => l.name.toLowerCase() === newLevel.value.toLowerCase())
  if (existing) {
    levelChoice.value = String(existing.id)
    newLevel.value = ''
    return
  }
  busy.value = true
  error.value = ''
  try {
    const res = await api.post('/levels/', {
      subject: subjectId.value,
      name: newLevel.value,
      duration_minutes: newMinutes.value || 30,
    })
    await loadAll()
    levelChoice.value = String(res.data.id)
    newLevel.value = ''
  } catch (e) {
    error.value = detail(e, 'Darajani yaratib bo‘lmadi.')
  } finally {
    busy.value = false
  }
}

function onFile(event) {
  file.value = event.target.files?.[0] || null
  parsed.value = null
  success.value = ''
  error.value = ''
}

function formData(saveIt) {
  const data = new FormData()
  data.append('file', file.value)
  data.append('level', levelId.value)
  data.append('mode', mode.value)
  data.append('save', saveIt ? '1' : '0')
  return data
}

async function preview() {
  busy.value = true
  error.value = ''
  success.value = ''
  try {
    const res = await api.post('/questions/import-word/', formData(false))
    parsed.value = res.data
    if (!res.data.questions.length) error.value = 'Faylda savol topilmadi. Namuna Word faylga qarab tekshiring.'
  } catch (e) {
    parsed.value = null
    error.value = detail(e, 'Faylni o‘qib bo‘lmadi.')
  } finally {
    busy.value = false
  }
}

async function save() {
  if (mode.value === 'replace' && parsed.value?.existing_count) {
    const ok = window.confirm(`Bu darajadagi eski ${parsed.value.existing_count} ta savol o‘chiriladi. Davom etasizmi?`)
    if (!ok) return
  }
  busy.value = true
  error.value = ''
  try {
    const res = await api.post('/questions/import-word/', formData(true))
    success.value = `${res.data.subject} · ${res.data.level}: ${res.data.saved} ta savol saqlandi. Darajada jami ${res.data.total} ta savol. O‘quvchilar endi bu testni ro‘yxatdan o‘tish oynasida tanlay oladi.`
    parsed.value = null
    file.value = null
    await loadAll()
  } catch (e) {
    error.value = detail(e, 'Saqlab bo‘lmadi.')
  } finally {
    busy.value = false
  }
}

async function downloadTemplate() {
  templateLoading.value = true
  try {
    const res = await api.get('/questions/word-template/', { responseType: 'blob' })
    const url = URL.createObjectURL(res.data)
    const link = document.createElement('a')
    link.href = url
    link.download = 'test_namunasi.docx'
    document.body.appendChild(link)
    link.click()
    link.remove()
    setTimeout(() => URL.revokeObjectURL(url), 2000)
  } catch {
    error.value = 'Namuna faylni yuklab bo‘lmadi.'
  } finally {
    templateLoading.value = false
  }
}

onMounted(async () => {
  try {
    await loadAll()
  } catch (e) {
    error.value = detail(e, 'Fanlar ro‘yxatini yuklab bo‘lmadi.')
  }
})
</script>

<style scoped>
.tu-steps {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  align-items: start;
}

.tu-step {
  display: grid;
  gap: 12px;
  transition: opacity 0.2s ease;
}

.tu-step.locked { opacity: 0.6; }

.tu-step-head {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tu-step-head h3 { margin: 0 !important; }

.tu-num {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  font-weight: 800;
  font-size: 14px;
  color: #fff;
  background: var(--bx-primary, #0f7d8f);
}

.tu-step.done .tu-num { background: var(--bx-gold, #c9a23d); }

.tu-step select,
.tu-step input:not([type=radio]):not([type=file]) {
  width: 100%;
  min-height: 44px;
  padding: 0 12px;
}

.tu-new { display: grid; gap: 8px; }
.tu-new-level { grid-template-columns: 1fr; }

.tu-minutes {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tu-minutes input { max-width: 110px; }
.tu-minutes span { color: var(--bx-muted, #6f6650); font-weight: 600; }

.tu-muted { margin: 0; color: var(--bx-muted, #6f6650); font-size: 14px; }

.tu-drop {
  position: relative;
  display: grid;
  gap: 4px;
  padding: 18px 14px;
  border: 2px dashed var(--bx-border-strong, #d8cbae);
  border-radius: 14px;
  background: var(--bx-surface-2, #fbf8f1);
  text-align: center;
  cursor: pointer;
}

.tu-drop.has { border-color: var(--bx-primary, #0f7d8f); background: var(--bx-primary-soft, rgba(20, 163, 181, 0.12)); }
.tu-drop input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
.tu-drop strong { color: var(--bx-text, #13294b); word-break: break-all; }
.tu-drop span { font-size: 12.5px; color: var(--bx-muted, #6f6650); }

.tu-mode { display: grid; gap: 6px; font-size: 14px; }
.tu-mode label { display: flex; gap: 8px; align-items: center; font-weight: 600 !important; }

.tu-preview { margin-top: 18px; }

.tu-preview-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.tu-preview-head h3 { margin: 0 0 4px !important; }
.tu-preview-head p { margin: 0; color: var(--bx-muted, #6f6650); }
.tu-bad { color: var(--bx-danger, #c0392b); font-weight: 700; }

.tu-warn {
  margin: 14px 0 0;
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(201, 144, 14, 0.12);
  border: 1px solid rgba(201, 144, 14, 0.35);
  color: #8a5f00;
  font-weight: 600;
}

.tu-errors {
  margin-top: 14px;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(192, 57, 43, 0.08);
  border: 1px solid rgba(192, 57, 43, 0.3);
  color: var(--bx-danger, #c0392b);
}

.tu-errors ul,
.tu-skipped ul { margin: 8px 0 0; padding-left: 20px; }

.tu-skipped { margin-top: 12px; color: var(--bx-muted, #6f6650); font-size: 14px; }
.tu-skipped summary { cursor: pointer; font-weight: 600; }

.tu-list {
  margin: 16px 0 0;
  padding: 0;
  list-style: none;
  counter-reset: q;
  display: grid;
  gap: 10px;
}

.tu-q {
  counter-increment: q;
  padding: 14px 16px;
  border: 1px solid var(--bx-border, #e8dfcb);
  border-radius: 14px;
  background: var(--bx-surface-2, #fbf8f1);
}

.tu-q-text {
  margin: 0 0 10px;
  font-weight: 700;
  white-space: pre-wrap;
  color: var(--bx-text, #13294b);
}

.tu-q-text::before { content: counter(q) '. '; color: var(--bx-primary, #0f7d8f); }

.tu-opts {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 6px;
}

.tu-opts span {
  padding: 7px 10px;
  border-radius: 10px;
  border: 1px solid var(--bx-border, #e8dfcb);
  background: var(--bx-surface, #fff);
  font-size: 14px;
  color: var(--bx-text, #13294b);
}

.tu-opts span.correct {
  border-color: #1e8e5a;
  background: rgba(30, 142, 90, 0.12);
  color: #146b43;
  font-weight: 700;
}

@media (max-width: 1100px) {
  .tu-steps { grid-template-columns: 1fr; }
}

@media (max-width: 600px) {
  .tu-opts { grid-template-columns: 1fr; }
}
</style>
