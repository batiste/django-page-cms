from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

class HierarchicalNode(models.Model):
    
    name = models.CharField(max_length=20)
    parent = models.ForeignKey('self', related_name="children", blank=True, null=True)
    order = models.IntegerField(blank=True)
    
    class Admin:
        pass
    
    class Meta:
        ordering = ['order']
   
    def __str__(self):
        return "%s" % (self.name)
   
    def save(self):
        recalculate_order = False
        if not self.order:
            self.order=1
            recalculate_order = True
        super(HierarchicalNode, self).save()
        # not so proud of this code
        if recalculate_order:
            self.set_default_order()
            super(HierarchicalNode, self).save()
        
    def set_default_order(self):
        max = 0
        brothers = self.brothers()
        if brothers.count():
            for brother in brothers:
                if brother.order >= max:
                    max = brother.order
        self.order = max+1
    
    def brothers_and_me(self):
        if self.parent:
            return HierarchicalNode.objects.filter(parent=self.parent)
        else:
            return HierarchicalNode.objects.filter(parent__isnull=True)
        
    def brothers(self):
        return self.brothers_and_me().exclude(pk=self.id)
        
    def is_first(self):
        return self.brothers_and_me().order_by('order')[0:1][0] == self
    
    def is_last(self):
        return self.brothers_and_me().order_by('-order')[0:1][0] == self
        
    @classmethod
    def switch_node(cls, node1, node2):
        buffer = node1.order
        node1.order = node2.order
        node2.order = buffer
        node1.save()
        node2.save()
        
    def up(self):
        brother = self.brothers().order_by('-order').filter(order__lt=self.order+1)[0:1]
        if not brother.count():
            return False
        if brother[0].order == self.order:
            self.set_default_order()
            self.save()
        HierarchicalNode.switch_node(self, brother[0])
        return True
        
    def down(self):
        brother = self.brothers().order_by('order').filter(order__gt=self.order-1)[0:1]
        if not brother.count():
            return False
        brother = brother[0]
        if brother.order == self.order:
            brother.set_default_order()
            brother.save()
        HierarchicalNode.switch_node(self, brother)
        return True
    
    def get_objects(self, object=None):
        """return objects associated with this node. Extra parameter filter by model"""
        objs = HierarchicalObject.objects.filter(node=self)
        if object:
            objs = objs.filter(content_type=ContentType.objects.get_for_model(object))
        return [obj.object for obj in objs]
    
    @classmethod
    def get_first_level_objects(cls, model):
        """return objects associated with first level nodes"""
        ctype = ContentType.objects.get_for_model(model)
        nodes = HierarchicalNode.objects.filter(parent__isnull=True)
        objs = HierarchicalObject.objects.filter(content_type=ctype, node__in=nodes).order_by('hierarchical_hierarchicalnode.order').select_related()
        return [obj.object for obj in objs]
    
    @classmethod
    def get_nodes_by_model(cls, model):
        """return nodes associated with an object of the given model"""
        ctype = ContentType.objects.get_for_model(model)
        return HierarchicalNode.objects.filter(linked_objects__content_type=ctype).distinct()
    
    @classmethod
    def get_nodes_by_object(cls, object):
        """return nodes associated with the given object"""
        ctype = ContentType.objects.get_for_model(object)
        return HierarchicalNode.objects.filter(linked_objects__content_type=ctype, linked_objects__object_id=object.id).distinct()
    
    @classmethod
    def get_parent_object(cls, object):
        """return the first parent object of the same type that the given object"""
        ctype = ContentType.objects.get_for_model(object)
        node = HierarchicalNode.objects.get(linked_objects__content_type=ctype, linked_objects__object_id=object.id)
        if not node.parent:
            return None
        parent = node.parent.linked_objects.filter(content_type=ctype)
        if len(parent) == 0:
            return None
        else:
            return parent[0].object
    
    @classmethod
    def is_parent(cls, object1, object2):
        """tell if object1 is parent of object2"""
        p = cls.get_parent_object(object2)
        while(p):
            if p == object1:
                return True
            p = cls.get_parent_object(p)
        return False
    
    @classmethod
    def get_children_objects(self, object):
        """return children objects of the given object assuming that the object is only associated with one node"""
        ctype = ContentType.objects.get_for_model(object)
        node = HierarchicalNode.objects.get(linked_objects__content_type=ctype, linked_objects__object_id=object.id)
        objs = HierarchicalObject.objects.filter(content_type=ctype, node__in=node.children.all()).order_by('hierarchical_hierarchicalnode.order').select_related()
        return [obj.object for obj in objs]
    
class HierarchicalObject(models.Model):
    
    node = models.ForeignKey(HierarchicalNode, related_name='linked_objects')
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'))
    object_id = models.PositiveIntegerField(_('object id'), db_index=True)
    object = generic.GenericForeignKey('content_type', 'object_id')
    
    class Admin:
        pass
    
    class Meta:
        unique_together = (('node', 'content_type', 'object_id'),)
        
    def __str__(self):
        return "%s : %s" % (self.node, self.object)
        
    @classmethod
    def update_for_object(cls, object, new_nodes):
        """update association between an object and nodes"""
        ctype = ContentType.objects.get_for_model(object)
        if new_nodes:
            if new_nodes is not list:
                new_nodes = [new_nodes]
        else:
            new_nodes = []
        current_nodes = HierarchicalNode.get_nodes_by_object(object)
        for node in new_nodes:
            if node not in current_nodes:
                n = HierarchicalNode.objects.get(pk=node.id)
                HierarchicalObject(node=n, object_id=object.id, content_type=ctype).save()
        for node in current_nodes:
            if node not in new_nodes:
                HierarchicalObject.objects.filter(object_id=object.id, content_type=ctype, node=node).delete()

