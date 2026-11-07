# 2026-11-06: Barcha eski testlar va darajalar o'chiriladi. Yangi testlar ("Test hammasi" arxivi:
# IT, English, Rus tili, Koreys tili, Hamshiralik) shu yerda tests_data.py dan yoziladi.
# O'quvchisi bor eski daraja/fan o'chirilmaydi (o'quvchi va natija saqlanadi), lekin savoli qolmaydi,
# shuning uchun ro'yxatdan o'tish oynasida ko'rinmaydi.
from django.db import migrations


def replace_tests(apps, schema_editor):
    from olympiad.tests_data import TESTS

    Subject = apps.get_model('olympiad', 'Subject')
    Level = apps.get_model('olympiad', 'Level')
    Question = apps.get_model('olympiad', 'Question')

    Question.objects.all().delete()
    Level.objects.filter(students__isnull=True).delete()
    Subject.objects.filter(levels__isnull=True, students__isnull=True).delete()

    for subject_name, levels in TESTS:
        subject, _ = Subject.objects.get_or_create(name=subject_name)
        for level_name, duration_minutes, questions in levels:
            level, _ = Level.objects.get_or_create(
                subject=subject, name=level_name, defaults={'duration_minutes': duration_minutes},
            )
            level.duration_minutes = duration_minutes
            level.save(update_fields=['duration_minutes'])
            Question.objects.bulk_create([
                Question(subject=subject, level=level, version=1, **item) for item in questions
            ])


class Migration(migrations.Migration):
    dependencies = [('olympiad', '0038_student_phones_site_settings')]
    operations = [migrations.RunPython(replace_tests, migrations.RunPython.noop)]
