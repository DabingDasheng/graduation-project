# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-01-01 15:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0009_auto_20190101_2109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='birthday',
            field=models.DateField(null=True),
        ),
    ]
