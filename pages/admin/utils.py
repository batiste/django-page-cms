# -*- coding: utf-8 -*-
from django.core.urlresolvers import get_mod_func
from pages import settings

def get_connected_models():

    if not settings.PAGE_CONNECTED_MODELS:
        return []
    
    models = []
    for capp in settings.PAGE_CONNECTED_MODELS:
        model = {}
        mod_name, form_name = get_mod_func(capp['form'])
        f = getattr(__import__(mod_name, {}, {}, ['']), form_name)
        model['form'] = f
        mod_name, model_name = get_mod_func(capp['model'])
        model['model_name'] = model_name
        m = getattr(__import__(mod_name, {}, {}, ['']), model_name)
        model['model'] = m
        model['fields'] = []
        for k, v in f.base_fields.iteritems():
            if k is not "page":
                model['fields'].append((model_name.lower() + '_' + k, k, v))
        models.append(model)
    
    return models
