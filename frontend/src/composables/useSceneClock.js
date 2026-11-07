import { onBeforeUnmount, onMounted, ref } from 'vue'

// Manzara fonini va kirish sahifasidagi yozuvni bir xil vaqtda almashtiradigan umumiy soat.
const SCENE_COUNT = 3
const SCENE_MS = 9000
const sceneIndex = ref(0)
let users = 0
let timer = null

export function useSceneClock({ run = true } = {}) {
  onMounted(() => {
    if (!run) return
    const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    users += 1
    if (users === 1 && !reduceMotion) {
      timer = setInterval(() => {
        sceneIndex.value = (sceneIndex.value + 1) % SCENE_COUNT
      }, SCENE_MS)
    }
  })

  onBeforeUnmount(() => {
    if (!run) return
    users = Math.max(0, users - 1)
    if (!users) {
      clearInterval(timer)
      timer = null
    }
  })

  return { sceneIndex }
}
