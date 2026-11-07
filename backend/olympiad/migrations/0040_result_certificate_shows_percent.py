from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("olympiad", "0039_replace_all_tests_2026_11"),
    ]

    operations = [
        migrations.AddField(
            model_name="result",
            name="certificate_shows_percent",
            field=models.BooleanField(default=False),
        ),
    ]
