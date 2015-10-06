# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pages.utils
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=5, verbose_name='language')),
                ('body', models.TextField(verbose_name='body', blank=True)),
                ('type', models.CharField(max_length=100, verbose_name='type', db_index=True)),
                ('creation_date', models.DateTimeField(default=pages.utils.get_now, verbose_name='creation date', editable=False)),
            ],
            options={
                'get_latest_by': 'creation_date',
                'verbose_name': 'content',
                'verbose_name_plural': 'contents',
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateTimeField(default=pages.utils.get_now, verbose_name='creation date', editable=False)),
                ('publication_date', models.DateTimeField(help_text='When the page should go\n            live. Status must be "Published" for page to go live.', null=True, verbose_name='publication date', blank=True)),
                ('publication_end_date', models.DateTimeField(help_text='When to expire the page.\n            Leave empty to never expire.', null=True, verbose_name='publication end date', blank=True)),
                ('last_modification_date', models.DateTimeField(verbose_name='last modification date')),
                ('status', models.IntegerField(default=0, verbose_name='status', choices=[(1, 'Published'), (3, 'Hidden'), (0, 'Draft')])),
                ('template', models.CharField(max_length=100, null=True, verbose_name='template', blank=True)),
                ('delegate_to', models.CharField(max_length=100, null=True, verbose_name='delegate to', blank=True)),
                ('freeze_date', models.DateTimeField(help_text="Don't publish any content\n            after this date.", null=True, verbose_name='freeze date', blank=True)),
                ('redirect_to_url', models.CharField(max_length=200, null=True, blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('author', models.ForeignKey(verbose_name='author', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(related_name='children', verbose_name='parent', blank=True, to='pages.Page', null=True)),
                ('redirect_to', models.ForeignKey(related_name='redirected_pages', blank=True, to='pages.Page', null=True)),
            ],
            options={
                'ordering': ['tree_id', 'lft'],
                'get_latest_by': 'publication_date',
                'verbose_name': 'page',
                'verbose_name_plural': 'pages',
                'permissions': [('can_freeze', 'Can freeze page'), ('can_publish', 'Can publish page'), ('can_manage_de', 'Manage German'), ('can_manage_fr_ch', 'Manage Swiss french'), ('can_manage_en_us', 'Manage US English')],
            },
        ),
        migrations.CreateModel(
            name='PageAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(unique=True, max_length=255)),
                ('page', models.ForeignKey(verbose_name='page', blank=True, to='pages.Page', null=True)),
            ],
            options={
                'verbose_name_plural': 'Aliases',
            },
        ),
        migrations.AddField(
            model_name='content',
            name='page',
            field=models.ForeignKey(verbose_name='page', to='pages.Page'),
        ),
    ]
