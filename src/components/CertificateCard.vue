<template>
  <div class="certificate-card">
    <div class="certificate-preview" v-html="svg"></div>
    <div class="certificate-actions">
      <button type="button" class="primary-btn" :disabled="busy" @click="download">
        {{ busy ? 'Tayyorlanmoqda...' : 'Sertifikatni yuklab olish' }}
      </button>
      <button type="button" class="secondary-btn" @click="print">Chop etish / PDF</button>
    </div>
    <p v-if="error" class="error-box">{{ error }}</p>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { certificateSvg, downloadCertificatePng, loadCertificateAssets, printCertificate } from '../utils/certificate'

const props = defineProps({
  certificate: { type: Object, required: true },
})

const busy = ref(false)
const error = ref('')
// Kalon minorasi fotosurati yuklangach sertifikat rasm bilan qayta chiziladi.
const photo = ref('')
const svg = computed(() => certificateSvg(props.certificate, photo.value))

onMounted(async () => {
  photo.value = await loadCertificateAssets()
})

async function download() {
  busy.value = true
  error.value = ''
  try {
    await downloadCertificatePng(props.certificate)
  } catch (e) {
    error.value = 'Yuklab bo‘lmadi. "Chop etish / PDF" tugmasidan foydalaning.'
  } finally {
    busy.value = false
  }
}

function print() {
  error.value = ''
  if (!printCertificate(props.certificate)) {
    error.value = 'Brauzer yangi oynani to‘sib qo‘ydi. Qalqib chiquvchi oynalarga ruxsat bering.'
  }
}
</script>

<style scoped>
.certificate-card {
  display: grid;
  gap: 14px;
  width: 100%;
}

.certificate-preview {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(3, 12, 48, 0.25);
  line-height: 0;
}

.certificate-preview :deep(svg) {
  width: 100%;
  height: auto;
}

.certificate-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.certificate-actions button {
  width: 100%;
  margin: 0;
}

@media (max-width: 520px) {
  .certificate-actions {
    grid-template-columns: 1fr;
  }
}
</style>
