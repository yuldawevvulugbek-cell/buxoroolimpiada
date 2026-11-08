// Buxoro Respublika olimpiadasi sertifikati: bitta SVG, ekranda ko'rsatiladi, PNG qilib yuklanadi va chop etiladi.
// Chap tomonda Kalon minorasi fotosurati ravoq (arka) shaklida, o'ngda matn, pastda oltin muhr.
// Fotosurat data URL qilib SVG ichiga joylanadi: PNG ga aylantirganda ham, chop etganda ham rasm chiqadi.
// Shriftlar tizimdagilar (Georgia, Arial), tashqi shrift yuklanmaydi.

const W = 1600
const H = 1131
const PHOTO_URL = `${import.meta.env.BASE_URL || '/'}images/buxoro/sertifikat_kalon.jpg`

let photoData = ''
let photoPromise = null

// Fotosuratni bir marta yuklab, data URL ko'rinishida saqlab qo'yadi.
export function loadCertificateAssets() {
  if (photoData) return Promise.resolve(photoData)
  if (!photoPromise) {
    photoPromise = fetch(PHOTO_URL)
      .then(res => {
        if (!res.ok) throw new Error('Rasm topilmadi')
        return res.blob()
      })
      .then(blob => new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result)
        reader.onerror = reject
        reader.readAsDataURL(blob)
      }))
      .then(data => {
        photoData = String(data)
        return photoData
      })
      .catch(() => {
        photoPromise = null
        return ''
      })
  }
  return photoPromise
}

