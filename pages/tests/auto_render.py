# -*- coding: utf-8 -*-
"""Auto render test suite"""
import django
from django.test import TestCase
from pages.http import auto_render, AutoRenderHttpError
from django.test.client import Client
from django.http import HttpResponse, HttpResponseRedirect

class AutoRenderTestCase(TestCase):
    """Auto render test suite class"""

    def test_13_auto_render(self):
        """
        Call an @auto_render decorated view with allowed keyword argument
        combinations.
        """
        @auto_render
        def testview(request, *args, **kwargs):
            assert 'only_context' not in kwargs
            assert 'template_name' not in kwargs
            return 'tests/auto_render.txt', locals()
        response = testview(None)
        self.assertEqual(response.__class__, HttpResponse)
        self.assertEqual(response.content,
                         "template_name: 'tests/auto_render.txt', "
                         "only_context: ''\n")
        self.assertEqual(testview(None, only_context=True),
                         {'args': (), 'request': None, 'kwargs': {}})
        response = testview(None, only_context=False)
        self.assertEqual(response.__class__, HttpResponse)
        self.assertEqual(response.content,
                         "template_name: 'tests/auto_render.txt', "
                         "only_context: ''\n")
        response = testview(None, template_name='tests/auto_render2.txt')
        self.assertEqual(response.__class__, HttpResponse)
        self.assertEqual(response.content,
                         "alternate template_name: 'tests/auto_render2.txt', "
                         "only_context: ''\n")

    def test_14_auto_render_httpresponse(self):
        """
        Call an @auto_render decorated view which returns an HttpResponse with
        allowed keyword argument combinations.
        """
        @auto_render
        def testview(request, *args, **kwargs):
            assert 'only_context' not in kwargs
            assert 'template_name' not in kwargs
            return HttpResponse(repr(sorted(locals().items())))
        response = testview(None)
        self.assertEqual(response.__class__, HttpResponse)
        self.assertEqual(response.content,
                         "[('args', ()), ('kwargs', {}), ('request', None)]")
        self.assertOnlyContextException(testview)
        self.assertEqual(testview(None, only_context=False).__class__,
                         HttpResponse)
        response = testview(None, template_name='tests/auto_render2.txt')
        self.assertEqual(response.__class__, HttpResponse)
        self.assertEqual(response.content,
                         "[('args', ()), ('kwargs', {}), ('request', None)]")

    def test_15_auto_render_redirect(self):
        """Call an @auto_render decorated view which returns an
        HttpResponseRedirect with allowed keyword argument combinations."""
        @auto_render
        def testview(request, *args, **kwargs):
            assert 'only_context' not in kwargs
            assert 'template_name' not in kwargs
            return HttpResponseRedirect(repr(sorted(locals().items())))
        response = testview(None)
        self.assertEqual(response.__class__, HttpResponseRedirect)
        self.assertOnlyContextException(testview)
        self.assertEqual(testview(None, only_context=False).__class__,
                         HttpResponseRedirect)
        response = testview(None, template_name='tests/auto_render2.txt')
        self.assertEqual(response.__class__, HttpResponseRedirect)

    def test_16_auto_render_any_httpresponse(self):
        """Call an @auto_render decorated view which returns an
        arbitrary HttpResponse subclass with allowed keyword argument
        combinations."""
        
        class MyResponse(HttpResponse): pass
        @auto_render
        def testview(request, *args, **kwargs):
            assert 'only_context' not in kwargs
            assert 'template_name' not in kwargs
            return MyResponse(repr(sorted(locals().items())))
        response = testview(None)
        self.assertEqual(response.__class__, MyResponse)
        self.assertOnlyContextException(testview)
        self.assertEqual(response.content,
                         "[('MyResponse', "
                         "<class 'pages.tests.auto_render.MyResponse'>), "
                         "('args', ()), ('kwargs', {}), ('request', None)]")
        self.assertEqual(testview(None, only_context=False).__class__,
                         MyResponse)
        response = testview(None, template_name='tests/auto_render2.txt')
        self.assertEqual(response.__class__, MyResponse)
        self.assertEqual(response.content,
                         "[('MyResponse', "
                         "<class 'pages.tests.auto_render.MyResponse'>), "
                         "('args', ()), ('kwargs', {}), ('request', None)]")

    def assertOnlyContextException(self, view):
        """If an @auto_render-decorated view returns an HttpResponse
        and is called with ``only_context=True``, it should raise an
        appropriate exception."""
        
        try:
            view(None, only_context=True)
        except Exception, e:
            self.assertTrue(isinstance(e, AutoRenderHttpError))
        else:
            assert False, 'Exception expected'
