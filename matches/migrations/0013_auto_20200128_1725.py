# Generated by Django 2.2.8 on 2020-01-28 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0012_team_logo_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='logo_file',
            field=models.ImageField(default=None, upload_to='media/logos'),
        ),
    ]
