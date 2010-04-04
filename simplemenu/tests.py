from django.conf.urls.defaults import patterns, url
from django.test import TestCase

from simplemenu import pages
from simplemenu.models import MenuItem

# test urls
urlpatterns = patterns('',
    (r'^test/view/$', 'simplemenu.tests.phony_view'),
    url(r'^test/named/view/$', 'simplemenu.tests.phony_view2',
        name='named_view')
)

def phony_view(request):
    pass

def phony_view2(request):
    pass

class RegistryTests(TestCase):
    urls = 'simplemenu.tests'
    
    def setUp(self):
        pages.registry = []

    def _test_url(self, url):
        pages.register(url)
        p = pages.get_registered_pages()
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0].name(), url)
        self.assertEqual(p[0].url(), url)
        self.assertEqual(p[0].strkey(), url)

    def test_url(self):
        self._test_url('/url/to/page/')

    def test_full_url(self):
        self._test_url('http://site.com/url/to/page/')

    def test_root_url(self):
        self._test_url('/')

    def test_view(self):
        pages.register('simplemenu.tests.phony_view')
        p = pages.get_registered_pages()
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0].name(), 'Phony view')
        self.assertEqual(p[0].url(), '/test/view/')
        self.assertEqual(p[0].strkey(), 'simplemenu.tests.phony_view')

    def test_named_view(self):
        pages.register('named_view')
        p = pages.get_registered_pages()
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0].name(), 'Named view')
        self.assertEqual(p[0].url(), '/test/named/view/')
        self.assertEqual(p[0].strkey(), 'named_view')

    def test_empty_queryset(self):
        pages.register(MenuItem.objects.all())
        self.failIf(pages.get_registered_pages())

    def test_queryset_of_one_object(self):
        MenuItem(name='item1', urlstr='/item1/').save()
        pages.register(MenuItem.objects.all())
        p = pages.get_registered_pages()
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0].name(), 'item1')
        self.assertEqual(p[0].url(), '/item1/')
        self.assert_(p[0].strkey().endswith('simplemenu.models.MenuItem.pk1'))

    def test_queryset(self):
        MenuItem(name='item1', urlstr='/item1/').save()
        MenuItem(name='item2', urlstr='/item2/').save()
        pages.register(MenuItem.objects.all())
        p = pages.get_registered_pages()
        self.assertEqual(len(p), 2)
        self.assertEqual(p[0].name(), 'item1')
        self.assertEqual(p[0].url(), '/item1/')
        self.assert_(p[0].strkey().endswith('simplemenu.models.MenuItem.pk1'))
        self.assertEqual(p[1].name(), 'item2')
        self.assertEqual(p[1].url(), '/item2/')
        self.assert_(p[1].strkey().endswith('simplemenu.models.MenuItem.pk2'))
