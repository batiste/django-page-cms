from utils import auto_render
from hierarchical.models import HierarchicalNode, HierarchicalObject
from django.contrib.admin.views.decorators import staff_member_required
from django import newforms as forms
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_unicode, smart_str
from django.utils.translation import ugettext as _
from django import newforms as forms
from django.contrib.contenttypes.models import ContentType

@staff_member_required
@auto_render
def list_nodes(request):
    opts = HierarchicalNode._meta
    nodes = HierarchicalNode.objects.filter(parent__isnull=True)
    return 'hierarchical/change_list.html', locals()

@staff_member_required
@auto_render
def up(request, hnode_id):
    node = HierarchicalNode.objects.get(pk=hnode_id)
    node.up()
    return HttpResponseRedirect("../../")

@staff_member_required
@auto_render
def down(request, hnode_id):
    node = HierarchicalNode.objects.get(pk=hnode_id)
    node.down()
    return HttpResponseRedirect("../../")

from django.newforms import ModelForm
class HierarchicalObjectForm(ModelForm):
    class Meta:
        model = HierarchicalObject

@staff_member_required
@auto_render
def modify(request, hobject_id):
    opts = HierarchicalNode._meta
    change = True
    has_absolute_url = True
    hnode = HierarchicalObject.objects.get(pk=hobject_id)
    if request.POST:
        form = HierarchicalObjectForm(request.POST, instance=hnode)
        if form.is_valid():
            form.save()
            msg = _('The %(name)s "%(obj)s" was changed successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(hnode)}
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect("../")
    else:
        form = HierarchicalObjectForm(instance=hnode)
    return 'hierarchical/change_form.html', locals()
    
@staff_member_required
@auto_render
def add(request):
    opts = HierarchicalNode._meta
    add = True
    hnode = HierarchicalObject()
    if request.POST:
        form = HierarchicalObjectForm(request.POST, instance=hnode)
        if form.is_valid():
            form.save()
            msg = _('The %(name)s "%(obj)s" was created successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(hnode)}
            request.user.message_set.create(message=msg)
            return HttpResponseRedirect("../")
    else:
        form = HierarchicalObjectForm(instance=hnode)
    return 'hierarchical/change_form.html', locals()

@staff_member_required
@auto_render
def get_objects_by_model(request, content_type_id):
    ct = ContentType.objects.get(id=content_type_id)
    objects = ct.model_class().objects.all()
    return 'hierarchical/select.html', locals()
    