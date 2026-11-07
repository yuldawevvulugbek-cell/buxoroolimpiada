<template>
  <div class="sky-scenes" :class="{ 'is-still': still, 'is-photo': !still }" aria-hidden="true">
    <template v-if="!still">
      <div
        v-for="(photo, index) in photos"
        :key="photo.src"
        class="photo-scene"
        :class="{ active: index === activeIndex }"
      >
        <div
          class="photo-image"
          :class="`pan-${photo.pan}`"
          :style="{ backgroundImage: `url(${photo.src})`, backgroundPosition: photo.pos }"
        ></div>
      </div>
      <div class="photo-light"></div>
      <div class="photo-shade"></div>
      <span class="photo-credit">Foto: Wikimedia Commons (Bgag, travelmag.com CC BY 2.0, B. Gagnon)</span>
    </template>
    <svg
      v-for="(scene, index) in shownScenes"
      v-else
      :key="scene"
      class="sky-scene"
      :class="{ active: index === activeIndex }"
      viewBox="0 0 1600 900"
      preserveAspectRatio="xMidYMid slice"
    >
      <defs>
        <linearGradient :id="`sky-${scene}`" x1="0" y1="0" x2="0" y2="1">
          <stop v-for="stop in look[scene].sky" :key="stop[0]" :offset="stop[0]" :stop-color="stop[1]" />
        </linearGradient>
        <radialGradient :id="`sun-${scene}`" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" :stop-color="look[scene].sun[0]" stop-opacity="0.95" />
          <stop offset="0.3" :stop-color="look[scene].sun[1]" stop-opacity="0.5" />
          <stop offset="1" :stop-color="look[scene].sun[1]" stop-opacity="0" />
        </radialGradient>
        <radialGradient :id="`cloud-${scene}`" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" :stop-color="look[scene].cloud" stop-opacity="0.9" />
          <stop offset="0.6" :stop-color="look[scene].cloud" stop-opacity="0.45" />
          <stop offset="1" :stop-color="look[scene].cloud" stop-opacity="0" />
        </radialGradient>
        <linearGradient :id="`sand-${scene}`" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" :stop-color="look[scene].sand[0]" />
          <stop offset="1" :stop-color="look[scene].sand[1]" />
        </linearGradient>
        <linearGradient :id="`dome-${scene}`" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" :stop-color="look[scene].dome[0]" />
          <stop offset="0.45" :stop-color="look[scene].dome[1]" />
          <stop offset="1" :stop-color="look[scene].dome[2]" />
        </linearGradient>
        <linearGradient :id="`water-${scene}`" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#7fd3d8" />
          <stop offset="0.5" stop-color="#2b8fa3" />
          <stop offset="1" stop-color="#145a73" />
        </linearGradient>
        <!-- Buxoro koshinlaridagi sakkiz qirrali yulduz naqshi -->
        <pattern :id="`girih-${scene}`" width="80" height="80" patternUnits="userSpaceOnUse">
          <path d="M40 8 L48 32 L72 40 L48 48 L40 72 L32 48 L8 40 L32 32Z" fill="none" stroke="#ffffff" stroke-width="1.2" />
          <rect x="28" y="28" width="24" height="24" transform="rotate(45 40 40)" fill="none" stroke="#ffffff" stroke-width="1" />
        </pattern>
      </defs>

      <g class="sky-zoom">
        <rect width="1600" height="900" :fill="`url(#sky-${scene})`" />
        <rect width="1600" height="520" :fill="`url(#girih-${scene})`" :opacity="look[scene].girih" />
        <circle :cx="look[scene].sunAt[0]" :cy="look[scene].sunAt[1]" :r="look[scene].sunAt[2]" :fill="`url(#sun-${scene})`" />

        <!-- 1. Kunduz: Minorai Kalon va Kalon masjidining moviy gumbazi -->
        <template v-if="scene === 'kalon'">
          <ellipse v-for="c in dayClouds" :key="c.x" :cx="c.x" :cy="c.y" :rx="c.rx" :ry="c.ry" :fill="`url(#cloud-${scene})`" class="sky-drift" :style="{ animationDelay: c.d }" />
          <g class="sky-birds">
            <path v-for="b in birds" :key="b.x" :d="`M${b.x} ${b.y} q10 -10 20 0 q10 -10 20 0`" fill="none" stroke="#1d3557" stroke-width="3" stroke-linecap="round" :style="{ animationDelay: b.d }" />
          </g>
          <path :d="dunes.far" fill="#e7c792" />
          <g fill="#c99560">
            <rect x="80" y="610" width="420" height="140" />
            <rect v-for="i in 10" :key="`m${i}`" :x="66 + i * 42" y="596" width="22" height="18" rx="4" />
          </g>
          <!-- Kalon masjidi: peshtoq va gumbaz -->
          <g>
            <rect x="380" y="470" width="190" height="280" fill="#d8a96e" />
            <path d="M412 750 L412 560 Q475 470 538 560 L538 750Z" fill="#0f5f78" />
            <path d="M424 750 L424 568 Q475 492 526 568 L526 750Z" fill="#1c8aa5" opacity="0.55" />
            <rect x="380" y="470" width="190" height="16" fill="#1aa6b7" />
            <rect x="606" y="520" width="200" height="230" fill="#cf9f66" />
            <rect x="640" y="470" width="132" height="56" fill="#c79358" />
            <path d="M632 472 Q632 350 706 330 Q780 350 780 472Z" :fill="`url(#dome-${scene})`" />
            <path v-for="r in 5" :key="`rib${r}`" :d="`M${648 + r * 20} 470 Q${650 + r * 18} 380 706 334`" fill="none" stroke="#0b6b7c" stroke-width="2" opacity="0.5" />
            <rect x="702" y="306" width="8" height="30" fill="#e7c792" />
            <circle cx="706" cy="302" r="7" fill="#f2c14e" />
          </g>
          <!-- Minorai Kalon -->
          <g>
            <path d="M968 750 L1088 750 L1068 250 L988 250Z" fill="#c9915a" />
            <path d="M968 750 L1028 750 L1018 250 L988 250Z" fill="#b57f4b" opacity="0.6" />
            <rect v-for="band in kalonBands" :key="band" :x="972 + (750 - band) * 0.004" :y="band" :width="112 - (750 - band) * 0.08" height="7" fill="#9e6a3b" opacity="0.7" />
            <rect x="976" y="232" width="104" height="22" fill="#1aa6b7" />
            <rect x="970" y="190" width="116" height="46" fill="#d7a468" />
            <path v-for="a in 5" :key="`arc${a}`" :d="`M${968 + a * 20} 232 L${968 + a * 20} 208 Q${976 + a * 20} 196 ${984 + a * 20} 208 L${984 + a * 20} 232Z`" fill="#5b3a22" />
            <rect x="976" y="176" width="104" height="16" fill="#c08850" />
            <path d="M990 176 L1066 176 L1056 150 L1000 150Z" fill="#b57f4b" />
          </g>
          <g fill="#2f6b3a" opacity="0.85">
            <ellipse v-for="t in poplars" :key="t" :cx="t" cy="700" rx="14" ry="60" />
          </g>
          <path :d="dunes.near" :fill="`url(#sand-${scene})`" />
        </template>

        <!-- 2. Quyosh botishi: Ark qal'asi -->
        <template v-else-if="scene === 'ark'">
          <ellipse v-for="c in eveningClouds" :key="c.x" :cx="c.x" :cy="c.y" :rx="c.rx" :ry="c.ry" :fill="`url(#cloud-${scene})`" class="sky-drift" :style="{ animationDelay: c.d }" />
          <path :d="dunes.far" fill="#b9735a" opacity="0.6" />
          <g fill="#8a4b3a">
            <path d="M120 760 L220 520 L700 520 L760 760Z" />
            <path d="M840 760 L900 520 L1400 520 L1500 760Z" />
            <circle v-for="m in arkMerlons" :key="m" :cx="m" cy="520" r="15" />
          </g>
          <g fill="#7a3f31">
            <path d="M700 760 L716 430 L800 430 L800 760Z" />
            <path d="M900 760 L884 430 L800 430 L800 760Z" />
            <rect x="740" y="470" width="120" height="70" fill="#6a3428" />
            <rect v-for="c in 5" :key="`gal${c}`" :x="748 + c * 20" y="482" width="10" height="46" fill="#ffcf8f" opacity="0.8" />
            <path d="M756 760 L756 640 Q800 590 844 640 L844 760Z" fill="#3d1d17" />
            <circle v-for="m in 5" :key="`tm${m}`" :cx="704 + m * 32" cy="430" r="12" />
          </g>
          <path d="M0 900 L0 760 L1600 760 L1600 900Z" fill="#5a2a22" />
          <path d="M620 900 L740 760 L860 760 L980 900Z" fill="#6e3a2c" />
        </template>

        <!-- 3. Yulduzli tun: Buxoro gumbazlari va minoralari silueti -->
        <template v-else-if="scene === 'night'">
          <circle v-for="s in stars" :key="s.id" :cx="s.x" :cy="s.y" :r="s.r" fill="#ffffff" class="sky-twinkle" :style="{ animationDelay: s.d, opacity: s.o }" />
          <path d="M1270 150 a64 64 0 1 0 54 100 a52 52 0 1 1 -54 -100Z" fill="#fff4cf" class="sky-moon" />
          <g fill="#0a1d4f">
            <path :d="skyline" />
          </g>
          <g fill="#ffcf7a" opacity="0.8">
            <rect v-for="w in windows" :key="`${w.x}-${w.y}`" :x="w.x" :y="w.y" width="8" height="14" rx="4" class="sky-twinkle" :style="{ animationDelay: w.d }" />
          </g>
          <path d="M0 900 L0 820 L1600 820 L1600 900Z" fill="#06123a" />
        </template>

        <!-- 4. Tong: Chor Minor va Labi Hovuz -->
        <template v-else>
          <ellipse v-for="c in dawnClouds" :key="c.x" :cx="c.x" :cy="c.y" :rx="c.rx" :ry="c.ry" :fill="`url(#cloud-${scene})`" class="sky-drift" :style="{ animationDelay: c.d }" />
          <path :d="dunes.far" fill="#d9a77e" opacity="0.7" />
          <g>
            <rect x="620" y="440" width="360" height="200" fill="#d29a64" />
            <path d="M740 640 L740 520 Q800 470 860 520 L860 640Z" fill="#7a4a2c" />
            <path d="M752 640 L752 528 Q800 488 848 528 L848 640Z" fill="#1aa6b7" opacity="0.35" />
            <path d="M740 440 Q740 380 800 370 Q860 380 860 440Z" fill="#c58c55" />
            <template v-for="m in chorMinor" :key="m">
              <rect :x="m - 30" y="330" width="60" height="310" fill="#c58c55" />
              <rect :x="m - 30" y="330" width="60" height="12" fill="#1aa6b7" />
              <rect :x="m - 30" y="380" width="60" height="6" fill="#1aa6b7" opacity="0.8" />
              <path :d="`M${m - 34} 332 Q${m - 34} 270 ${m} 262 Q${m + 34} 270 ${m + 34} 332Z`" :fill="`url(#dome-${scene})`" />
              <circle :cx="m" cy="256" r="6" fill="#f2c14e" />
            </template>
          </g>
          <g fill="#2f5a3a">
            <ellipse cx="420" cy="590" rx="90" ry="60" />
            <ellipse cx="1190" cy="585" rx="100" ry="64" />
            <rect x="414" y="600" width="12" height="60" fill="#5b3a22" />
            <rect x="1184" y="600" width="12" height="60" fill="#5b3a22" />
          </g>
          <rect y="640" width="1600" height="30" fill="#c99560" />
          <rect y="668" width="1600" height="232" :fill="`url(#water-${scene})`" />
          <g class="sky-shimmer">
            <rect v-for="r in reflections" :key="r.y" :x="800 - r.w / 2" :y="r.y" :width="r.w" height="4" rx="2" fill="#ffe7b8" :opacity="r.o" />
          </g>
          <g opacity="0.25" transform="translate(0 1310) scale(1 -1)">
            <rect x="620" y="440" width="360" height="200" fill="#d29a64" />
            <rect v-for="m in chorMinor" :key="`rf${m}`" :x="m - 30" y="330" width="60" height="310" fill="#c58c55" />
          </g>
        </template>
      </g>
    </svg>
    <div v-if="still" class="sky-veil"></div>
  </div>
