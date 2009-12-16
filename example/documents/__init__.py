from pages.urlconf_registry import register_urlconf

try:
    register_urlconf('Documents', 'example.documents.urls',
        label='Display documents')
except:
    pass