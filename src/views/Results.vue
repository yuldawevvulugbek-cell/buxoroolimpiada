<template>
  <div>
    <div class="page-head">
      <div>
        <h2>Natijalar</h2>
        <p>Test natijalari: o‘quvchi, fan, daraja, nechtadan nechta to‘g‘ri va foiz</p>
      </div>
      <button class="primary-btn" @click="downloadExcel">Natijalarni Excelga yuklash</button>
    </div>

    <div class="panel hide-results-panel">
      <div>
        <h3>Test natijasini yashirish</h3>
        <p v-if="hideResults">Yoqilgan: o‘quvchi test tugagach nechta to‘g‘ri topganini va foizini ko‘rmaydi.</p>
        <p v-else>O‘chirilgan: o‘quvchi test tugagach nechta to‘g‘ri topganini va necha foiz olganini ko‘radi.</p>
        <p v-if="settingsError" class="error-box">{{ settingsError }}</p>
      </div>
      <label class="hide-results-switch" :class="{ on: hideResults, disabled: !mainAdmin || savingSettings }" :title="mainAdmin ? '' : 'Faqat bosh admin o‘zgartira oladi'">
        <input type="checkbox" :checked="hideResults" :disabled="!mainAdmin || savingSettings" @change="toggleHideResults($event.target.checked)" />
        <span class="hide-results-track"><i></i></span>
        <b>{{ hideResults ? 'Yoqiq' : 'O‘chiq' }}</b>
      </label>
    </div>

    <div class="filter-bar">
      <select v-if="mainAdmin" v-model="filters.center" @change="loadResults">
        <option value="">Barchasi</option>
        <option v-for="center in centers" :key="center.id" :value="center.id">{{ center.name }}</option>
      </select>
      <button class="secondary-btn" @click="loadResults">Yangilash</button>
    </div>


    <div class="panel">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>№</th>
              <th>O‘quvchi</th>
              <th>Yosh</th>
              <th>Telefon 1</th>
              <th>Telefon 2</th>
              <th>Fan</th>
              <th>Daraja/Sinf</th>
              <th>Version</th>
              <th>O‘quv markaz</th>
              <th>Code</th>
              <th>Nechta to‘g‘ri</th>
              <th>Foiz</th>
              <th>Vaqt</th>
              <th>Javoblar</th>
              <th>Sertifikat</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in results" :key="r.id">
              <td>{{ i + 1 }}</td>
              <td><b>{{ r.student_full_name }}</b></td>
              <td>{{ r.student_age || '—' }}</td>
              <td>{{ r.student_phone || '—' }}</td>
              <td>{{ r.student_phone2 || '—' }}</td>
              <td>{{ r.subject_name }}</td>
              <td>{{ r.level_name }}</td>
              <td>{{ r.student_selected_version ? `Version ${r.student_selected_version}` : '—' }}</td>
              <td>{{ r.center_name }}</td>
              <td>{{ r.student_code }}</td>
              <td><b>{{ r.correct_count }}/{{ r.total_questions }}</b></td>
              <td>{{ r.percent }}%</td>
              <td>{{ formatSeconds(r.spent_seconds) }}</td>
              <td>
                <button class="secondary-btn small-action-btn" @click="openResultDetails(r)">
                  Javoblarni ko‘rish
                </button>
              </td>
              <td>
                <button class="secondary-btn small-action-btn" @click="openCertificate(r)">
                  Sertifikat
                </button>
              </td>
            </tr>
            <tr v-if="!results.length">
              <td colspan="15" class="empty-cell">Natija topilmadi</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="certificateResult" class="modal-backdrop" @click.self="certificateResult = null">
      <div class="result-detail-modal certificate-modal">
        <div class="modal-head">
          <div>
            <h3>{{ certificateResult.student_full_name }} sertifikati</h3>
            <p>
              {{ certificateResult.subject_name }} • {{ certificateResult.level_name }}
            </p>
          </div>
          <button type="button" class="modal-close-btn" @click="certificateResult = null">×</button>
        </div>
        <CertificateCard :certificate="certificateFor(certificateResult)" />
      </div>
    </div>

    <div v-if="selectedResult" class="modal-backdrop" @click.self="closeResultDetails">
      <div class="result-detail-modal">
        <div class="modal-head">
          <div>
            <h3>{{ selectedResult.student_full_name }} javoblari</h3>
            <p>
              {{ selectedResult.subject_name }} • {{ selectedResult.level_name }}
              <span v-if="selectedResult.student_selected_version"> • Version {{ selectedResult.student_selected_version }}</span>
            </p>
          </div>
          <button type="button" class="modal-close-btn" @click="closeResultDetails">×</button>
        </div>

        <div class="result-detail-summary">
          <div v-if="selectedResult.student_phone">
            <span>Telefon</span>
            <b>{{ selectedResult.student_phone }}<template v-if="selectedResult.student_phone2">, {{ selectedResult.student_phone2 }}</template></b>
          </div>
          <div>
            <span>Code</span>
            <b>{{ selectedResult.student_code }}</b>
          </div>
          <div>
            <span>Natija</span>
            <b>{{ selectedResult.correct_count }}/{{ selectedResult.total_questions }}</b>
          </div>
          <div>
            <span>Foiz</span>
            <b>{{ selectedResult.percent }}%</b>
          </div>
          <div>
            <span>Vaqt</span>
            <b>{{ formatSeconds(selectedResult.spent_seconds) }}</b>
          </div>
        </div>

        <div v-if="isMentalResult" class="answers-list">
          <div v-for="task in mentalAnswers" :key="task.id" class="answer-detail-card" :class="task.is_correct ? 'answer-ok' : 'answer-bad'">
            <div class="answer-card-head">
              <strong>{{ task.task_order }}-misol</strong>
              <span>{{ task.is_correct ? 'To‘g‘ri' : 'Noto‘g‘ri' }}</span>
            </div>
            <p class="question-text">{{ task.expression }}</p>
            <div class="answer-meta-grid">
              <div>
                <span>O‘quvchi javobi</span>
                <b>{{ task.student_answer ?? 'Belgilanmagan' }}</b>
              </div>
              <div>
                <span>To‘g‘ri javob</span>
                <b>{{ task.correct_answer }}</b>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="answers-list">
          <div v-for="(answer, index) in normalAnswers" :key="answer.id" class="answer-detail-card" :class="answer.is_correct ? 'answer-ok' : 'answer-bad'">
            <div class="answer-card-head">
              <strong>{{ index + 1 }}-savol</strong>
              <span>{{ answer.is_correct ? 'To‘g‘ri' : 'Noto‘g‘ri' }}</span>
            </div>
            <p class="question-text" v-html="mathHtml(answer.question_text)"></p>

            <div v-if="answer.question_type === 'open'" class="answer-meta-grid">
              <div>
                <span>O‘quvchi yozgan javob</span>
                <b>{{ answer.written_answer || 'Yozilmagan' }}</b>
              </div>
              <div>
                <span>To‘g‘ri javob (kalit so‘zlar)</span>
                <b>{{ (answer.answer_text || '').split('|').join(' / ') }}</b>
              </div>
            </div>

            <div v-if="answer.question_type !== 'open'" class="option-review-list">
              <div v-for="letter in optionLetters" :key="letter" :class="optionClass(answer, letter)">
                <b>{{ letter }}</b>
                <span v-html="mathHtml(optionText(answer, letter))"></span>
              </div>
            </div>

            <div v-if="answer.question_type !== 'open'" class="answer-meta-grid">
              <div>
                <span>O‘quvchi belgilagan</span>
                <b>{{ answerLabel(answer.selected_answer) }}</b>
              </div>
              <div>
                <span>To‘g‘ri javob</span>
                <b>{{ answerLabel(answer.correct_answer) }}</b>
              </div>
            </div>
          </div>

          <div v-if="!normalAnswers.length" class="empty-cell">
            Bu natija uchun savollar bo‘yicha javoblar topilmadi.
          </div>
        </div>

        <div class="modal-actions">
          <button class="secondary-btn" @click="closeResultDetails">Yopish</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { mathHtml } from '../utils/math'