</template>

<script setup>
// To'liq ekranli Buxoro manzaralari: sekin kattalashadi va bir-biriga o'tadi.
// Bosh sahifada haqiqiy Buxoro fotosuratlari (Ken Burns effekti bilan),
// test sahifasida esa tinch SVG tungi manzara (diqqatni chalg'itmaydi).
import { computed } from 'vue'
import { useSceneClock } from '../composables/useSceneClock'

const props = defineProps({
  // still: test sahifasi uchun bitta tinch manzara, almashmaydi.
  still: { type: Boolean, default: false },
  scene: { type: String, default: 'kalon' },
})

const order = ['kalon', 'ark', 'night', 'lyabi']
const base = import.meta.env.BASE_URL || '/'
// Fotosuratlar: Wikimedia Commons (mualliflar BUXORO_SERTIFIKAT.md faylida).
const photos = [
  { src: `${base}images/buxoro/kalon_minaret.jpg`, pos: '30% 40%', pan: 'left' },
  { src: `${base}images/buxoro/poi_kalon.jpg`, pos: '50% 35%', pan: 'right' },
  { src: `${base}images/buxoro/chor_minor.jpg`, pos: '50% 30%', pan: 'up' },
]
const shownScenes = computed(() => (props.still ? [props.scene] : order))
const { sceneIndex } = useSceneClock({ run: !props.still })
const activeIndex = computed(() => (props.still ? 0 : sceneIndex.value))

