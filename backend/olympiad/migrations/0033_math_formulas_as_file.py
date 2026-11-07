# 2026-10-25: Matematika 1–11-sinf savollari "Matem" arxividagidek: formulalar (kasr, daraja, ildiz) \( ... \) ichida
# yoziladi va saytda Word'dagidek chiziladi; savol, variant va javob kaliti fayldagidek.
# Savollar soni mos kelsa joyida yangilanadi (natijalar saqlanadi), aks holda o'chiriladi va seed_demo qayta yuklaydi.
from django.db import migrations

FIELDS = ('text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')


def update_questions(apps, schema_editor):
    from olympiad.tests_data import TESTS

    Question = apps.get_model('olympiad', 'Question')
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
    dependencies = [('olympiad', '0032_english_tests_v2_remove_starter')]
    operations = [migrations.RunPython(update_questions, migrations.RunPython.noop)]
