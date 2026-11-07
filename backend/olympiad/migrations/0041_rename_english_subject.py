# 2026-11-06: platforma o'zbekcha: "English" fani "Ingliz tili" deb nomlanadi.
from django.db import migrations


def rename(apps, schema_editor):
    Subject = apps.get_model('olympiad', 'Subject')
    if Subject.objects.filter(name='Ingliz tili').exists():
        return
    Subject.objects.filter(name='English').update(name='Ingliz tili')


class Migration(migrations.Migration):
    dependencies = [('olympiad', '0040_result_certificate_shows_percent')]
    operations = [migrations.RunPython(rename, migrations.RunPython.noop)]
