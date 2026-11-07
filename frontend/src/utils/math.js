import katex from 'katex'

const cache = new Map()

function escapeHtml(text) {
  return text.replace(/[&<>"']/g, (ch) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]))
}

// Savol matnini HTML qiladi: \( ... \) ichidagi formulalar Word'dagidek (kasr, daraja, ildiz) chiziladi,
// qolgan matn xavfsiz ko'rinishda chiqadi, qator ko'chishlari saqlanadi.
export function mathHtml(text) {
  const value = String(text ?? '')
  if (cache.has(value)) return cache.get(value)
  const html = value
    .split(/(\\\([\s\S]*?\\\))/)
    .map((part) => {
      if (part.startsWith('\\(') && part.endsWith('\\)')) {
        try {
          return katex.renderToString('\\displaystyle ' + part.slice(2, -2), { throwOnError: false, strict: 'ignore' })
        } catch {
          return escapeHtml(part)
        }
      }
      // Qator boshidagi bo'shliqlar saqlanadi: kod savollaridagi (Python) chekinishlar ko'rinsin.
      return escapeHtml(part)
        .replace(/(^|\n)( +)/g, (_, nl, spaces) => nl + '&nbsp;'.repeat(spaces.length))
        .replace(/\n/g, '<br>')
    })
    .join('')
  cache.set(value, html)
  return html
}
