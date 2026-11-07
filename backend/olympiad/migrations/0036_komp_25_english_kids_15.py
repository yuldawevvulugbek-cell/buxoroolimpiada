# 2026-10-25: Kompyuter darajalariga fayldagi 21–25-savollar qo'shiladi (25 tadan), English Kids 15 ta savolga qisqartiriladi.
# Mavjud savollar o'chirilmaydi (natijalar saqlanadi): yetishmagani qo'shiladi, ortiqchasi olib tashlanadi.
from django.db import migrations


def sync(apps, schema_editor):
    from olympiad.tests_data import TESTS

    Question = apps.get_model('olympiad', 'Question')
    Level = apps.get_model('olympiad', 'Level')
    data = {(subject, level): items for subject, levels in TESTS for level, _minutes, items in levels}
    targets = [('Kompyuter', 'Excel'), ('Kompyuter', 'Word Excel PowerPoint'), ('English', 'Kids')]
    for subject, level_name in targets:
        items = data.get((subject, level_name)) or []
        level = Level.objects.filter(subject__name=subject, name=level_name).first()
        if level is None:
            continue
        questions = list(Question.objects.filter(level=level).order_by('id'))
        if not questions:
            continue  # bo'sh daraja seed_demo orqali to'ladi
        texts = [item['text'] for item in items]
        for question in questions:
            if question.text not in texts:
                question.delete()
        existing = set(Question.objects.filter(level=level).values_list('text', flat=True))
        for item in items:
            if item['text'] not in existing:
                Question.objects.create(subject=level.subject, level=level, version=1, **item)


class Migration(migrations.Migration):
    dependencies = [('olympiad', '0035_english_kids_no_written')]
    operations = [migrations.RunPython(sync, migrations.RunPython.noop)]