import { computed, onMounted, reactive, ref } from 'vue'
import api from '../api/axios'
import CertificateCard from '../components/CertificateCard.vue'
import { useBranches } from '../composables/useBranches'
import { useCenters } from '../composables/useCenters'
import { fetchCurrentAdmin, getStoredAdminProfile, isMainAdmin } from '../utils/auth'

const results = ref([])
const selectedResult = ref(null)
const currentAdmin = ref(getStoredAdminProfile())
const { branches, loadBranches, addBranch } = useBranches()
const { centers, loadCenters } = useCenters()
const newBranchName = ref('')
const addingBranch = ref(false)
const branchMessage = ref('')
const branchError = ref('')
const filters = reactive({ center: '', branch: '' })
const mainAdmin = computed(() => isMainAdmin(currentAdmin.value))
const optionLetters = ['A', 'B', 'C', 'D']
const normalAnswers = computed(() => selectedResult.value?.answers || [])
const mentalAnswers = computed(() => selectedResult.value?.mental_answers || [])
const isMentalResult = computed(() => mentalAnswers.value.length > 0)
const certificateResult = ref(null)

function openCertificate(result) {
  certificateResult.value = result
}

// Admin o'quvchiga berilgan sertifikatning aynan o'zini ko'radi (foiz bo'lgan-bo'lmaganiga qarab).
function certificateFor(result) {
  return {
    number: result.certificate_number,
    full_name: result.student_full_name,
    subject_name: result.subject_name,
    level_name: result.level_name,
    issued_at: result.finished_at,
    percent: result.percent,
  }
}

