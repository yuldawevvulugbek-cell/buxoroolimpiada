# 2026-10-25: IT darajalari (HTML CSS, JavaScript, React, Vue, Python) yangi testlar bilan almashtiriladi (har birida 25 ta):
# eski savollar o'chiriladi, seed_demo bo'sh darajalarga tests_data.py dagi yangi savollarni yuklaydi.
# Matematika 1–11-sinf: foydalanuvchi roziligi bilan 21 ta savoldagi kalit/variant xatolari tuzatildi (joyida yangilanadi).
from django.db import migrations

FIELDS = ('text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')


def update(apps, schema_editor):
    from olympiad.tests_data import TESTS

    Question = apps.get_model('olympiad', 'Question')
    Question.objects.filter(subject__name='IT').delete()
    data = {(subject, level): items for subject, levels in TESTS for level, _minutes, items in levels}
    for grade in range(1, 12):
        level = f'{grade}-sinf'
        items = data.get(('Matematika', level)) or []
        questions = list(Question.objects.filter(level__subject__name='Matematika', level__name=level).order_by('id'))
        if len(questions) != len(items):
            Question.objects.filter(id__in=[q.id for q in questions]).delete()
            continue
        for question, item in zip(questions, items):
            for field in FIELDS:
                setattr(question, field, item[field])
            question.save(update_fields=list(FIELDS))


class Migration(migrations.Migration):
    dependencies = [('olympiad', '0033_math_formulas_as_file')]
    operations = [migrations.RunPython(update, migrations.RunPython.noop)]