const look = {
  kalon: {
    sky: [[0, '#1767c9'], [0.45, '#4fa3e6'], [0.75, '#a9d8f2'], [1, '#f3e2bd']],
    sun: ['#ffffff', '#fff1c4'], sunAt: [1340, 130, 340], cloud: '#ffffff',
    sand: ['#e9c58f', '#c99560'], dome: ['#0b6f86', '#22c3d0', '#0a5c70'], girih: 0.05,
  },
  ark: {
    sky: [[0, '#2a2a7a'], [0.38, '#8a4fa0'], [0.62, '#f07f5a'], [0.82, '#ffc27a'], [1, '#ffe2a8']],
    sun: ['#fff1c9', '#ff9a5a'], sunAt: [800, 560, 330], cloud: '#ffc79e',
    sand: ['#b9735a', '#5a2a22'], dome: ['#0b6f86', '#22c3d0', '#0a5c70'], girih: 0.04,
  },
  night: {
    sky: [[0, '#030b2e'], [0.55, '#0a2272'], [0.85, '#14408f'], [1, '#1e5aa8']],
    sun: ['#fff6d8', '#8fb0ff'], sunAt: [1290, 200, 170], cloud: '#3b5bd0',
    sand: ['#0a1d4f', '#06123a'], dome: ['#0a1d4f', '#0a1d4f', '#0a1d4f'], girih: 0.035,
  },
  lyabi: {
    sky: [[0, '#16408f'], [0.5, '#4f86d8'], [0.78, '#a6c4ef'], [0.92, '#ffc79a'], [1, '#ffe0bd']],
    sun: ['#fff0d0', '#ffa86a'], sunAt: [300, 520, 260], cloud: '#ffd7b8',
    sand: ['#d9a77e', '#b97f50'], dome: ['#0b6f86', '#22c3d0', '#0a5c70'], girih: 0.05,
  },
}

