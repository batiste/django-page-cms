# -*- coding: utf-8 -*-
from pages import settings
from django.contrib import admin
from django.forms import ModelForm
from django.core.urlresolvers import get_mod_func
import django

def get_connected():
    if not settings.PAGE_CONNECTED_MODELS:
        return []

    models = []
    for capp in settings.PAGE_CONNECTED_MODELS:
        model = {}
        mod_name, model_name = get_mod_func(capp['model'])
        model['model_name'] = model_name
        m = getattr(__import__(mod_name, {}, {}, ['']), model_name)
        model['model'] = m

        options = capp.get('options', {})
        model['options'] = options

        if 'form' in capp:
            mod_name, form_name = get_mod_func(capp['form'])
            f = getattr(__import__(mod_name, {}, {}, ['']), form_name)
            model['options'].update({'form': f})
            
        admin_class = admin.StackedInline
        if 'admin' in capp:
            mod_name, admin_class_name = get_mod_func(capp['admin'])
            admin_class = getattr(__import__(mod_name, {}, {}, ['']), admin_class_name)

        models.append((admin_class, m, options))

    return models


def make_inline_admin(admin_class, model_class, options):

    class ModelOptions(admin_class):
        model = model_class
        fk_name = 'page'
        form = options.get('form', ModelForm)
        extra = options.get('extra', 3)

        # Since Django 1.2, max_num=None sets unlimited inlines, 
        # see https://docs.djangoproject.com/en/1.2/topics/forms/modelforms/#model-formsets-max-num
        max_num = options.get('max_num', 0 if django.VERSION < (1, 2) else None)
    return ModelOptions
