# 2026-10-25: Matematika 1–6-sinf va Kompyuter Excel'da to'g'ri javoblar takrorlanuvchi tartibda (A, C, B, D...) edi.
# Foydalanuvchi roziligi bilan variantlar o'rni aralashtirildi; savol, variantlar va to'g'ri javob o'zgarmaydi. Joyida yangilanadi.
from django.db import migrations

LEVELS = [('Matematika', f'{grade}-sinf') for grade in range(1, 7)] + [('Kompyuter', 'Excel')]
FIELDS = ('text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')


def update_questions(apps, schema_editor):
    from olympiad.tests_data import TESTS

    Question = apps.get_model('olympiad', 'Question')
    data = {(subject, level): items for subject, levels in TESTS for level, _minutes, items in levels}
    for subject, level in LEVELS:
        items = data.get((subject, level)) or []
        questions = list(Question.objects.filter(level__subject__name=subject, level__name=level).order_by('id'))
        if len(questions) != len(items):
            Question.objects.filter(id__in=[q.id for q in questions]).delete()
            continue
        for question, item in zip(questions, items):
            for field in FIELDS:
                setattr(question, field, item[field])
            question.save(update_fields=list(FIELDS))


class Migration(migrations.Migration):
    dependencies = [('olympiad', '0036_komp_25_english_kids_15')]
    operations = [migrations.RunPython(update_questions, migrations.RunPython.noop)]
