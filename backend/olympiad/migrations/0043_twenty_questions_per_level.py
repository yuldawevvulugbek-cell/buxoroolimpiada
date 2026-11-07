# 2026-11-07: har bir darajada 20 tadan savol qoladi. 20 dan ortiq savollar (eng oxirgi qo'shilganlari) o'chiriladi.
from django.db import migrations

LIMIT = 20


def forwards(apps, schema_editor):
    Level = apps.get_model('olympiad', 'Level')
    Question = apps.get_model('olympiad', 'Question')
    for level in Level.objects.all():
        for version in Question.objects.filter(level=level).values_list('version', flat=True).distinct():
            ids = list(Question.objects.filter(level=level, version=version).order_by('id').values_list('id', flat=True))
            if len(ids) > LIMIT:
                Question.objects.filter(id__in=ids[LIMIT:]).delete()


class Migration(migrations.Migration):
    dependencies = [('olympiad', '0042_python_level_and_rename')]
    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
