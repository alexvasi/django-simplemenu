import types

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models

from simplemenu.pages import PageWrapper

class MenuItem(models.Model):
    name = models.CharField(max_length=64)
    rank = models.SmallIntegerField(unique=True)

    urlobj_content_type = models.ForeignKey(ContentType, null=True)
    urlobj_id = models.PositiveIntegerField(null=True)
    urlobj = generic.GenericForeignKey('urlobj_content_type', 'urlobj_id')
    urlstr = models.CharField(max_length=255)

    class Meta:
        ordering = ['rank']
    
    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.rank is None:
            try:
                self.rank = MenuItem.objects.reverse()[0].rank + 1
            except(IndexError):
                self.rank = 0
        super(MenuItem, self).save(*args, **kwargs)

    def get_absolute_url(self):
        if self.urlobj:
            return self.urlobj.get_absolute_url()
        elif "/" in self.urlstr:
            return self.urlstr
        else:
            return reverse(self.urlstr)

    def get_page(self):
        p = self.urlobj if self.urlobj else self.urlstr
        return PageWrapper(p)

    def set_page(self, urlobj_or_str):
        if isinstance(urlobj_or_str, PageWrapper):
            urlobj_or_str = urlobj_or_str.wrappee
        
        if isinstance(urlobj_or_str, types.StringTypes):
            self.urlobj = None
            self.urlstr = urlobj_or_str
        else:
            self.urlobj = urlobj_or_str
            self.urlstr = str()

    page = property(get_page, set_page)

    def is_first(self):
        return MenuItem.objects.filter(rank__lt=self.rank).count() == 0

    def is_last(self):
        return MenuItem.objects.filter(rank__gt=self.rank).count() == 0

    def increase_rank(self):
        try:
            next_item = MenuItem.objects.filter(rank__gt=self.rank)[0]
        except IndexError:
            pass
        else:
            self.swap_ranks(next_item)

    def decrease_rank(self):
        try:
            prev_item = MenuItem.objects.filter(rank__lt=self.rank).reverse()[0]
        except IndexError:
            pass
        else:
            self.swap_ranks(prev_item)

    def swap_ranks(self, other):
        maxrank = MenuItem.objects.reverse()[0].rank + 1
        prev_rank, self.rank = self.rank, maxrank
        self.save()
        self.rank, other.rank = other.rank, prev_rank
        other.save()
        self.save()
