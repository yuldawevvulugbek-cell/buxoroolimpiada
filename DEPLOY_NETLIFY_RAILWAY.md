# Buxoro Respublika olimpiadasi: Railway + PostgreSQL + Netlify'ga joylash

Backend (`backend/`) Railway'da, baza PostgreSQL'da, frontend (`frontend/`) esa Netlify'da ishlaydi. Barcha sozlama fayllari tayyor va PostgreSQL bilan Railway rejimida sinab ko'rilgan: migratsiyalar, testlar, ro'yxatdan o'tish, test ishlash, sertifikat, admin panel va /sekret ishladi.

Ikki yo'l bor. **A yo'l (GitHub orqali)** qulayroq, chunki keyin har `git push` dan keyin sayt o'zi yangilanadi. **B yo'l (GitHub'siz)** tezroq: kompyuterdan to'g'ridan-to'g'ri yuklaysiz.

---

## 0. Tayyorlash

Zipni oching. Ichida `Antalya` papkasi bor: barcha buyruqlar shu papka ichida bajariladi.

### A yo'l: GitHub'ga yuklash

GitHub'da yangi bo'sh repo yarating (masalan `buxoro-olimpiada`), keyin:

```powershell
cd Antalya
git init
git add .
git commit -m "Buxoro olimpiadasi"
git branch -M main
git remote add origin https://github.com/SIZNING-LOGIN/buxoro-olimpiada.git
git push -u origin main
```

`.env`, `db.sqlite3`, `node_modules` va `dist` GitHub'ga yuklanmaydi (`.gitignore` ularni chiqarib tashlaydi).

### B yo'l: GitHub'siz

Railway CLI'ni o'rnating (Node.js kerak):

```powershell
npm.cmd i -g @railway/cli
railway login
```

---

## 1. Railway: backend

**A yo'l:** railway.app → **New Project** → **Deploy from GitHub repo** → reponi tanlang.

**B yo'l:** railway.app → **New Project** → **Empty Project**. Keyin kompyuterda `Antalya` papkasida:

```powershell
railway link      # yaratilgan loyihani tanlang
railway up        # kodni yuklaydi va deploy qiladi
```

Har o'zgarishdan keyin yana `railway up` qilasiz.

Ikkala yo'lda ham:

1. Xizmat sozlamalarida **Root Directory** bo'sh qolsin (papka ildizi). `railway.json`, `nixpacks.toml` va `start_railway.sh` hammasini o'zi qiladi: kutubxonalarni o'rnatadi, migratsiya qiladi, testlarni va admin akkauntini yaratadi, gunicorn'ni ishga tushiradi.
2. **Settings → Networking → Generate Domain** tugmasini bosing. Masalan `buxoro-olimpiada.up.railway.app` degan manzil chiqadi. Uni 4-qadamda ishlatasiz.

## 2. Railway: PostgreSQL

1. Shu loyihaning ichida **+ New → Database → Add PostgreSQL** ni tanlang.
2. Backend xizmati → **Variables** → **Add Variable Reference** → `DATABASE_URL` ni tanlang (`${{Postgres.DATABASE_URL}}`).
3. Shundan keyin har bir deploy ma'lumotlarni saqlab qoladi. SQLite'da esa har deployda hammasi o'chib ketardi.

## 3. Railway Variables (backend → Variables)

| O'zgaruvchi | Qiymat | Izoh |
|---|---|---|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | 2-qadamda qo'shilgan |
| `SECRET_KEY` | 50+ belgili tasodifiy matn | Majburiy. Masalan: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `ADMIN_PASSWORD` | o'zingizning parolingiz | `ulugbek` akkauntining paroli. Yozilmasa, eski parol ishlaydi |
| `SECRET_PANEL_PASSWORD` | o'zingizning parolingiz | /sekret sahifasining paroli. Yozilmasa standart `buxoro-sekret-2026` ishlaydi, albatta o'zgartiring |
| `CORS_ALLOWED_ORIGINS` | `https://SIZNING-SAYT.netlify.app` | Ixtiyoriy: `*.netlify.app` domenlariga ruxsat avtomatik beriladi. O'z domeningiz bo'lsa, shuni yozing |
| `CSRF_TRUSTED_ORIGINS` | yuqoridagi bilan bir xil | Ixtiyoriy |
| `WEB_CONCURRENCY` | `3` | Ixtiyoriy: jarayonlar soni |
| `GUNICORN_THREADS` | `8` | Ixtiyoriy: har bir jarayondagi oqimlar soni |

`DEBUG` ni yozish shart emas: Railway'da u avtomatik o'chiq bo'ladi. Railway har deploydan keyin `/api/health/` manzilini tekshiradi. Server javob bermasa, eski versiya ishlashda davom etadi.

Tekshirish: brauzerda `https://SIZNING-BACKEND.up.railway.app/api/health/` manzilini oching. `{"status": "ok"}` chiqishi kerak.

## 4. Netlify: frontend

### A yo'l (GitHub)

1. app.netlify.com → **Add new site → Import an existing project** → GitHub → reponi tanlang.
2. Build sozlamalari ildizdagi `netlify.toml` dan avtomatik olinadi (base `frontend`, `npm run build`, `dist`, Node 22). Hech narsani o'zgartirmang.
3. **Site configuration → Environment variables** bo'limiga qo'shing:
   - `VITE_API_BASE_URL` = `https://SIZNING-BACKEND.up.railway.app/api`
4. **Deploys → Trigger deploy** tugmasini bosing. O'zgaruvchi qo'shilgandan keyin bitta qayta build kerak.

### B yo'l (GitHub'siz, sudrab tashlash)

Kompyuterda frontendni Railway manzili bilan build qiling:

```powershell
cd Antalya\frontend
npm.cmd install
$env:VITE_API_BASE_URL="https://SIZNING-BACKEND.up.railway.app/api"
npm.cmd run build
```

Keyin app.netlify.com → **Sites** → **Add new site → Deploy manually** sahifasiga `frontend\dist` papkasini sudrab tashlang. Sahifa yangilanganda 404 chiqmasligi uchun `_redirects` fayli `dist` ichiga avtomatik tushadi.

Har o'zgarishdan keyin build qilib, sayt → **Deploys** sahifasiga yangi `dist` ni yana sudrab tashlaysiz.

Ikkala yo'lda ham manzil oxiridagi `/api` esdan chiqsa, frontend uni o'zi qo'shadi. Netlify'ning `*.netlify.app` domeni uchun CORS ruxsati backendda avtomatik bor.

## 5. Kompyuterdagi ma'lumotlarni PostgreSQL'ga ko'chirish (ixtiyoriy, bir marta)

Kompyuterdagi `backend/db.sqlite3` dagi o'quvchilar va natijalarni Railway Postgres'ga o'tkazish uchun:

1. Railway → Postgres → **Connect** → **Public Network** bo'limidan `DATABASE_PUBLIC_URL` ni nusxalang.
2. `backend/sqlite_to_postgres.bat` faylini ikki marta bosing va so'ralganda shu manzilni joylang.
3. Skript Postgres'dagi eski ma'lumotlarni o'chiradi va SQLite'dagilarni yozadi. Shuning uchun uni faqat birinchi marta ishlating.

## 6. Tekshirish ro'yxati

- [ ] `https://...railway.app/api/health/` manzili ok qaytaradi
- [ ] Netlify sayti ochiladi, "Ro'yxatdan o'tish" bosilganda fanlar ro'yxati chiqadi
- [ ] Admin panelga `ulugbek` va `ADMIN_PASSWORD` dagi parol bilan kirsa bo'ladi
- [ ] Bitta sinov o'quvchi bilan test ishlab, natija admin panelda ko'rinadi

## Muammo bo'lsa

| Belgi | Sababi va yechimi |
|---|---|
| Saytda "Network Error" chiqadi, fanlar yuklanmaydi | Netlify'da `VITE_API_BASE_URL` yozilmagan yoki noto'g'ri. Uni tuzatib, qayta deploy qiling |
| Brauzer konsolida CORS xatosi | Netlify'dan boshqa domen ishlatilyapti: Railway'da `CORS_ALLOWED_ORIGINS` ga o'sha domenni yozing |
| Railway'da `Bad Request (400)` | O'z domeningiz bor: `ALLOWED_HOSTS` ga `.railway.app,sizning-domen.uz` ni yozing |
| Word test yuklangandan keyin o'quvchilarda darhol ko'rinmaydi | Kesh sababli 1 daqiqagacha kechikish bo'lishi mumkin, bu normal |
| Har deploydan keyin o'quvchilar yo'qoladi | Postgres ulanmagan: 2-qadamni bajaring. Railway loglarida "DATABASE_URL topilmadi" degan ogohlantirish chiqadi |
