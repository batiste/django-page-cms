# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0006_auto_20170119_0628'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='language',
            field=models.CharField(max_length=7, verbose_name='language'),
        ),
    ]
