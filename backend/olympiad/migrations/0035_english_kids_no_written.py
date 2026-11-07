# 2026-10-25: English Kids darajasidan yozma (open) savollar olib tashlandi, 20 ta variantli savol qoladi.
from django.db import migrations


def remove_open(apps, schema_editor):
    Question = apps.get_model('olympiad', 'Question')
    Question.objects.filter(subject__name='English', level__name='Kids', question_type='open').delete()


class Migration(migrations.Migration):
    dependencies = [('olympiad', '0034_it_25_and_math_fixes')]
    operations = [migrations.RunPython(remove_open, migrations.RunPython.noop)]
