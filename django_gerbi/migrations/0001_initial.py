# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

from django_gerbi import settings
from django_gerbi.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Page'
        django_gerbi_page = [
               ('id', orm['django_gerbi.Page:id']),
               ('author', orm['django_gerbi.Page:author']),
               ('parent', orm['django_gerbi.Page:parent']),
               ('creation_date', orm['django_gerbi.Page:creation_date']),
               ('publication_date', orm['django_gerbi.Page:publication_date']),
               ('publication_end_date', orm['django_gerbi.Page:publication_end_date']),
               ('last_modification_date', orm['django_gerbi.Page:last_modification_date']),
               ('status', orm['django_gerbi.Page:status']),
               ('template', orm['django_gerbi.Page:template']),
               ('delegate_to', orm['django_gerbi.Page:delegate_to']),
               ('redirect_to_url', orm['django_gerbi.Page:redirect_to_url']),
               ('redirect_to', orm['django_gerbi.Page:redirect_to']),
               ('lft', orm['django_gerbi.Page:lft']),
               ('rght', orm['django_gerbi.Page:rght']),
               ('tree_id', orm['django_gerbi.Page:tree_id']),
               ('level', orm['django_gerbi.Page:level'])
               ]
        if settings.DJANGO_GERBI_TAGGING:
            django_gerbi_page.append(('tags', orm['django_gerbi.Page:tags']))
        db.create_table('django_gerbi_page', django_gerbi_page)
        db.send_create_signal('pages', ['Page'])
        
        # Adding model 'Content'
        db.create_table('django_gerbi_content', (
            ('id', orm['django_gerbi.Content:id']),
            ('language', orm['django_gerbi.Content:language']),
            ('body', orm['django_gerbi.Content:body']),
            ('type', orm['django_gerbi.Content:type']),
            ('page', orm['django_gerbi.Content:page']),
            ('creation_date', orm['django_gerbi.Content:creation_date']),
        ))
        db.send_create_signal('pages', ['Content'])
        
        # Adding model 'PageAlias'
        db.create_table('django_gerbi_pagealias', (
            ('id', orm['django_gerbi.PageAlias:id']),
            ('page', orm['django_gerbi.PageAlias:page']),
            ('url', orm['django_gerbi.PageAlias:url']),
        ))
        db.send_create_signal('pages', ['PageAlias'])
        
        # Adding model 'PagePermission'
        db.create_table('django_gerbi_pagepermission', (
            ('id', orm['django_gerbi.PagePermission:id']),
            ('page', orm['django_gerbi.PagePermission:page']),
            ('user', orm['django_gerbi.PagePermission:user']),
            ('type', orm['django_gerbi.PagePermission:type']),
        ))
        db.send_create_signal('pages', ['PagePermission'])
        
        if settings.DJANGO_GERBI_USE_SITE_ID:
            # Adding ManyToManyField 'Page.sites'
            db.create_table('django_gerbi_page_sites', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('page', models.ForeignKey(orm.Page, null=False)),
                ('site', models.ForeignKey(orm['sites.Site'], null=False))
            ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Page'
        db.delete_table('django_gerbi_page')
        
        # Deleting model 'Content'
        db.delete_table('django_gerbi_content')
        
        # Deleting model 'PageAlias'
        db.delete_table('django_gerbi_pagealias')
        
        # Deleting model 'PagePermission'
        db.delete_table('django_gerbi_pagepermission')
        
        if settings.DJANGO_GERBI_USE_SITE_ID:
            # Dropping ManyToManyField 'Page.sites'
            db.delete_table('django_gerbi_page_sites')
        
    
    page = {
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'delegate_to': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modification_date': ('django.db.models.fields.DateTimeField', [], {}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['django_gerbi.Page']"}),
            'publication_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'publication_end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'redirect_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'redirected_pages'", 'null': 'True', 'to': "orm['django_gerbi.Page']"}),
            'redirect_to_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
            }
    if settings.DJANGO_GERBI_TAGGING:
        page['tags'] = ('tagging.fields.TagField', [], {'null': 'True'})
    if settings.DJANGO_GERBI_USE_SITE_ID:
        page['sites'] = ('django.db.models.fields.related.ManyToManyField', [], {'default': '[1]', 'to': "orm['sites.Site']"})
        
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'django_gerbi.content': {
            'body': ('django.db.models.fields.TextField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_gerbi.Page']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'django_gerbi.page': page,
        'django_gerbi.pagealias': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_gerbi.Page']", 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'django_gerbi.pagepermission': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['django_gerbi.Page']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'sites.site': {
            'Meta': {'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }
    
    complete_apps = ['pages']
