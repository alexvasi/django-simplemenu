import copy
import types

from django.core.urlresolvers import reverse
from django.db.models.query import QuerySet

registry = []

def register(*args):
    registry.extend(args)

class PageWrapper(object):
    def __init__(self, urlobj_or_str):
        if isinstance(urlobj_or_str, types.StringTypes):
            self.urlobj = None
            self.urlstr = urlobj_or_str
        else:
            self.urlobj = urlobj_or_str
            self.urlstr = str()

    def name(self):
        if self.urlobj:
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
        if self.urlobj:
            return "%s.%s.pk%s" % (self.urlobj.__module__,
                                   self.urlobj.__class__.__name__,
                                   self.urlobj.id)
        else:
            return self.urlstr

def get_registered_pages():
    pages = []
    for reg in map(copy.deepcopy, registry):
        if isinstance(reg, QuerySet):
            # evaluating QuerySet objects by iteration
            pages.extend(map(PageWrapper, reg))
        else:
            pages.append(PageWrapper(reg))
    return pages
