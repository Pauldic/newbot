# Generated by Django 2.0.2 on 2018-05-16 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_auto_20180515_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='src_time',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='news',
            name='author',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
    ]
