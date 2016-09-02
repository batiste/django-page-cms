from django.core.management.base import BaseCommand, CommandError
from pages.models import Page
from pages.tests.testcase import new_page
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create a couple of dummy pages for a demo'

    def handle(self, *args, **options):

        UserModel = get_user_model()
        if UserModel.objects.count() == 0:
            UserModel.objects.create(username='demo', password='demo')

        new_page(content={
            'title': 'Home', 'slug': 'home', 'lead': 'Welcome to the Gerbi CMS'
        }, template='index.html')
        prod_page = new_page(content={
            'title': 'Products', 'slug': 'products', 'lead': 'Our products'
        }, template='index.html')
        new_page(content={
            'title': 'Poney', 'slug': 'poney', 'lead': 'Our shiny poney'},
            parent=prod_page,
            template='index.html')
        new_page(content={
            'title': 'Hat', 'slug': 'hat', 'lead': 'Fedora for elegance'},
            parent=prod_page,
            template='index.html')
        new_page(content={
            'title': 'Contact', 'slug': 'products', 'lead': 'Contact us at gerbi@example.com'
        }, template='index.html')
        
