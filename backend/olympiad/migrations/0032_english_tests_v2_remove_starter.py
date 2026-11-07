from django.db import migrations


def replace_english(apps, schema_editor):
    # Ingliz tili testlari yangi fayllar (English_test_2) bilan almashtiriladi va Starter darajasi olib tashlanadi.
    # Starter'dagi o'quvchilar Kids darajasiga o'tkaziladi, keyin Starter o'chiriladi.
    # seed_demo bo'sh qolgan darajalarga tests_data.py dagi yangi savollarni yuklaydi.
    Question = apps.get_model('olympiad', 'Question')
    Level = apps.get_model('olympiad', 'Level')
    Student = apps.get_model('olympiad', 'Student')
    Question.objects.filter(subject__name='English').delete()
    for starter in Level.objects.filter(subject__name='English', name__iexact='Starter'):
        kids, _ = Level.objects.get_or_create(subject=starter.subject, name='Kids', defaults={'duration_minutes': 30})
        Student.objects.filter(level=starter).update(level=kids)
        starter.delete()


class Migration(migrations.Migration):
    dependencies = [('olympiad', '0031_english_new_tests')]
    operations = [migrations.RunPython(replace_english, migrations.RunPython.noop)]
