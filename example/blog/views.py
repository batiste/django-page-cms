from django.shortcuts import render
from pages.models import Page
from taggit.models import Tag
from django.core.paginator import Paginator

def category_view(request, *args, **kwargs):
    context = dict(kwargs)
    category = Tag.objects.get(id=kwargs['tag_id'])
    page = context['current_page']
    blogs = page.get_children_for_frontend().filter(tags__name__in=[category.name])

    paginator = Paginator(blogs, 8)
    page_index = request.GET.get('page')
    blogs = paginator.get_page(page_index)
    context['blogs'] = blogs
    
    context['category'] = category.name
    return render(request, 'blog-home.html', context)

def blog_index(request, *args, **kwargs):
    context = dict(kwargs)
    page = context['current_page']
    blogs = page.get_children_for_frontend()

    paginator = Paginator(blogs, 7)
    page = request.GET.get('page')
    blogs = paginator.get_page(page)
    context['blogs'] = blogs
    context['template_name'] = 'blog-home.html'

    return render(request, 'blog-home.html', context)