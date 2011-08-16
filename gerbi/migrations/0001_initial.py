# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

from gerbi import settings
from gerbi.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Page'
        gerbi_page = [
               ('id', orm['gerbi.Page:id']),
               ('author', orm['gerbi.Page:author']),
               ('parent', orm['gerbi.Page:parent']),
               ('creation_date', orm['gerbi.Page:creation_date']),
               ('publication_date', orm['gerbi.Page:publication_date']),
               ('publication_end_date', orm['gerbi.Page:publication_end_date']),
               ('last_modification_date', orm['gerbi.Page:last_modification_date']),
               ('status', orm['gerbi.Page:status']),
               ('template', orm['gerbi.Page:template']),
               ('delegate_to', orm['gerbi.Page:delegate_to']),
               ('redirect_to_url', orm['gerbi.Page:redirect_to_url']),
               ('redirect_to', orm['gerbi.Page:redirect_to']),
               ('lft', orm['gerbi.Page:lft']),
               ('rght', orm['gerbi.Page:rght']),
               ('tree_id', orm['gerbi.Page:tree_id']),
               ('level', orm['gerbi.Page:level'])
               ]
        db.create_table('gerbi_page', gerbi_page)
        db.send_create_signal('gerbi', ['Page'])
        
        # Adding model 'Content'
        db.create_table('gerbi_content', (
            ('id', orm['gerbi.Content:id']),
            ('language', orm['gerbi.Content:language']),
            ('body', orm['gerbi.Content:body']),
            ('type', orm['gerbi.Content:type']),
            ('page', orm['gerbi.Content:page']),
            ('creation_date', orm['gerbi.Content:creation_date']),
        ))
        db.send_create_signal('gerbi', ['Content'])
        
        # Adding model 'PageAlias'
        db.create_table('gerbi_pagealias', (
            ('id', orm['gerbi.PageAlias:id']),
            ('page', orm['gerbi.PageAlias:page']),
            ('url', orm['gerbi.PageAlias:url']),
        ))
        db.send_create_signal('gerbi', ['PageAlias'])
        
        # Adding model 'PagePermission'
        db.create_table('gerbi_pagepermission', (
            ('id', orm['gerbi.PagePermission:id']),
            ('page', orm['gerbi.PagePermission:page']),
            ('user', orm['gerbi.PagePermission:user']),
            ('type', orm['gerbi.PagePermission:type']),
        ))
        db.send_create_signal('gerbi', ['PagePermission'])
        
        if settings.GERBI_USE_SITE_ID:
            # Adding ManyToManyField 'Page.sites'
            db.create_table('gerbi_page_sites', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('page', models.ForeignKey(orm.Page, null=False)),
                ('site', models.ForeignKey(orm['sites.Site'], null=False))
            ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Page'
        db.delete_table('gerbi_page')
        
        # Deleting model 'Content'
        db.delete_table('gerbi_content')
        
        # Deleting model 'PageAlias'
        db.delete_table('gerbi_pagealias')
        
        # Deleting model 'PagePermission'
        db.delete_table('gerbi_pagepermission')
        
        if settings.GERBI_USE_SITE_ID:
            # Dropping ManyToManyField 'Page.sites'
            db.delete_table('gerbi_page_sites')
        
    
    page = {
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'delegate_to': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modification_date': ('django.db.models.fields.DateTimeField', [], {}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['gerbi.Page']"}),
            'publication_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'publication_end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'redirect_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'redirected_pages'", 'null': 'True', 'to': "orm['gerbi.Page']"}),
            'redirect_to_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
            }
    if settings.GERBI_USE_SITE_ID:
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
        'gerbi.content': {
            'body': ('django.db.models.fields.TextField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gerbi.Page']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'gerbi.page': page,
        'gerbi.pagealias': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gerbi.Page']", 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'gerbi.pagepermission': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['gerbi.Page']", 'null': 'True', 'blank': 'True'}),
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
    
    complete_apps = ['gerbi']
