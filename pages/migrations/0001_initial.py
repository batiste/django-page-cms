# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

from pages import settings
from pages.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Page'
        pages_page = [
               ('id', orm['pages.Page:id']),
               ('author', orm['pages.Page:author']),
               ('parent', orm['pages.Page:parent']),
               ('creation_date', orm['pages.Page:creation_date']),
               ('publication_date', orm['pages.Page:publication_date']),
               ('publication_end_date', orm['pages.Page:publication_end_date']),
               ('last_modification_date', orm['pages.Page:last_modification_date']),
               ('status', orm['pages.Page:status']),
               ('template', orm['pages.Page:template']),
               ('delegate_to', orm['pages.Page:delegate_to']),
               ('redirect_to_url', orm['pages.Page:redirect_to_url']),
               ('redirect_to', orm['pages.Page:redirect_to']),
               ('lft', orm['pages.Page:lft']),
               ('rght', orm['pages.Page:rght']),
               ('tree_id', orm['pages.Page:tree_id']),
               ('level', orm['pages.Page:level'])
               ]
        if settings.PAGE_TAGGING:
            pages_page.append(('tags', orm['pages.Page:tags']))
        db.create_table('pages_page', pages_page)
        db.send_create_signal('pages', ['Page'])
        
        # Adding model 'Content'
        db.create_table('pages_content', (
            ('id', orm['pages.Content:id']),
            ('language', orm['pages.Content:language']),
            ('body', orm['pages.Content:body']),
            ('type', orm['pages.Content:type']),
            ('page', orm['pages.Content:page']),
            ('creation_date', orm['pages.Content:creation_date']),
        ))
        db.send_create_signal('pages', ['Content'])
        
        # Adding model 'PageAlias'
        db.create_table('pages_pagealias', (
            ('id', orm['pages.PageAlias:id']),
            ('page', orm['pages.PageAlias:page']),
            ('url', orm['pages.PageAlias:url']),
        ))
        db.send_create_signal('pages', ['PageAlias'])
        
        # Adding model 'PagePermission'
        db.create_table('pages_pagepermission', (
            ('id', orm['pages.PagePermission:id']),
            ('page', orm['pages.PagePermission:page']),
            ('user', orm['pages.PagePermission:user']),
            ('type', orm['pages.PagePermission:type']),
        ))
        db.send_create_signal('pages', ['PagePermission'])
        
        if settings.PAGE_USE_SITE_ID:
            # Adding ManyToManyField 'Page.sites'
            db.create_table('pages_page_sites', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('page', models.ForeignKey(orm.Page, null=False)),
                ('site', models.ForeignKey(orm['sites.Site'], null=False))
            ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Page'
        db.delete_table('pages_page')
        
        # Deleting model 'Content'
        db.delete_table('pages_content')
        
        # Deleting model 'PageAlias'
        db.delete_table('pages_pagealias')
        
        # Deleting model 'PagePermission'
        db.delete_table('pages_pagepermission')
        
        if settings.PAGE_USE_SITE_ID:
            # Dropping ManyToManyField 'Page.sites'
            db.delete_table('pages_page_sites')
        
    
    page = {
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'delegate_to': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modification_date': ('django.db.models.fields.DateTimeField', [], {}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['pages.Page']"}),
            'publication_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'publication_end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'redirect_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'redirected_pages'", 'null': 'True', 'to': "orm['pages.Page']"}),
            'redirect_to_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
            }
    if settings.PAGE_TAGGING:
        page['tags'] = ('tagging.fields.TagField', [], {'null': 'True'})
    if settings.PAGE_USE_SITE_ID:
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
        'pages.content': {
            'body': ('django.db.models.fields.TextField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pages.Page']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'pages.page': page,
        'pages.pagealias': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pages.Page']", 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'pages.pagepermission': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pages.Page']", 'null': 'True', 'blank': 'True'}),
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
