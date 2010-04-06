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

    def test_named_items(self):
        pages.register('/url/',
                       ('/url/', 'Url name'),
                       'simplemenu.tests.phony_view',
                       ('simplemenu.tests.phony_view', 'PHONY NAME'))
        p = pages.get_registered_pages()
        self.assertEqual(len(p), 4)
        self.assertEqual(p[0].name(), '/url/')
        self.assertEqual(p[1].name(), 'Url name')
        self.assertEqual(p[2].name(), 'Phony view')
        self.assertEqual(p[3].name(), 'PHONY NAME')

class MenuItemTests(TestCase):
    def test_get_absolute_url(self):
        item1 = MenuItem(name='item1', urlstr='/item1/')
        self.assertEqual(item1.get_absolute_url(), '/item1/')
        item1.save()
        item2 = MenuItem(urlobj=item1)
        self.assertEqual(item2.get_absolute_url(), '/item1/')

    def test_pages(self):
        item = MenuItem(urlstr='/url/')
        self.assertEqual(item.page.urlstr, '/url/')
        self.assertEqual(item.page.urlobj, None)

        foo = MenuItem(name='foo', urlstr='/foo/')
        item.page = foo
        self.assertEqual(item.urlstr, '')
        self.assertEqual(item.urlobj, foo)

    def test_creating_and_rank(self):
        item1 = MenuItem(name='1', urlstr='/1/')
        item1.save()
        self.assertEqual(item1.rank, 0)
        self.assert_(item1.is_first())
        self.assert_(item1.is_last())

        item2 = MenuItem(name='2', urlstr='/2/')
        item2.save()
        self.assertEqual(item2.rank, 1)
        self.failIf(item2.is_first())
        self.assert_(item2.is_last())
        self.failIf(item1.is_last())
        self.assert_(item1.is_first())

        item3 = MenuItem(name='3', urlstr='/3/')
        item3.save()
        self.assertEqual(item3.rank, 2)
        self.failIf(item2.is_first())
        self.failIf(item2.is_last())

    def test_phony_changing_rank(self):
        item_a = MenuItem(name='a', urlstr='/a/')
        item_a.save()
        self.assertEqual(item_a.rank, 0)
        item_a.increase_rank()
        self.assertEqual(item_a.rank, 0)
        item_a = MenuItem.objects.get(id=item_a.id)
        self.assertEqual(item_a.rank, 0)
        item_a.decrease_rank()
        self.assertEqual(item_a.rank, 0)

    def test_changing_rank(self):
        item_a = MenuItem(name='a', urlstr='/a/')
        item_a.save()
        item_b = MenuItem(name='b', urlstr='/b/')
        item_b.save()
        item_c = MenuItem(name='c', urlstr='/c/')
        item_c.save()
        self.assertEqual(item_a.rank, 0)
        self.assertEqual(item_b.rank, 1)
        self.assertEqual(item_c.rank, 2)

        item_a.increase_rank()
        item_a.increase_rank()
        item_a = MenuItem.objects.get(id=item_a.id)
        item_b = MenuItem.objects.get(id=item_b.id)
        item_c = MenuItem.objects.get(id=item_c.id)
        self.assertEqual(item_b.rank, 0)
        self.assertEqual(item_c.rank, 1)
        self.assertEqual(item_a.rank, 2)

        item_c.decrease_rank()
        item_a = MenuItem.objects.get(id=item_a.id)
        item_b = MenuItem.objects.get(id=item_b.id)
        item_c = MenuItem.objects.get(id=item_c.id)
        self.assertEqual(item_c.rank, 0)
        self.assertEqual(item_b.rank, 1)
        self.assertEqual(item_a.rank, 2)

    def test_changing_rank_after_deletion(self):
        item_a = MenuItem(name='a', urlstr='/a/')
        item_a.save()
        item_b = MenuItem(name='b', urlstr='/b/')
        item_b.save()
        item_c = MenuItem(name='c', urlstr='/c/')
        item_c.save()

        item_b.delete()
        item_c.decrease_rank()
        item_a = MenuItem.objects.get(id=item_a.id)
        item_c = MenuItem.objects.get(id=item_c.id)
        self.assertEqual(item_c.rank, 0)
        self.assertEqual(item_a.rank, 2)

        item_c.increase_rank()
        item_a = MenuItem.objects.get(id=item_a.id)
        item_c = MenuItem.objects.get(id=item_c.id)
        self.assertEqual(item_a.rank, 0)
        self.assertEqual(item_c.rank, 2)
