"""Page CMS page_tags template tags"""
from django import template
from django.utils.safestring import SafeUnicode
from django.template import TemplateSyntaxError

from pages import settings as pages_settings
from pages.plugins.category.models import Category

register = template.Library()


def get_category_from_string_or_id(category_string, lang=None):
    """Return a Category object from a slug or an id"""
    # Please forgive me :/
    try:
        try:
            category_string = int(category_string)
            return Category.objects.get(pk=category_string)
        except ValueError:
            return Category.objects.get(slug=category_string)
    except Category.DoesNotExist:
        pass
    return category_string
    

def category_name(category_slug):
    """
    Gets the name of a category
    """
    try:
        return Category.objects.filter(slug=category_slug).values('title')[0]['title']
    except IndexError:
        return ''
register.simple_tag(category_name)


def pages_for_category(context, category):
    """Render a nested list of all the pages in category

    :param category: category object or slug or id for pages
    """
    lang = context.get('lang', pages_settings.PAGE_DEFAULT_LANGUAGE)
    if not isinstance(category, Category):
        category = get_category_from_string_or_id(category, lang)
    if category:
        pages = category.get_pages()
        context.update({'pages': pages})
    return ''
pages_for_category = register.simple_tag(takes_context=True)(pages_for_category)


def get_category(context, category):
    """
    Retrieve category.
    Be careful with multiple calls, because it uses only one context key

    :param category: category object or slug or id for pages
    """

    lang = context.get('lang', pages_settings.PAGE_DEFAULT_LANGUAGE)
    if not isinstance(category, Category):
        category = get_category_from_string_or_id(category, lang)

    context.update({'category': category})
    return ''
get_category = register.simple_tag(takes_context=True)(get_category)
