<template>
  <div>
    <div class="page-head">
      <div>
        <h2>Adminlar</h2>
        <p>Kichik admin yarating va unga o‘quv markazni biriktiring.</p>
      </div>
    </div>

    <div class="grid-2">
      <div class="panel">
        <h3>Admin yaratish</h3>
        <form @submit.prevent="createAdmin" class="form-grid">
          <label>Login <input v-model="form.username" required /></label>
          <label>Parol <input v-model="form.password" type="password" required minlength="6" /></label>
          <label>O‘quv markaz
            <select v-model="form.center" required>
              <option value="">O‘quv markaz tanlang</option>
              <option v-for="center in centers" :key="center.id" :value="center.id">{{ center.name }}</option>
            </select>
          </label>

          <button class="primary-btn">Yaratish</button>
        </form>
        <p v-if="message" class="success-box">{{ message }}</p>
        <p v-if="error" class="error-box">{{ error }}</p>
      </div>

      <div class="panel">
        <h3>Adminlar ro‘yxati</h3>
        <div class="list-cards">
          <div v-for="admin in admins" :key="admin.id" class="mini-card">
            <b>{{ admin.username }}</b>
            <small><b>O‘quv markaz:</b> {{ admin.center_name || 'Bosh admin' }}</small>
            <small v-if="admin.branch"><b>Filial:</b> {{ admin.branch }}</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import api from '../api/axios'
import { useBranches } from '../composables/useBranches'
import { useCenters } from '../composables/useCenters'

const admins = ref([])
const message = ref('')
const error = ref('')
const { branches, loadBranches, addBranch } = useBranches()
const { centers, loadCenters } = useCenters()
const newBranchName = ref('')
const addingBranch = ref(false)
const form = reactive({ username: '', password: '', center: '', branch: '' })

async function loadAdmins() {
  const res = await api.get('/accounts/admins/')
  admins.value = res.data
}


async function createBranch() {
  error.value = ''
  addingBranch.value = true
  try {
    const savedName = await addBranch(newBranchName.value)
    form.branch = savedName
    newBranchName.value = ''
  } catch (e) {
    error.value = e.message || JSON.stringify(e.response?.data || 'Filial qo‘shishda xatolik')
  } finally {
    addingBranch.value = false
  }
}

async function createAdmin() {
  message.value = ''
  error.value = ''
  try {
    await api.post('/accounts/admins/', form)
    Object.assign(form, { username: '', password: '', center: '', branch: '' })
    message.value = 'Admin yaratildi.'
    await loadAdmins()
  } catch (e) {
    error.value = JSON.stringify(e.response?.data || 'Xatolik')
  }
}

onMounted(async () => {
  await Promise.all([loadAdmins(), loadBranches(), loadCenters()])
})
</script>
