"""Word (.docx) fayldan test savollarini o'qish.

Tashqi kutubxona kerak emas: .docx bu zip arxiv, ichidagi word/document.xml o'qiladi.

Qo'llab-quvvatlanadigan ko'rinish (namuna faylda ham shunday):

    1. Savol matni
    A) variant
    B) variant
    C) variant
    D) variant
    Javob: B

To'g'ri javobni belgilashning boshqa yo'llari:
  * variant oldiga yoki oxiriga "*" qo'yish:  *B) variant
  * faqat to'g'ri variantni qalin (bold) qilish
  * fayl oxirida "Javoblar" sarlavhasi va ostida "1-A, 2-C, 3-B ..." ro'yxati
Variant harflari lotin (A-D) yoki kirill (А-Г) bo'lishi mumkin; Word'ning avtomatik
raqamlash/harflash ro'yxatlari ham tushuniladi.
"""
import re
import zipfile
from io import BytesIO
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
LETTERS = 'ABCD'
LETTER_MAP = {
    'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D',
    'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D',
    'А': 'A', 'Б': 'B', 'В': 'C', 'Г': 'D',
    'а': 'A', 'б': 'B', 'в': 'C', 'г': 'D',
}
LETTER_CHARS = ''.join(LETTER_MAP)

OPTION_RE = re.compile(rf'^\s*([*+]?)\s*([{LETTER_CHARS}])\s*[\)\.]\s*(.*?)\s*$')
INLINE_SPLIT_RE = re.compile(rf'(?:^|\s)([*+]?)([{LETTER_CHARS}])\)\s+')
ANSWER_RE = re.compile(
    rf"^\s*(?:to['‘’`]?g['‘’`]?ri\s+javob|javob|answer|correct|ответ|правильный\s+ответ)\s*[:\-–—=]\s*([{LETTER_CHARS}])\s*\)?\s*\.?\s*$",
    re.IGNORECASE,
)
KEY_HEADER_RE = re.compile(r'^\s*(javoblar|javob\s+kaliti|kalit|test\s+javoblari|answers?|answer\s+key|ответы|ключ(?:\s+к\s+тесту)?)\s*:?\s*$', re.IGNORECASE)
KEY_PAIR_RE = re.compile(rf'(\d+)\s*[\-–—.):=]?\s*([{LETTER_CHARS}])(?![\w])')
QUESTION_NUM_RE = re.compile(r'^\s*(\d{1,3})\s*(?:[.)]|-\s*savol\s*[.:)]?|\s*-\s+)\s*(.*)$', re.IGNORECASE)

LETTER_FORMATS = {'lowerLetter', 'upperLetter', 'russianLower', 'russianUpper'}


class WordImportError(Exception):
    pass


def _numbering_formats(zf):
    """numId -> {ilvl: numFmt} (Word avtomatik ro'yxatlari uchun)."""
    try:
        root = ET.fromstring(zf.read('word/numbering.xml'))
    except KeyError:
        return {}
    abstract = {}
    for an in root.findall(f'{W}abstractNum'):
        levels = {}
        for lvl in an.findall(f'{W}lvl'):
            fmt = lvl.find(f'{W}numFmt')
            levels[lvl.get(f'{W}ilvl')] = fmt.get(f'{W}val') if fmt is not None else ''
        abstract[an.get(f'{W}abstractNumId')] = levels
    result = {}
    for num in root.findall(f'{W}num'):
        ref = num.find(f'{W}abstractNumId')
        if ref is not None:
            result[num.get(f'{W}numId')] = abstract.get(ref.get(f'{W}val'), {})
    return result


def _is_bold(run):
    rpr = run.find(f'{W}rPr')
    if rpr is None:
        return False
    b = rpr.find(f'{W}b')
    if b is None:
        return False
    return b.get(f'{W}val') not in ('0', 'false')