const hideResults = ref(true)
const savingSettings = ref(false)
const settingsError = ref('')

async function loadSettings() {
  try {
    const res = await api.get('/settings/')
    hideResults.value = Boolean(res.data.hide_results)
  } catch {
    settingsError.value = 'Sozlamani yuklab bo‘lmadi.'
  }
}

async function toggleHideResults(value) {
  savingSettings.value = true
  settingsError.value = ''
  const previous = hideResults.value
  hideResults.value = value
  try {
    const res = await api.patch('/settings/', { hide_results: value })
    hideResults.value = Boolean(res.data.hide_results)
  } catch (e) {
    hideResults.value = previous
    settingsError.value = e.response?.data?.detail || 'Sozlamani saqlab bo‘lmadi.'
  } finally {
    savingSettings.value = false
  }
}

function formatSeconds(seconds) {
  const total = Number(seconds || 0)
  const min = Math.floor(total / 60)
  const sec = total % 60
  return `${min} daq ${sec} sek`
}

function answerLabel(value) {
  return value ? value : 'Belgilanmagan'
}

function optionText(answer, letter) {
  return answer?.[`option_${letter.toLowerCase()}`] || ''
}

function optionClass(answer, letter) {
  return {
    'option-review-item': true,
    'student-selected': answer?.selected_answer === letter,
    'correct-option': answer?.correct_answer === letter,
  }
}

function openResultDetails(result) {
  selectedResult.value = result
}

function closeResultDetails() {
  selectedResult.value = null
}

async function createBranch() {
  branchMessage.value = ''
  branchError.value = ''
  addingBranch.value = true
  try {
    const savedName = await addBranch(newBranchName.value)
    filters.branch = savedName
    newBranchName.value = ''
    branchMessage.value = 'Filial qo‘shildi.'
    await Promise.all([loadBranches(), loadCenters()])
    await loadResults()
  } catch (e) {
    branchError.value = e.message || JSON.stringify(e.response?.data || 'Filial qo‘shishda xatolik')
  } finally {
    addingBranch.value = false
  }
}

async function loadCurrentAdmin() {
  try {
    currentAdmin.value = await fetchCurrentAdmin()
    if (!mainAdmin.value && currentAdmin.value?.branch) filters.branch = currentAdmin.value.branch
  } catch {
    currentAdmin.value = getStoredAdminProfile()
  }
}

async function loadResults() {
  const params = {}
  if (filters.center && mainAdmin.value) params.center = filters.center
  if (filters.branch && mainAdmin.value) params.branch = filters.branch
  const res = await api.get('/results/', { params })
  results.value = res.data
}

async function downloadExcel() {
  const params = {}
  if (filters.center && mainAdmin.value) params.center = filters.center
  if (filters.branch && mainAdmin.value) params.branch = filters.branch
  const res = await api.get('/results/export-excel/', { params, responseType: 'blob', timeout: 0 })
  const url = window.URL.createObjectURL(new Blob([res.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'olimpiada_natijalari.xlsx')
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

onMounted(async () => {
  await loadCurrentAdmin()
  await Promise.all([loadBranches(), loadCenters(), loadSettings()])
  await loadResults()
})
</script>

<style scoped>
.hide-results-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 16px;
}

.hide-results-panel h3 {
  margin: 0 0 6px;
}

.hide-results-panel p {
  margin: 0;
  opacity: 0.85;
}

.hide-results-switch {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  flex-shrink: 0;
  user-select: none;
}

.hide-results-switch.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.hide-results-switch input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.hide-results-track {
  position: relative;
  width: 54px;
  height: 30px;
  border-radius: 999px;
  background: #94a3b8;
  transition: background 0.2s ease;
}

.hide-results-track i {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
  transition: transform 0.2s ease;
}

.hide-results-switch.on .hide-results-track {
  background: #22c55e;
}

.hide-results-switch.on .hide-results-track i {
  transform: translateX(24px);
}

.hide-results-switch input:focus-visible + .hide-results-track {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

.certificate-modal {
  width: min(1160px, calc(100vw - 24px));
}

.certificate-modal :deep(.secondary-btn) {
  background: #eef3ff !important;
  color: #1d4ed8 !important;
  border: 1px solid #c7d6f7 !important;
}

@media (max-width: 640px) {
  .hide-results-panel {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
