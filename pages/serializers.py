from pages.models import Page, Content
from rest_framework import serializers
from django.contrib.auth import get_user_model
from pages import settings
from django.contrib.sites.models import Site


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'


class PageSerializer(serializers.ModelSerializer):
    content_set = ContentSerializer(many=True, read_only=True)
    creation_date = serializers.DateTimeField()
    uuid = serializers.UUIDField()

    class Meta:
        model = Page
        fields = '__all__'

    def create(self, validated_data):

        attributes = (
            'status', 'delegate_to', 'freeze_date', 'creation_date',
            'publication_end_date', 'template', 'redirect_to_url',
            'last_modification_date', 'publication_date', 'uuid')

        admin = get_user_model().objects.filter(is_superuser=True)[0]

        cleaned_data = {}
        for attribute in attributes:
            cleaned_data[attribute] = validated_data.get(attribute)

        if validated_data.get('parent', False):
            cleaned_data['parent'] = validated_data.get('parent')

        cleaned_data['author'] = admin

        page = Page.objects.create(**cleaned_data)
        if settings.PAGE_USE_SITE_ID:
            site = Site.objects.get_current()
            page.sites.add(site)

        page.invalidate()
        return page
