# Generated by Django 3.0.3 on 2020-03-06 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0031_auto_20200304_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='videogoal',
            name='author',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='videogoalmirror',
            name='author',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
