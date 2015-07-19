from pages.models import Page, Content
from rest_framework import serializers

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content

class PageSerializer(serializers.ModelSerializer):
    content_set = ContentSerializer(many=True)

    class Meta:
        model = Page