def read_docx_paragraphs(data):
    """[{'text', 'bold', 'list': None|'letter'|'number'}] hujjatdagi tartibda."""
    try:
        zf = zipfile.ZipFile(BytesIO(data))
        xml = zf.read('word/document.xml')
    except (zipfile.BadZipFile, KeyError):
        raise WordImportError('Fayl Word (.docx) formatida emas. Faylni Word’da ochib ".docx" qilib saqlang.')
    formats = _numbering_formats(zf)
    root = ET.fromstring(xml)
    paragraphs = []
    for p in root.iter(f'{W}p'):
        parts = []
        bold_flags = []
        for run in p.iter(f'{W}r'):
            text = ''
            for node in run:
                if node.tag == f'{W}t':
                    text += node.text or ''
                elif node.tag == f'{W}tab':
                    text += ' '
                elif node.tag in (f'{W}br', f'{W}cr'):
                    text += '\n'
            if text:
                parts.append(text)
                if text.strip():
                    bold_flags.append(_is_bold(run))
        text = ''.join(parts)
        list_kind = None
        ppr = p.find(f'{W}pPr')
        numpr = ppr.find(f'{W}numPr') if ppr is not None else None
        if numpr is not None:
            num_id = numpr.find(f'{W}numId')
            ilvl = numpr.find(f'{W}ilvl')
            num_id = num_id.get(f'{W}val') if num_id is not None else None
            ilvl = ilvl.get(f'{W}val') if ilvl is not None else '0'
            if num_id and num_id != '0':
                fmt = formats.get(num_id, {}).get(ilvl, '')
                list_kind = 'letter' if fmt in LETTER_FORMATS else 'number'
        for line in text.split('\n'):
            if line.strip() or list_kind:
                paragraphs.append({
                    'text': line.strip(),
                    'bold': bool(bold_flags) and all(bold_flags),
                    'list': list_kind,
                })
    return paragraphs


def _new_question(text, number=None):
    return {'number': number, 'text_lines': [text] if text else [], 'options': [], 'answer': None}


def parse_questions(paragraphs):
    questions = []
    current = None
    key_mode = False
    key = {}
    segment_start = 0

    def apply_key():
        # Kalit faqat o'zidan oldingi savollarga tegishli (bitta faylda bir nechta test bo'lishi mumkin).
        nonlocal key, segment_start
        segment = questions[segment_start:]
        for position, q in enumerate(segment, start=1):
            q['key_answer'] = key.get(q['number']) if q['number'] in key else key.get(position)
        key = {}
        segment_start = len(questions)

    def start(text, number=None):
        nonlocal current
        current = _new_question(text, number)
        questions.append(current)

    def add_option(letter, text, marked, bold):
        if current is None:
            return False
        letter = LETTER_MAP.get(letter) if letter else LETTERS[len(current['options'])] if len(current['options']) < 4 else None
        if not letter:
            return False
        text = text.strip()
        # "C) *" kabi variantning o'zi yulduzcha bo'lsa, u belgi emas, variant matni.
        if len(text) > 1 and (text.endswith('*') or text.endswith('(+)')):
            marked = True
            text = text.rstrip('*').removesuffix('(+)').strip()
        current['options'].append({'letter': letter, 'text': text, 'marked': bool(marked), 'bold': bold})
        return True

    for para in paragraphs:
        line = para['text']
        if not line and not para['list']:
            continue

        if key_mode:
            restart = QUESTION_NUM_RE.match(line)
            if restart and len(restart.group(2).strip()) > 3 and not KEY_PAIR_RE.fullmatch(line.strip()):
                apply_key()
                key_mode = False
        if key_mode:
            pairs = KEY_PAIR_RE.findall(line)
            for num, letter in pairs:
                key[int(num)] = LETTER_MAP[letter]
            # Kalit ustun ko'rinishida bo'lsa: har qatorda bitta harf (1-savol, 2-savol, ...).
            single = re.fullmatch(rf'\s*([{LETTER_CHARS}])\s*[.)]?\s*', line)
            if not pairs and single:
                key[len(key) + 1] = LETTER_MAP[single.group(1)]
            continue

        if KEY_HEADER_RE.match(line):
            key_mode = True
            continue

        answer = ANSWER_RE.match(line)
        if answer and current is not None:
            current['answer'] = LETTER_MAP[answer.group(1)]
            continue

        # Bir qatorda bir nechta variant: "A) 5  B) 6  C) 7  D) 8"
        inline = INLINE_SPLIT_RE.findall(' ' + line)
        if len(inline) >= 2:
            pieces = INLINE_SPLIT_RE.split(' ' + line)
            head = pieces[0].strip()
            head_number = QUESTION_NUM_RE.match(head) if head else None
            if head_number and head_number.group(2):
                start(head_number.group(2).strip(), int(head_number.group(1)))
            elif head and (current is None or current['options']):
                start(head)
            elif head:
                current['text_lines'].append(head)
            if current is None:
                continue
            for i in range(1, len(pieces), 3):
                add_option(pieces[i + 1], pieces[i + 2], pieces[i] in ('*', '+'), False)
            continue

        option = OPTION_RE.match(line)
        if option and current is not None and option.group(3):
            letter = LETTER_MAP[option.group(2)]
            used = {o['letter'] for o in current['options']}
            # "A)" yangi savolning boshi emasligini tekshiramiz: harf ketma-ket kelishi kerak.
            if letter not in used and (current['options'] or letter == 'A' or current['text_lines']):
                add_option(option.group(2), option.group(3), option.group(1) in ('*', '+'), para['bold'])
                continue

        if para['list'] == 'letter' and current is not None and len(current['options']) < 4:
            marked = line.startswith('*') or line.startswith('+')
            add_option(None, line.lstrip('*+ ').strip(), marked, para['bold'])
            continue

        number_match = QUESTION_NUM_RE.match(line)
        if number_match and number_match.group(2):
            start(number_match.group(2).strip(), int(number_match.group(1)))
            continue

        if para['list'] == 'number':
            start(line)
            continue

        if current is None or current['options']:
            start(line)
        else:
            current['text_lines'].append(line)

    if key:
        apply_key()

    # Natijani yig'ish va tekshirish.
    result = []
    errors = []
    skipped = []
    for index, q in enumerate(questions, start=1):
        number = q['number'] or index
        text = '\n'.join(q['text_lines']).strip()
        options = {o['letter']: o['text'] for o in q['options']}
        answer = q['answer']
        if not answer:
            marked = [o['letter'] for o in q['options'] if o['marked']]
            if len(marked) == 1:
                answer = marked[0]
        if not answer:
            answer = q.get('key_answer')
        if not answer:
            bold = [o['letter'] for o in q['options'] if o['bold']]
            if len(bold) == 1 and len(q['options']) > 1:
                answer = bold[0]

        if not text and not options:
            continue
        if not options:
            # Variantsiz matn (sarlavha, izoh yoki yozma savol) test sifatida qo'shilmaydi.
            skipped.append(text[:80])
            continue
        short = (text[:60] + '…') if len(text) > 60 else text
        if not text:
            errors.append(f'{number}-savol: savol matni topilmadi.')
            continue
        if len(options) < 2:
            errors.append(f'{number}-savol ("{short}"): kamida 2 ta variant (A, B) kerak.')
            continue
        if not answer:
            errors.append(f'{number}-savol ("{short}"): to‘g‘ri javob ko‘rsatilmagan.')
            continue
        if not options.get(answer):
            errors.append(f'{number}-savol ("{short}"): javob {answer}, lekin bunday variant yo‘q.')
            continue
        result.append({
            'text': text,
            'option_a': options.get('A', ''),
            'option_b': options.get('B', ''),
            'option_c': options.get('C', ''),
            'option_d': options.get('D', ''),
            'correct_answer': answer,
            'image_url': '',
        })
    return result, errors, skipped


