# Ro‘yxatdan o‘tish va natijani yashirish

Qilingan o‘zgarishlar:

- O‘quvchi kirish sahifasida code bo‘limi olib tashlandi. Faqat `Register` tugmasi qoldi.
- Tugma bosilganda modal oyna ochiladi: ism familiya, yosh, 2 ta telefon raqam, fan va daraja (select).
- Ro‘yxatdan o‘tgach test shu fan va daraja bo‘yicha darhol boshlanadi. Code ichkarida ishlatiladi, o‘quvchiga ko‘rsatilmaydi.
- O‘quv markaz so‘ralmaydi: o‘zi ro‘yxatdan o‘tganlar `Online ro‘yxatdan o‘tganlar` markaziga yoziladi.
- Admin paneldagi `Natijalar` sahifasida `Test natijasini yashirish` tugmasi bor (faqat bosh admin o‘zgartiradi):
  - Yoqiq: o‘quvchi test tugagach natijasini ko‘rmaydi.
  - O‘chiq: o‘quvchi nechta to‘g‘ri topgani va necha foiz olganini ko‘radi.
- Natijalar, Yaratilgan o‘quvchilar sahifalari va Excel fayllarida yosh va telefon raqamlar chiqadi.

Backend o‘zgarishlari: `Student.phone`, `Student.phone2`, `SiteSettings` modeli, migratsiya `0038`, yangi API `GET/PATCH /api/settings/`.

Deploy qilgandan keyin migratsiya ishlashi kerak (`python manage.py migrate`).
