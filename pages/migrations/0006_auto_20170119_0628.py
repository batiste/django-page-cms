# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-01-19 06:28
from __future__ import unicode_literals

from django.db import migrations, models
import pages.models
import pages.utils


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0005_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='creation_date',
            field=models.DateTimeField(default=pages.utils.get_now, editable=False, verbose_name='creation date'),
        ),
        migrations.AlterField(
            model_name='media',
            name='url',
            field=models.FileField(upload_to=pages.models.media_filename),
        ),
    ]
