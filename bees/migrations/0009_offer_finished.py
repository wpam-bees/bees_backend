# Generated by Django 2.1.2 on 2018-12-27 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bees', '0008_auto_20181227_0941'),
    ]

    operations = [
        migrations.AddField(
            model_name='offer',
            name='finished',
            field=models.BooleanField(default=False),
        ),
    ]
