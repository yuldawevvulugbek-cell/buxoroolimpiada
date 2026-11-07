from django.db import migrations


def clear_english(apps, schema_editor):
    # Ingliz tili testlari yangilari bilan almashtiriladi: eski savollar o'chiriladi,
    # seed_demo esa bo'sh qolgan darajalarga tests_data.py dagi yangi savollarni yuklaydi.
    Question = apps.get_model('olympiad', 'Question')
    Question.objects.filter(subject__name='English').delete()


class Migration(migrations.Migration):
    dependencies = [('olympiad', '0030_open_questions')]
    operations = [migrations.RunPython(clear_english, migrations.RunPython.noop)]
