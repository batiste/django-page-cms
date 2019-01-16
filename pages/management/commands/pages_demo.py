from django.core.management.base import BaseCommand, CommandError
from pages.models import Page
from pages.tests.testcase import new_page
from django.contrib.auth import get_user_model


lorem = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
Quisque tempus tellus enim, quis tempus dui pretium non. 
Cras eget enim vel magna fringilla cursus ut sit amet mi. 
Curabitur id pharetra turpis. Pellentesque quis eros nunc. 
Etiam interdum nisi ut sapien facilisis ornare. Mauris in tellus elit. 
Integer vulputate venenatis odio. Vivamus in diam vitae magna gravida 
sodales sit amet id ex. Aliquam commodo massa at mollis blandit. 
Donec auctor sapien et risus gravida, ultrices imperdiet est laoreet."""


class Command(BaseCommand):
    help = 'Create a couple of dummy pages for a demo'

    def handle(self, *args, **options):

        UserModel = get_user_model()
        if UserModel.objects.count() == 0:
            UserModel.objects.create(username='demo', password='demo')

        new_page(content={
            'title': 'Home', 'slug': 'home', 'lead': 'Welcome to the Gerbi CMS', 'content': lorem
        }, template='index.html')
        prod_page = new_page(content={
            'title': 'Products', 'slug': 'products', 'lead': 'Our products', 'content': lorem
        }, template='index.html')
        new_page(content={
            'title': 'Poney', 'slug': 'poney', 'lead': 'Our shiny poney', 'content': lorem},
            parent=prod_page,
            template='index.html')
        new_page(content={
            'title': 'Hat', 'slug': 'hat', 'lead': 'Fedora for elegance', 'content': lorem},
            parent=prod_page,
            template='index.html')
        blog = new_page(content={
            'title': 'Blog', 'slug': 'blog', 'lead': 'Blog example', 'content': lorem},
            template='blog-home.html', delegate_to='blog')
        new_page(content={
            'title': 'Blog post 1', 'slug': 'blog-post-1', 'lead': 'Blog post example', 'content': lorem},
            parent=blog,
            template='blog-post.html')
        new_page(content={
            'title': 'Blog post 2', 'slug': 'blog-post-2', 'lead': 'Blog post example', 'content': lorem},
            parent=blog,
            template='blog-post.html')
        new_page(content={
            'title': 'Blog post 3', 'slug': 'blog-post-3', 'lead': 'Blog post example', 'content': lorem},
            parent=blog,
            template='blog-post.html')
        new_page(content={
            'title': 'Blog post 4', 'slug': 'blog-post-4', 'lead': 'Blog post example', 'content': lorem},
            parent=blog,
            template='blog-post.html')
        new_page(content={
            'title': 'Contact', 'slug': 'contact', 
            'lead': 'Contact us at gerbi@example.com', 'content':lorem
        }, template='index.html')
        
