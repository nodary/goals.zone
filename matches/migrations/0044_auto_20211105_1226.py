# Generated by Django 3.2.9 on 2021-11-05 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0043_auto_20210410_1529'),
    ]

    operations = [
        migrations.RenameField(
            model_name='match',
            old_name='msg_sent',
            new_name='first_msg_sent',
        ),
        migrations.AddField(
            model_name='match',
            name='highlights_msg_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='match',
            name='status',
            field=models.CharField(default='finished', max_length=50),
        ),
    ]