function esc(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function formatDate(value) {
  const date = value ? new Date(value) : new Date()
  if (Number.isNaN(date.getTime())) return ''
  const pad = n => String(n).padStart(2, '0')
  return `${pad(date.getDate())}.${pad(date.getMonth() + 1)}.${date.getFullYear()}`
}

function formatPercent(value) {
  const number = Number(value || 0)
  return Number.isInteger(number) ? String(number) : number.toFixed(1)
}

// Ism ramkadan chiqib ketmasligi uchun: avval brauzerning o'zida shu shrift bilan
// haqiqiy kenglik o'lchanadi (canvas), bo'lmasa harflar bo'yicha taxmin qilinadi.
// Juda uzun ism eng kichik o'lchamda ham sig'masa, textLength bilan siqiladi.
const NAME_MAX_WIDTH = 760
const NAME_MAX_SIZE = 86
const NAME_MIN_SIZE = 30
const NAME_FONT = "Georgia, 'Times New Roman', serif"

function nameEm(name) {
  let em = 0
  for (const ch of String(name || '')) {
    if (ch === ' ') em += 0.3
    else if (/[A-ZА-ЯЁЎҚҒҲ]/.test(ch)) em += 0.78
    else if (/[a-zа-яёўқғҳ]/.test(ch)) em += 0.56
    else em += 0.45
  }
  return Math.max(em, 1)
}

let measureCtx = null
function measureName(name, size) {
  try {
    if (typeof document === 'undefined') return null
    if (!measureCtx) measureCtx = document.createElement('canvas').getContext('2d')
    if (!measureCtx) return null
    measureCtx.font = `italic 700 ${size}px ${NAME_FONT}`
    const width = measureCtx.measureText(String(name || '')).width
    return width > 0 ? width : null
  } catch {
    return null
  }
}

function nameLayout(name) {
  const measured = measureName(name, 100)
  // 6% zaxira: SVG va canvas shriftni sal boshqacha chizishi mumkin
  const perPx = measured ? (measured * 1.06) / 100 : nameEm(name)
  const size = Math.max(NAME_MIN_SIZE, Math.min(NAME_MAX_SIZE, Math.floor(NAME_MAX_WIDTH / perPx)))
  const width = perPx * size
  return { size, squeeze: width > NAME_MAX_WIDTH }
}

function fitSize(text, base, maxWidth, ratio = 0.6) {
  const len = String(text || '').length || 1
  return Math.min(base, Math.floor(maxWidth / (len * ratio)))
}

// Sakkiz qirrali yulduz (Buxoro koshinlari naqshi).
function star(cx, cy, r, fill, inner = 0.55, points = 8) {
  const pts = []
  for (let i = 0; i < points * 2; i += 1) {
    const rad = (Math.PI / points) * i - Math.PI / 2
    const rr = i % 2 === 0 ? r : r * inner
    pts.push(`${(cx + rr * Math.cos(rad)).toFixed(1)},${(cy + rr * Math.sin(rad)).toFixed(1)}`)
  }
  return `<polygon points="${pts.join(' ')}" fill="${fill}"/>`
}

// Uchli (Sharq uslubidagi) ravoq: pastda to'g'ri to'rtburchak, tepada o'tkir gumbaz.
function archPath(x, y, w, h) {
  const r = w / 2
  const cx = x + r
  const shoulder = y + r * 0.95
  return `M${x} ${y + h} L${x} ${shoulder} C${x} ${y + r * 0.35} ${cx - r * 0.45} ${y + r * 0.1} ${cx} ${y} C${cx + r * 0.45} ${y + r * 0.1} ${x + w} ${y + r * 0.35} ${x + w} ${shoulder} L${x + w} ${y + h} Z`
}

// Burchak bezagi: oltin yulduz, ichida firuza yulduz va ikki chiziq.
function corner(x, y, sx, sy) {
  return `<g transform="translate(${x} ${y}) scale(${sx} ${sy})">
    <path d="M0 0 L120 0 M0 0 L0 120" stroke="#d9b45a" stroke-width="3"/>
    <path d="M14 14 L84 14 M14 14 L14 84" stroke="#d9b45a" stroke-width="1.5"/>
    ${star(30, 30, 26, '#d9b45a')}${star(30, 30, 13, '#0f7d8f')}
  </g>`
}

function seal(cx, cy, percent) {
  const rays = star(0, 0, 96, 'url(#goldSeal)', 0.86, 24)
  const center = percent === null
    ? `${star(0, -6, 30, '#0f3557', 0.5)}<text y="44" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="700" letter-spacing="3" fill="#0f3557">BUXORO</text>`
    : `<text y="4" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="46" font-weight="700" fill="#0f3557">${formatPercent(percent)}%</text>
       <text y="36" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700" letter-spacing="3" fill="#0f3557">NATIJA</text>`
  return `<g transform="translate(${cx} ${cy}) scale(0.84)">
    <path d="M-50 60 L-78 168 L-52 150 L-36 178 L-14 70Z" fill="#0f7d8f"/>
    <path d="M50 60 L78 168 L52 150 L36 178 L14 70Z" fill="#0b5b6a"/>
    <g filter="url(#shadow)">${rays}</g>
    <circle r="74" fill="url(#goldSeal)" stroke="#8a6a16" stroke-width="2"/>
    <circle r="64" fill="none" stroke="#fff2c2" stroke-width="2" stroke-dasharray="3 5"/>
    <circle r="56" fill="#f7e6ad"/>
    ${center}
  </g>`
}

export function certificateSvg(cert, photo = photoData) {
  const name = esc(cert.full_name)
  const subject = esc(cert.subject_name)
  const level = esc(cert.level_name)
  const hasPercent = cert.percent !== null && cert.percent !== undefined
  const percent = hasPercent ? cert.percent : null

  const cx = 1080 // matn ustunining markazi
  const lineReason = hasPercent
    ? `<tspan font-weight="700" fill="#0f7d8f">${formatPercent(percent)}%</tspan> natija ko‘rsatgani uchun taqdirlanadi.`
    : 'muvaffaqiyatli qatnashgani uchun taqdirlanadi.'

  const archX = 112
  const archY = 150
  const archW = 470
  const archH = 830
  const arch = archPath(archX, archY, archW, archH)
  const archOuter = archPath(archX - 16, archY - 22, archW + 32, archH + 22)

  const photoLayer = photo
    ? `<image href="${photo}" x="${archX}" y="${archY}" width="${archW}" height="${archH}" preserveAspectRatio="xMidYMid slice" clip-path="url(#archClip)"/>`
    : `<path d="${arch}" fill="url(#skyFallback)"/>`

  const nameFit = nameLayout(cert.full_name)
  const subjSize = fitSize(cert.subject_name, 32, 330, 0.62)
  const levelSize = fitSize(cert.level_name, 32, 330, 0.62)

  return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">
  <defs>
    <linearGradient id="paper" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#fffdf6"/>
      <stop offset="0.55" stop-color="#fbf3e1"/>
      <stop offset="1" stop-color="#f1e2c2"/>
    </linearGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#9c7613"/>
      <stop offset="0.25" stop-color="#e9cd72"/>
      <stop offset="0.5" stop-color="#b8901f"/>
      <stop offset="0.75" stop-color="#f1d98a"/>
      <stop offset="1" stop-color="#9c7613"/>
    </linearGradient>
    <linearGradient id="goldV" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f3dc8e"/>
      <stop offset="0.5" stop-color="#c49a2a"/>
      <stop offset="1" stop-color="#8f6b10"/>
    </linearGradient>
    <radialGradient id="goldSeal" cx="0.4" cy="0.35" r="0.75">
      <stop offset="0" stop-color="#fff0b8"/>
      <stop offset="0.45" stop-color="#e2bf55"/>
      <stop offset="1" stop-color="#9a7414"/>
    </radialGradient>
    <linearGradient id="navy" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0f3557"/>
      <stop offset="1" stop-color="#07203a"/>
    </linearGradient>
    <linearGradient id="archFade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0.6" stop-color="#07203a" stop-opacity="0"/>
      <stop offset="1" stop-color="#07203a" stop-opacity="0.85"/>
    </linearGradient>
    <linearGradient id="skyFallback" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2d7fd0"/>
      <stop offset="1" stop-color="#e9c58f"/>
    </linearGradient>
    <pattern id="tiles" width="36" height="36" patternUnits="userSpaceOnUse">
      <rect width="36" height="36" fill="#0f3557"/>
      <path d="M18 3 L22 14 L33 18 L22 22 L18 33 L14 22 L3 18 L14 14Z" fill="#14a3b5"/>
      <circle cx="18" cy="18" r="3.2" fill="#e9cd72"/>
      <circle cx="0" cy="0" r="3" fill="#e9cd72"/><circle cx="36" cy="0" r="3" fill="#e9cd72"/>
      <circle cx="0" cy="36" r="3" fill="#e9cd72"/><circle cx="36" cy="36" r="3" fill="#e9cd72"/>
    </pattern>
    <pattern id="girih" width="80" height="80" patternUnits="userSpaceOnUse">
      <path d="M40 8 L48 32 L72 40 L48 48 L40 72 L32 48 L8 40 L32 32Z M40 22 L58 40 L40 58 L22 40Z" fill="none" stroke="#0f7d8f" stroke-width="1"/>
    </pattern>
    <clipPath id="archClip"><path d="${arch}"/></clipPath>
    <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="#3a2a05" flood-opacity="0.35"/>
    </filter>
  </defs>

  <rect width="${W}" height="${H}" fill="url(#navy)"/>
  <rect x="16" y="16" width="${W - 32}" height="${H - 32}" fill="url(#tiles)"/>
  <rect x="52" y="52" width="${W - 104}" height="${H - 104}" fill="url(#paper)"/>
  <rect x="52" y="52" width="${W - 104}" height="${H - 104}" fill="url(#girih)" opacity="0.07"/>
  <rect x="52" y="52" width="${W - 104}" height="${H - 104}" fill="none" stroke="url(#gold)" stroke-width="6"/>
  <rect x="70" y="70" width="${W - 140}" height="${H - 140}" fill="none" stroke="#c9a23d" stroke-width="1.5"/>
  ${corner(80, 80, 1, 1)}${corner(W - 80, 80, -1, 1)}${corner(80, H - 80, 1, -1)}${corner(W - 80, H - 80, -1, -1)}

  <g opacity="0.06">${star(cx, 560, 330, '#0f7d8f', 0.62)}</g>

  <path d="${archOuter}" fill="url(#navy)" filter="url(#shadow)"/>
  <path d="${archOuter}" fill="none" stroke="url(#goldV)" stroke-width="5"/>
  ${photoLayer}
  <path d="${arch}" fill="url(#archFade)"/>
  <path d="${arch}" fill="none" stroke="#f1d98a" stroke-width="3"/>
  <path d="${archPath(archX + 14, archY + 18, archW - 28, archH - 32)}" fill="none" stroke="#fff4cf" stroke-width="1.2" stroke-opacity="0.7"/>
  ${star(archX + archW / 2, archY - 2, 18, '#e9cd72')}${star(archX + archW / 2, archY - 2, 8, '#0f7d8f')}
  <text x="${archX + archW / 2}" y="${archY + archH - 62}" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="30" font-style="italic" fill="#fff6dc">Kalon minorasi</text>
  <text x="${archX + archW / 2}" y="${archY + archH - 28}" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16" letter-spacing="5" fill="#e9cd72">BUXORO · 1127</text>

  <g transform="translate(${cx} 160)">
    <path d="M-250 0 L-60 0" stroke="url(#gold)" stroke-width="2"/>
    <path d="M60 0 L250 0" stroke="url(#gold)" stroke-width="2"/>
    ${star(0, 0, 20, '#c9a23d')}${star(0, 0, 9, '#0f7d8f')}
    ${star(-40, 0, 7, '#0f7d8f')}${star(40, 0, 7, '#0f7d8f')}
  </g>
  <text x="${cx}" y="226" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="23" letter-spacing="5" fill="#0f7d8f" font-weight="700">BUXORO 2026 RESPUBLIKA OCHIQ OLIMPIADASI</text>
  <text x="${cx}" y="346" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="104" letter-spacing="12" fill="url(#gold)" font-weight="700" stroke="#8a6a16" stroke-width="0.8">SERTIFIKAT</text>
  <g transform="translate(${cx} 384)">
    <path d="M-200 0 Q-100 -14 0 0 Q100 14 200 0" fill="none" stroke="#c9a23d" stroke-width="2"/>
    <circle r="5" fill="#0f7d8f"/>
  </g>
  <text x="${cx}" y="446" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="30" font-style="italic" fill="#6b5634">Ushbu sertifikat faxr bilan topshiriladi</text>
  <text x="${cx}" y="${540 + (NAME_MAX_SIZE - nameFit.size) / 3}" text-anchor="middle" font-family="${NAME_FONT}" font-size="${nameFit.size}" fill="#0f3557" font-weight="700" font-style="italic"${nameFit.squeeze ? ` textLength="${NAME_MAX_WIDTH}" lengthAdjust="spacingAndGlyphs"` : ''}>${name}</text>
  <rect x="${cx - 360}" y="572" width="720" height="3" fill="url(#gold)"/>
  ${star(cx - 372, 573.5, 8, '#c9a23d')}${star(cx + 372, 573.5, 8, '#c9a23d')}

  <text x="${cx}" y="636" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="27" fill="#3d3424">Buxoro 2026 Respublika ochiq olimpiadasida ishtirok etib,</text>
  <text x="${cx}" y="680" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="27" fill="#3d3424">${lineReason}</text>

  <g transform="translate(${cx - 395} 718)">
    <rect width="380" height="96" rx="14" fill="#ffffff" fill-opacity="0.75" stroke="#c9a23d" stroke-width="1.5"/>
    <rect x="0" y="0" width="8" height="96" rx="4" fill="#0f7d8f"/>
    <text x="190" y="34" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16" letter-spacing="5" font-weight="700" fill="#0f7d8f">FAN</text>
    <text x="190" y="74" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="${subjSize}" font-weight="700" fill="#0f3557">${subject}</text>
  </g>
  <g transform="translate(${cx + 15} 718)">
    <rect width="380" height="96" rx="14" fill="#ffffff" fill-opacity="0.75" stroke="#c9a23d" stroke-width="1.5"/>
    <rect x="0" y="0" width="8" height="96" rx="4" fill="#0f7d8f"/>
    <text x="190" y="34" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="16" letter-spacing="5" font-weight="700" fill="#0f7d8f">DARAJA</text>
    <text x="190" y="74" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="${levelSize}" font-weight="700" fill="#0f3557">${level}</text>
  </g>

  <g font-family="Arial, Helvetica, sans-serif" fill="#5b4a2e">
    <text x="${cx - 290}" y="922" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="30" font-weight="700" fill="#0f3557">${esc(formatDate(cert.issued_at))}</text>
    <rect x="${cx - 400}" y="938" width="220" height="2" fill="#8a7650"/>
    <text x="${cx - 290}" y="970" text-anchor="middle" font-size="20" letter-spacing="3">SANA</text>

    <g fill="none" stroke="#1d3f8f" stroke-linecap="round" stroke-linejoin="round">
      <path d="M${cx + 166} 920 c6 -30 14 -54 27 -58 c11 -3 6 21 -6 45 c-8 16 -10 29 -2 25 c10 -5 18 -27 27 -25 c6 2 -2 19 4 19 c8 0 14 -17 23 -17 c6 0 2 15 8 15 c10 0 16 -21 27 -21 c8 0 4 17 12 17 c13 0 23 -15 36 -22" stroke-width="2.6"/>
      <path d="M${cx + 174} 892 c15 -4 32 -5 47 -2" stroke-width="2.2"/>
      <path d="M${cx + 156} 930 c52 -11 124 -13 196 -6 c10 1 16 -5 9 -9" stroke-width="1.8" stroke-opacity="0.85"/>
    </g>
    <rect x="${cx + 120}" y="938" width="260" height="2" fill="#8a7650"/>
    <text x="${cx + 250}" y="966" text-anchor="middle" font-size="15" letter-spacing="2">TASHKILIY QO‘MITA RAHBARI</text>
    <text x="${cx + 250}" y="1000" text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-size="24" font-weight="700" font-style="italic" fill="#0f3557">Abdurahmanova Farida</text>

    <text x="${cx - 290}" y="1008" text-anchor="middle" font-size="18" letter-spacing="2" fill="#8a7650">№ ${esc(cert.number)}</text>
  </g>
  ${seal(cx, 915, percent)}
</svg>`
}

function fileName(cert) {
  const safe = String(cert.full_name || 'sertifikat').replace(/[^\p{L}\p{N}]+/gu, '_').replace(/^_|_$/g, '')
  return `Sertifikat_${safe || 'oquvchi'}.png`
}

export async function downloadCertificatePng(cert) {
  const photo = await loadCertificateAssets()
  return new Promise((resolve, reject) => {
    const svg = certificateSvg(cert, photo)
    const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml;charset=utf-8' }))
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      canvas.width = W
      canvas.height = H
      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, W, H)
      URL.revokeObjectURL(url)
      canvas.toBlob(blob => {
        if (!blob) return reject(new Error('PNG yaratilmadi'))
        const link = document.createElement('a')
        link.href = URL.createObjectURL(blob)
        link.download = fileName(cert)
        document.body.appendChild(link)
        link.click()
        link.remove()
        setTimeout(() => URL.revokeObjectURL(link.href), 2000)
        resolve()
      }, 'image/png')
    }
    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error('Sertifikat rasmi yaratilmadi'))
    }
    img.src = url
  })
}

export function printCertificate(cert) {
  const win = window.open('', '_blank')
  if (!win) return false
  win.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>Sertifikat</title>
<style>@page{size:A4 landscape;margin:0}html,body{margin:0;background:#fff}svg{width:100vw;height:auto;display:block}</style>
</head><body>${certificateSvg(cert)}<script>window.onload=function(){setTimeout(function(){window.print()},300)}<\/script></body></html>`)
  win.document.close()
  return true
}
