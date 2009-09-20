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
from pages.lib.BeautifulSoup import BeautifulSoup

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


# (extra) pagelink
def get_pagelink_absolute_url(page, language=None):
    """
    get the url of this page, adding parent's slug - with not cache usage
    """
    url = u'%s' % page.slug(language)
    for ancestor in page.get_ancestors(ascending=True):
        url = ancestor.slug(language) + u'/' + url

    return reverse('pages-root') + url

# (extra) pagelink
def valide_url(value):
    """
    return 1 if URL is validate
    """
    if value == u'':
        return 1
    import urllib2
    headers = {
        "Accept": "text/xml,application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5",
        "Accept-Language": "en-us,en;q=0.5",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
        "Connection": "close",
        "User-Agent": settings.PAGE_URL_VALIDATOR_USER_AGENT,
    }
    try:
        req = urllib2.Request(value, None, headers)
        u = urllib2.urlopen(req)
    except:
        return 0
    return 1

page_id_regexp = re.compile('^page_[0-9]+$')

# for pagelink
def get_body_pagelink_ids(page):
    """
    return all 'page_ID' found in body content.
    """
    pagelink_ids = []
    for placeholder in get_placeholders(page.get_template()):
        if placeholder.widget in settings.PAGE_LINK_EDITOR:
            for language in page.get_languages():
                try:
                    content = Content.objects.filter(
                        language=language,
                        type=placeholder.name, page=page
                    ).latest()
                    body = BeautifulSoup(content.body)
                    # find page link ID
                    tags = body.findAll('a', \
                                    {'class': page_id_regexp})
                    for tag in tags:
                        pagelink_ids.append(int(tag['class'] \
                                        .replace('page_','')))
                except Content.DoesNotExist:
                    pass

    if pagelink_ids:
        return list(set(pagelink_ids)) # remove duplicates
    else:
        return None

PAGE_CONTENT_DICT_KEY = "page_content_dict_%s_%s"

# for pagelink
def set_body_pagelink(page, initial_pagelink_ids=None):
    """
    Set or update page link(s) with slug and title based on the class 'page_ID'
    + set or update 'externallink_broken' db value if invalide URL found 
    and add class or remove 'externallink_broken' 
    (url 'http://' string to be checked) 
    + set or update number of 'pagelink_broken'
    """
    pagelink_ids = []
    externallink_broken = pagelink_broken = 0
    for placeholder in get_placeholders(page.get_template()):
        if placeholder.widget in settings.PAGE_LINK_EDITOR:
            content_dict = {}            
            # analyze content by langugage
            for language in page.get_languages():
                try:
                    content = Content.objects.filter(
                                language=language, 
                                type=placeholder.name, 
                                page=page).latest()
                    body = BeautifulSoup(content.body)

                    # find all page link
                    tags = body.findAll('a')
                    for tag in tags:
                        if tag.string and tag.string.strip():
                            if tag.get('class',''):
                                # find page link with class 'page_ID'
                                if page_id_regexp.match(tag['class']):
                                    pagelink_ids.append(tag['class'] \
                                            .replace('page_',''))
                                # find page link with class 'pagelink_broken'
                                if 'pagelink_broken' in tag['class']:
                                    pagelink_broken += 1 
                            # check URL validity
                            # set class 'externallink_broken' 
                            # if link return a 404
                            if 'http://' in tag.get('href','') \
                            and not valide_url(tag['href']):
                                externallink_broken += 1
                                tag['class'] = 'externallink_broken'
                        else:
                            # remove empty tag (prevent false-positive)
                            tag.extract()
                    content.body = unicode(body)
                    content.save()
                    content_dict[language] = content.body
                except Content.DoesNotExist:
                    content_dict[language] = ''
            cache.set(PAGE_CONTENT_DICT_KEY % 
                (str(page.id), placeholder.name), content_dict)
    page.externallink_broken = externallink_broken
    page.pagelink_broken = pagelink_broken
    page.save()
 
    pagelink_ids = list(set(pagelink_ids)) # remove duplicates

    # set/update 'pagelink' of pages concerned
    for pk, obj in Page.objects.in_bulk(pagelink_ids).items():
        if obj.pagelink is not None:
            obj_pagelink_ids = obj.pagelink.split(',')
            if obj_pagelink_ids[0] !='':
                if str(page.id) not in obj_pagelink_ids:
                    obj_pagelink_ids.append(str(page.id))
            else:
                obj_pagelink_ids = str(page.id)
        else:
            obj_pagelink_ids = str(page.id)

        if obj_pagelink_ids:
            obj.pagelink = ','.join(obj_pagelink_ids)
            obj.save()

        # set/update all link 'a' of body content
        for placeholder in get_placeholders(page.get_template()):
            if placeholder.widget in settings.PAGE_LINK_EDITOR:
                content_dict = {}
                for language in page.get_languages():
                    try:
                        content = Content.objects.filter(
                                        language=language, 
                                        type=placeholder.name, 
                                        page=page).latest()
                        body = BeautifulSoup(content.body)
                        tags = body.findAll('a', attrs={'class': 'page_'
                                        +str(obj.id)})
                        for tag in tags:
                            if tag.string and tag.string.strip():
                                tag['title'] = obj.title(language)
                                tag['href'] = get_pagelink_absolute_url(obj, language)
                        content.body = unicode(body)
                        content.save()
                        content_dict[language] = content.body
                    except Content.DoesNotExist:
                        content_dict[language] = ''
                cache.set(PAGE_CONTENT_DICT_KEY % 
                    (str(page.id), placeholder.name), content_dict)

    # update 'pagelink', if link removed from body
    update_pagelink_ids = removed_pagelink_ids = []
    if initial_pagelink_ids is not None:
        removed_pagelink_ids =  [id for id in initial_pagelink_ids \
                                        if id not in pagelink_ids]
        if removed_pagelink_ids[0] !='':
            for pk, obj in Page.objects.in_bulk(removed_pagelink_ids).items():
                if obj.pagelink:
                    update_pagelink_ids = obj.pagelink.split(',')
                    if update_pagelink_ids[0] !='' \
                    and str(page.id) in update_pagelink_ids:
                        update_pagelink_ids.remove(str(page.id))
                        if update_pagelink_ids[0] !='':
                            obj.pagelink = ','.join(update_pagelink_ids)
                        else:
                            obj.pagelink = ''
                        obj.save()