// Qum tepaliklari: yumshoq to'lqinlar.
function dune({ base, amp, seed, bottom = 900, step = 16 }) {
  let d = `M0 ${bottom}`
  for (let x = 0; x <= 1600; x += step) {
    const v = Math.sin(x * 0.004 + seed) * 0.6 + Math.sin(x * 0.011 + seed * 2.3) * 0.4
    d += ` L${x} ${(base - amp * v).toFixed(1)}`
  }
  return `${d} L1600 ${bottom}Z`
}

const dunes = {
  far: dune({ base: 640, amp: 26, seed: 0.8 }),
  near: dune({ base: 790, amp: 30, seed: 2.4 }),
}

// Tungi shahar silueti: gumbazlar, minoralar va peshtoqlar.
function buildSkyline() {
  let d = 'M0 900 L0 760'
  const parts = [
    ['wall', 0, 120, 720], ['dome', 120, 220, 720, 70], ['wall', 220, 300, 700], ['minaret', 300, 330, 420],
    ['wall', 330, 470, 690], ['portal', 470, 590, 600], ['dome', 590, 740, 690, 95], ['wall', 740, 820, 700],
    ['minaret', 820, 870, 300], ['wall', 870, 980, 680], ['dome', 980, 1060, 680, 50], ['dome', 1060, 1140, 680, 50],
    ['wall', 1140, 1230, 700], ['portal', 1230, 1340, 620], ['minaret', 1340, 1366, 470], ['wall', 1366, 1480, 720],
    ['dome', 1480, 1600, 730, 75],
  ]
  for (const [kind, a, b, y, h] of parts) {
    if (kind === 'wall') d += ` L${a} ${y} L${b} ${y}`
    if (kind === 'dome') {
      const mid = (a + b) / 2
      d += ` L${a} ${y} Q${a} ${y - h} ${mid} ${y - h - 18} Q${b} ${y - h} ${b} ${y}`
    }
    if (kind === 'minaret') d += ` L${a} 760 L${a + 3} ${y} L${a - 4} ${y} L${a - 4} ${y - 22} L${(a + b) / 2} ${y - 40} L${b + 4} ${y - 22} L${b + 4} ${y} L${b - 3} ${y} L${b} 760`
    if (kind === 'portal') d += ` L${a} ${y} L${b} ${y}`
  }
  return `${d} L1600 760 L1600 900Z`
}
const skyline = buildSkyline()
const windows = [
  { x: 150, y: 735, d: '0s' }, { x: 520, y: 640, d: '-1s' }, { x: 545, y: 640, d: '-2s' }, { x: 650, y: 700, d: '-0.5s' },
  { x: 1010, y: 700, d: '-1.6s' }, { x: 1270, y: 660, d: '-2.4s' }, { x: 1295, y: 660, d: '-0.8s' }, { x: 1520, y: 745, d: '-1.2s' },
]

