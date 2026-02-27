# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='sites',
            field=models.ManyToManyField(default=[1], help_text='The site(s) the page is accessible at.', verbose_name='sites', to='sites.Site'),
        ),
    ]
