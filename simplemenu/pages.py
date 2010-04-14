import copy
import types

from django.core.urlresolvers import reverse
from django.db.models.query import QuerySet

registry = []

def register(*args):
    """
    Register urls, views, model instances and QuerySets to be potential
    pages for menu items.
    
    Example::

        import simplemenu
        simplemenu.register(
            '/some/url/',
            'package.module.view',
            ('/some_url_or_view_with_name/', 'name'),
            FlatPage.objects.all(),
            Products.objects.get(pk=1),
        )
    """
    registry.extend(args)

class PageWrapper(object):
    """
    A helper-object to wrap the pages, which might be django models or
    strings.
    """
    def __init__(self, urlobj_or_str, name=None):
        if isinstance(urlobj_or_str, types.StringTypes):
            self.urlobj = None
            self.urlstr = urlobj_or_str
        else:
            self.urlobj = urlobj_or_str
            self.urlstr = str()
        self._name = name

    def name(self):
        if self._name:
            name = self._name
        elif self.urlobj:
            name = unicode(self.urlobj)
        elif "/" in self.urlstr:
            name = self.urlstr
        else:
            name = self.urlstr.rsplit('.', 1)[-1]
            name = name.replace("_", " ").capitalize()
        return name

    def url(self):
        if self.urlobj:
            url = self.urlobj.get_absolute_url()
        elif "/" in self.urlstr:
            url = self.urlstr
        else:
            url = reverse(self.urlstr)
        return url

    def strkey(self):
        """
        Generates somewhat unique string id of the wrappee.
        """
        if self.urlobj:
            return "%s.%s.pk%s" % (self.urlobj.__module__,
                                   self.urlobj.__class__.__name__,
                                   self.urlobj.id)
        else:
            return self.urlstr

def get_registered_pages():
    """
    Returns all registered pages wrapped in PageWrapper helper-object
    evaluating all QuerySets along the way.
    """
    pages = []
    for reg in map(copy.deepcopy, registry):
        if isinstance(reg, QuerySet):
            # evaluating QuerySet objects by iteration
            pages.extend(map(PageWrapper, reg))
        else:
            name = None
            if isinstance(reg, types.TupleType):
                reg, name = reg
            pages.append(PageWrapper(reg, name))
    return pages