const kalonBands = Array.from({ length: 12 }, (_, i) => 290 + i * 38)
const arkMerlons = [...Array.from({ length: 16 }, (_, i) => 232 + i * 30), ...Array.from({ length: 17 }, (_, i) => 912 + i * 30)]
const chorMinor = [650, 950]
const poplars = [60, 110, 860, 900, 1180, 1240, 1500, 1550]

const dayClouds = [
  { x: 260, y: 180, rx: 260, ry: 44, d: '0s' },
  { x: 820, y: 120, rx: 320, ry: 40, d: '-8s' },
  { x: 1400, y: 280, rx: 240, ry: 36, d: '-4s' },
]
const eveningClouds = [
  { x: 300, y: 200, rx: 280, ry: 30, d: '0s' },
  { x: 1000, y: 140, rx: 340, ry: 28, d: '-8s' },
  { x: 1450, y: 260, rx: 220, ry: 26, d: '-4s' },
]
const dawnClouds = [
  { x: 420, y: 200, rx: 300, ry: 36, d: '-2s' },
  { x: 1250, y: 150, rx: 360, ry: 40, d: '-10s' },
]
const birds = [
  { x: 1120, y: 260, d: '0s' },
  { x: 1170, y: 300, d: '-1.2s' },
  { x: 1220, y: 250, d: '-0.6s' },
]
const reflections = Array.from({ length: 10 }, (_, i) => ({
  y: 690 + i * 20,
  w: 240 - i * 14 + (i % 3) * 30,
  o: 0.7 - i * 0.05,
}))
const stars = Array.from({ length: 90 }, (_, i) => ({
  id: i,
  x: (i * 173) % 1600,
  y: (i * 97) % 560,
  r: i % 9 === 0 ? 2.2 : i % 3 === 0 ? 1.5 : 1,
  o: 0.45 + (i % 5) * 0.12,
  d: `${-(i % 7) * 0.7}s`,
}))
</script>

