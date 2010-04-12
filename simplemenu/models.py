from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from simplemenu.pages import PageWrapper

class MenuItem(models.Model):
    name = models.CharField(_('Caption'), max_length=64)
    rank = models.SmallIntegerField(unique=True, db_index=True)

    urlobj_content_type = models.ForeignKey(ContentType, null=True)
    urlobj_id = models.PositiveIntegerField(null=True)
    urlobj = generic.GenericForeignKey('urlobj_content_type', 'urlobj_id')
    urlstr = models.CharField(max_length=255)

    class Meta:
        ordering = ['rank']
        verbose_name = _('menu item')
        verbose_name_plural = _('menu items')
    
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
        return self.get_page().url()

    def get_page(self):
        return PageWrapper(self.urlstr or self.urlobj)

    def set_page(self, urlobj_or_str):
        p = urlobj_or_str
        if not isinstance(urlobj_or_str, PageWrapper):
            p = PageWrapper(urlobj_or_str)
        self.urlobj = p.urlobj
        self.urlstr = p.urlstr

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
