import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import tilt from './directives/tilt'
import { wakeBackend } from './api/axios'
import 'katex/dist/katex.min.css'
import './assets/styles.css'
import './assets/xorazm.css'
import './assets/sky.css'
import './assets/admin-buxoro.css'

wakeBackend()

createApp(App).use(router).directive('tilt', tilt).mount('#app')
