from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("olympiad", "0037_shuffle_patterned_keys"),
    ]

    operations = [
        migrations.AddField(
            model_name="student",
            name="phone",
            field=models.CharField(blank=True, default="", max_length=30),
        ),
        migrations.AddField(
            model_name="student",
            name="phone2",
            field=models.CharField(blank=True, default="", max_length=30),
        ),
        migrations.CreateModel(
            name="SiteSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("hide_results", models.BooleanField(default=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
