# Generated by Django 2.0.2 on 2018-05-15 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='setup',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
    ]