# for pagelink (move on the tree)
def update_body_pagelink(page):
    """
    update internal link(s) of body content, specialy the 'url' and 
    of all there children.
    """
    if page.pagelink is not None:
        pagelink_ids = page.pagelink.split(',')
        if pagelink_ids[0] != '':
            for pk, obj in Page.objects.in_bulk(pagelink_ids).items():
                for placeholder in get_placeholders(obj.get_template()):
                    if placeholder.widget in settings.PAGE_LINK_EDITOR:
                        content_dict = {}
                        for language in obj.get_languages():
                            try:
                                content = Content.objects.filter(
                                            language=language, 
                                            type=placeholder.name, 
                                            page=obj).latest()
                                body = BeautifulSoup(content.body)
                                tags = body.findAll('a', attrs={'class': 'page_'
                                                        +str(page.id)})
                                for tag in tags:
                                    if tag.string and tag.string.strip():
                                        tag['title'] = obj.title(language)
                                        tag['href'] = get_pagelink_absolute_url(obj, language)
                                content.body = unicode(body)
                                content.save()
                                content_dict[language] = content.body
                            except Content.DoesNotExist:
                                content_dict[language] = ''
                        cache.set(PAGE_CONTENT_DICT_KEY % 
                            (str(obj.id), placeholder.name), content_dict)

    # update new 'url' of children pages 
    for children_page in page.children.all():
        if children_page.pagelink is not None:
            pagelink_ids = children_page.pagelink.split(',')
            if pagelink_ids[0] !='':
                for pk, obj in Page.objects.in_bulk(pagelink_ids).items():
                    for placeholder in get_placeholders(obj.get_template()):
                        if placeholder.widget in settings.PAGE_LINK_EDITOR:
                            content_dict = {}
                            for language in obj.get_languages():
                                try:
                                    content = Content.objects.filter(
                                                language=language, 
                                                type=placeholder.name, 
                                                page=obj).latest()
                                    body = BeautifulSoup(content.body)
                                    tags = body.findAll('a', attrs={'class': 'page_'
                                                        +str(page.id)})
                                    for tag in tags:
                                        if tag.string and tag.string.strip():
                                            tag['title'] = page.title(language)
                                            tag['href'] = get_pagelink_absolute_url(page, language)
                                    content.body = unicode(body)
                                    content.save() 
                                    content_dict[language] = content.body
                                except Content.DoesNotExist:
                                    content_dict[language] = ''
                            cache.set(PAGE_CONTENT_DICT_KEY % 
                                (str(obj.id), placeholder.name), content_dict)

