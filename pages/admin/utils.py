# -*- coding: utf-8 -*-
from pages import settings
from django.contrib import admin
from django.forms import ModelForm
import re
from django.core.urlresolvers import get_mod_func
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.cache import cache
from pages.models import Page, Content
from pages.utils import get_placeholders

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

        models.append((m, options))

    return models

def make_inline_admin(model_class, options):
    class ModelOptions(admin.StackedInline):
        model = model_class
        fk_name = 'page'
        form = options.get('form', ModelForm)
        extra = options.get('extra', 3)
        max_num = options.get('max_num', 0)
    return ModelOptions

