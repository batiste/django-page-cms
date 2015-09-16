from pages.serializers import PageSerializer
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from pages.models import Page


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