# for pagelink
def delete_body_pagelink_by_language(page, language):
    """
    set class 'pagelink_broken' of all 'a' tags of body for a language.
    + clear pagelink page ID entries.
    """
    if page.pagelink is not None:
        pagelink_ids = page.pagelink.split(',')
        if pagelink_ids[0] !='':
            for pk, obj in Page.objects.in_bulk(pagelink_ids).items():
                if obj.id != page.id:
                    obj_pagelink_broken = obj_externallink_broken = 0
                    for placeholder in get_placeholders(obj.get_template()):
                        if placeholder.widget in settings.PAGE_LINK_EDITOR:
                            for lang in obj.get_languages():
                                try:
                                    content = Content.objects.filter(
                                                    language=language, 
                                                    type=placeholder.name, 
                                                    page=obj).latest()
                                    body = BeautifulSoup(content.body)
                                    tags = body.findAll('a')
                                    for tag in tags:
                                        if tag.string and tag.string.strip():
                                            if tag.get('class',''):
                                                # for the removed language
                                                if lang == language:
                                                    # if link(s) with the page_id > set link to broken
                                                    if tag['class'] == 'page_' +str(page.id):
                                                        obj_pagelink_broken += 1
                                                        tag['class']="pagelink_broken"
                                                # for other language(s)
                                                else:
                                                    # count already broken page link(s)
                                                    if tag['class'] == 'pagelink_broken':
                                                        obj_pagelink_broken += 1
                                                    # count already external broken link(s)
                                                    if tag['class'] == 'externallink_broken':
                                                        obj_externallink_broken += 1
                                    content.body = unicode(body)
                                    content.save()
                                except Content.DoesNotExist:
                                    pass
                            # clear cache entry
                            cache.delete(PAGE_CONTENT_DICT_KEY % 
                                (str(obj.id), placeholder.name))
                    obj.pagelink_broken = obj_pagelink_broken
                    obj.externallink_broken = obj_externallink_broken
                    obj.save()

    # find page link ID + count pagelink_broken and externallink_broken
    pagelink_ids = other_language_pagelink_ids = []
    pagelink_broken = externallink_broken = 0
    for placeholder in get_placeholders(page.get_template()):
        if placeholder.widget in settings.PAGE_LINK_EDITOR:
            for lang in page.get_languages():
                try:
                    content = Content.objects.filter(
                                    language=lang, 
                                    type=placeholder.name, 
                                    page=page).latest()
                    body = BeautifulSoup(content.body)
                    tags = body.findAll('a')
                    for tag in tags:
                        if tag.string and tag.string.strip():
                            if tag.get('class',''):
                                if page_id_regexp.match(tag['class']):
                                    pagelink_ids.append(tag['class'] \
                                                    .replace('page_',''))
                                    if lang != language:
                                        other_language_pagelink_ids \
                                                    .append(tag['class'] \
                                                    .replace('page_',''))
                                # find broken external link
                                if lang != language:
                                    if 'pagelink_broken' in tag['class']:
                                        pagelink_broken += 1
                                    if 'externallink_broken' in tag['class']:
                                        externallink_broken += 1
                except Content.DoesNotExist:
                    pass
    page.pagelink_broken = pagelink_broken
    page.externallink_broken = externallink_broken
    page.save()

    # remove duplicates
    pagelink_ids = list(set(pagelink_ids))
    other_language_pagelink_ids = list(set(other_language_pagelink_ids))
   
    # update 'pagelink's, remove page.id
    for pk, obj in Page.objects.in_bulk(pagelink_ids).items():
        if obj.pagelink is not None:
            obj_pagelink_ids = obj.pagelink.split(',')
            if obj_pagelink_ids[0] !='':
                if str(page.id) in obj_pagelink_ids \
                and str(obj.id) not in other_language_pagelink_ids: 
                    obj_pagelink_ids.remove(str(page.id))
                    if obj_pagelink_ids[0] !='':
                        obj.pagelink = ','.join(obj_pagelink_ids)
                    else:
                        obj.pagelink = ''
                    obj.save()