def parse_docx(data):
    paragraphs = read_docx_paragraphs(data)
    if not paragraphs:
        raise WordImportError('Faylda matn topilmadi.')
    return parse_questions(paragraphs)


TEMPLATE_LINES = [
    ('Test namunasi. Har bir savolni shu ko‘rinishda yozing.', True),
    ('', False),
    ('1. O‘zbekiston poytaxti qaysi shahar?', False),
    ('A) Samarqand', False),
    ('B) Toshkent', False),
    ('C) Buxoro', False),
    ('D) Xiva', False),
    ('Javob: B', False),
    ('', False),
    ('2. 7 × 8 nechaga teng?', False),
    ('A) 54', False),
    ('B) 56', False),
    ('C) 58', False),
    ('D) 64', False),
    ('Javob: B', False),
    ('', False),
    ('3. Buxorodagi Kalon minorasi qaysi asrda qurilgan?', False),
    ('A) X asr', False),
    ('B) XII asr', False),
    ('C) XV asr', False),
    ('Javob: B', False),
]


def build_template_docx():
    """Namuna Word fayli (Word, LibreOffice va Google Docs'da ochiladi)."""
    def esc(text):
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    body = ''.join(
        f'<w:p><w:r>{"<w:rPr><w:b/></w:rPr>" if bold else ""}<w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>'
        for text, bold in TEMPLATE_LINES
    )
    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        f'<w:body>{body}<w:sectPr/></w:body></w:document>'
    )
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>'
    )
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', content_types)
        zf.writestr('_rels/.rels', rels)
        zf.writestr('word/document.xml', document)
    return buffer.getvalue()