<style scoped>
.sky-scenes {
  position: fixed;
  inset: 0;
  z-index: -1;
  overflow: hidden;
  pointer-events: none;
  background: #1767c9;
}

.is-photo {
  background: #0b2a4a;
}

.photo-scene {
  position: absolute;
  inset: 0;
  overflow: hidden;
  opacity: 0;
  transition: opacity 2s ease;
}

.photo-scene.active {
  opacity: 1;
}

.photo-image {
  position: absolute;
  inset: -4%;
  background-size: cover;
  background-repeat: no-repeat;
  transform: scale(1.04);
  will-change: transform;
}

.photo-scene.active .photo-image.pan-left { animation: pan-left 12s ease-out forwards; }
.photo-scene.active .photo-image.pan-right { animation: pan-right 12s ease-out forwards; }
.photo-scene.active .photo-image.pan-up { animation: pan-up 12s ease-out forwards; }

@keyframes pan-left {
  from { transform: scale(1.16) translate(2%, 1%); }
  to { transform: scale(1.04) translate(-1%, 0); }
}

@keyframes pan-right {
  from { transform: scale(1.04) translate(-2%, 0); }
  to { transform: scale(1.15) translate(1.5%, -1%); }
}

@keyframes pan-up {
  from { transform: scale(1.14) translate(0, 2%); }
  to { transform: scale(1.04) translate(0, -1%); }
}

/* Quyosh nuri jilosi rasm ustida sekin suzadi. */
.photo-light {
  position: absolute;
  inset: -20%;
  background: radial-gradient(40% 35% at 75% 15%, rgba(255, 226, 160, 0.32), transparent 70%);
  mix-blend-mode: soft-light;
  animation: photo-light 18s ease-in-out infinite alternate;
}

@keyframes photo-light {
  from { transform: translate(-6%, 0); }
  to { transform: translate(6%, 4%); }
}

/* Matn o'qilishi uchun pastki va chekka qorong'ilashuv. */
.photo-shade {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(4, 18, 48, 0.35) 0%, rgba(4, 18, 48, 0.08) 35%, rgba(4, 18, 48, 0.25) 65%, rgba(4, 18, 48, 0.72) 100%),
    radial-gradient(120% 90% at 50% 45%, transparent 45%, rgba(3, 12, 48, 0.45) 100%);
}

.sky-scene {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  transition: opacity 1.8s ease;
}

.sky-scene.active,
.is-still .sky-scene {
  opacity: 1;
}

.sky-zoom {
  transform-origin: 50% 60%;
  transform: scale(1.12);
  transition: transform 9s cubic-bezier(0.2, 0.6, 0.3, 1);
}

.sky-scene.active .sky-zoom {
  transform: scale(1);
}

.is-still .sky-zoom {
  transform: scale(1.02);
  transition: none;
}

.sky-drift {
  animation: sky-drift 26s ease-in-out infinite alternate;
}

.sky-twinkle {
  animation: sky-twinkle 3.4s ease-in-out infinite;
}

.sky-shimmer {
  animation: sky-shimmer 4s ease-in-out infinite;
}

.sky-moon {
  filter: drop-shadow(0 0 24px rgba(255, 236, 180, 0.7));
}

.sky-birds path {
  animation: sky-bird 14s linear infinite;
}

.sky-veil {
  position: absolute;
  inset: 0;
  background: radial-gradient(120% 80% at 50% 45%, transparent 40%, rgba(3, 12, 48, 0.35) 100%);
}

@keyframes sky-drift {
  from { transform: translateX(-40px); }
  to { transform: translateX(40px); }
}

@keyframes sky-twinkle {
  0%, 100% { opacity: 0.25; }
  50% { opacity: 1; }
}

@keyframes sky-shimmer {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes sky-bird {
  0% { transform: translate(0, 0); }
  50% { transform: translate(-260px, -30px); }
  100% { transform: translate(-520px, 0); }
}

@media (prefers-reduced-motion: reduce) {
  .photo-scene.active .photo-image,
  .photo-light {
    animation: none;
  }

  .sky-scene,
  .sky-zoom {
    transition: none;
  }

  .sky-drift,
  .sky-twinkle,
  .sky-shimmer,
  .sky-birds path {
    animation: none;
  }
}
</style>
