import copy
import types

from django.core.urlresolvers import reverse
from django.db.models.query import QuerySet

registry = []

def register(*args):
    registry.extend(args)

class PageWrapper(object):
    def __init__(self, obj):
        self.wrappee = obj

    def name(self):
        if isinstance(self.wrappee, types.StringTypes):
            if "/" in self.wrappee:
                name = self.wrappee
            else:
                name = self.wrappee.rsplit('.', 1)[-1]
                name = name.replace("_", " ").capitalize()
        else:
            name = unicode(self.wrappee)
        return name

    def url(self):
        if isinstance(self.wrappee, types.StringTypes):
            if "/" in self.wrappee:
                url = self.wrappee
            else:
                url = reverse(self.wrappee)
        else:
            url = self.wrappee.get_absolute_url()
        return url

    def strkey(self):
        if isinstance(self.wrappee, types.StringTypes):
            return self.wrappee
        else:
            return "%s.%s.pk%s" % (self.wrappee.__module__,
                                   self.wrappee.__class__.__name__,
                                   self.wrappee.id)

def get_registered_pages():
    pages = []
    for reg in map(copy.deepcopy, registry):
        if isinstance(reg, QuerySet):
            # evaluating QuerySet objects by iteration
            pages.extend(map(PageWrapper, reg))
        else:
            pages.append(PageWrapper(reg))
    return pages
