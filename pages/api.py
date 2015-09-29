from pages.serializers import PageSerializer, ContentSerializer
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from pages.models import Page, Content


class PageList(generics.ListCreateAPIView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (IsAdminUser,)
    paginate_by = 100


class PageEdit(generics.RetrieveUpdateDestroyAPIView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = (IsAdminUser,)
    paginate_by = 100


class ContentList(generics.ListCreateAPIView):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = (IsAdminUser,)
    paginate_by = 200


class ContentEdit(generics.RetrieveUpdateDestroyAPIView):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = (IsAdminUser,)
    paginate_by = 200

