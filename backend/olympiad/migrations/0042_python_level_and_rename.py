# 2026-11-07: "Umumiy" darajalar fanga mos nomlanadi va IT fanida Python darajasi qo'shiladi.
from django.db import migrations

RENAMES = [('Koreys tili', 'Umumiy', 'Koreys tili 1'), ('Hamshiralik', 'Umumiy', 'Hamshiralik 1')]


def forwards(apps, schema_editor):
    from olympiad.tests_data import TESTS

    Subject = apps.get_model('olympiad', 'Subject')
    Level = apps.get_model('olympiad', 'Level')
    Question = apps.get_model('olympiad', 'Question')

    for subject_name, old, new in RENAMES:
        subject = Subject.objects.filter(name=subject_name).first()
        if not subject or Level.objects.filter(subject=subject, name=new).exists():
            continue
        Level.objects.filter(subject=subject, name=old).update(name=new)

    python_tests = next(
        (level for subject_name, levels in TESTS if subject_name == 'IT' for level in levels if level[0] == 'Python'),
        None,
    )
    if not python_tests:
        return
    level_name, minutes, questions = python_tests
    subject, _ = Subject.objects.get_or_create(name='IT')
    level, _ = Level.objects.get_or_create(subject=subject, name=level_name, defaults={'duration_minutes': minutes})
    if Question.objects.filter(subject=subject, level=level).exists():
        return
    Question.objects.bulk_create([
        Question(subject=subject, level=level, version=1, **item) for item in questions
    ])


def backwards(apps, schema_editor):
    Level = apps.get_model('olympiad', 'Level')
    for subject_name, old, new in RENAMES:
        Level.objects.filter(subject__name=subject_name, name=new).update(name=old)


class Migration(migrations.Migration):
    dependencies = [('olympiad', '0041_rename_english_subject')]
    operations = [migrations.RunPython(forwards, backwards)]
