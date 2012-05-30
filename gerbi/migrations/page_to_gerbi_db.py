from pages.models import Page as PPage, Content as PContent, PageAlias as PPageAlias
from gerbi.models import Page as GPage, Content as GContent, PageAlias as GPageAlias
from django.db.models.fields import AutoField

def mptt_attr_names(klass):
     if not hasattr(klass, '_mptt_meta'):
        return []
     mptt_meta = getattr(klass, '_mptt_meta')
     return [ mptt_meta.tree_id_attr,
              mptt_meta.right_attr,
              # mptt_meta.parent_attr,
              mptt_meta.left_attr,
              mptt_meta.level_attr, ]

mpttf = mptt_attr_names(PPage)

def get_attr_value(attr, object, skip_list=[]):
    value = None
    if AutoField != type(attr) or attr.name in skip_list :
        value = attr.value_from_object(object)
        if attr.rel:
            try:
                value = attr.rel.to.objects.get(pk=value)
            except attr.rel.to.DoesNotExist:
                pass
    return value

def do_migrate_alias(palias, gpage):
    attrs = dict()
    for attr in PPageAlias._meta.fields:
        attrs.update({ attr.name: get_attr_value(attr) })
    # Make shure alias is related to the right page.
    attrs.update({ 'page': gpage })
    GPageAlias.objects.create(**attrs)
    # Done


def do_migrate_aliases(ppage, gpage):
    paliases = PageAlias.objects.filter(page=ppage)
    for palias in aliases:
        do_migrate_alias(palias, gpage)


def do_migrate_contents(pcontent, gpage):
    attrs = dict()
    for attr in pcontent._meta.fields:
        attrs.update({ attr.name: get_attr_value(attr) })
    # Make sure content is related to the right page
    attrs.update({ 'page': gpage })

    GContent.objects.create(**attrs)
    # Done.


def do_migrate_contents(ppage, gpage):
    pcontents = PContent.objects.filter(page=ppage)
    for pcontent in pcontents:
        do_migrate_content(pcontent, gpage)


def do_migrate_page(ppage):
    attrs = dict()
    for attr in PPage._meta.fields:
        attrs.update({ attr.name: get_attr_value(attr, ppage, skip_list=mpttf) })

    print attrs
    #gpage = GPage.object.create(**attrs)

    # do_migrate_contents(ppage, gpage)
    # do_migrate_aliases (ppage, gpage)


def do_migrate_pages():
     pages = PPage.objects.all()[0:1]
     for page in pages:
          do_migrate_page(page)


if '__main__' == __name__:
    do_migrate_pages()
