from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from simplemenu.pages import PageWrapper

class MenuItem(models.Model):
    """
    A menu item.

    Each item is represented by caption ``name`` and a page it links
    to. Page could be any model with get_absolute_url method or a
    string (url, reversible name of the view).

    Use ``get_absolute_url()`` or ``page.url()`` to get url of the
    page.

    All items in the menu are ordered by ``rank``.
    """
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
        """
        Save model to a database and generate value for self.rank if
        it's not set.
        """
        if self.rank is None:
            try:
                self.rank = MenuItem.objects.reverse()[0].rank + 1
            except(IndexError):
                self.rank = 0
        super(MenuItem, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return self.get_page().url()

    def get_page(self):
        """
        Getter for ``MenuItem.page`` property. Returns
        ``simplemenu.pages.PageWrapper``.
        """
        return PageWrapper(self.urlstr or self.urlobj)

    def set_page(self, urlobj_or_str):
        """
        Setter for ``MenuItem.page`` property. Sets values for
        ``self.urlobj`` and ``self.urlstr``.

        ``urlobj_or_str`` could be instance of any model or string:
        url, reversible name of the view function.
        """
        p = urlobj_or_str
        if not isinstance(urlobj_or_str, PageWrapper):
            p = PageWrapper(urlobj_or_str)
        self.urlobj = p.urlobj
        self.urlstr = p.urlstr

    page = property(get_page, set_page)

    def is_first(self):
        """
        Returns ``True`` if item is the first one in the menu.
        """
        return MenuItem.objects.filter(rank__lt=self.rank).count() == 0

    def is_last(self):
        """
        Returns ``True`` if item is the last one in the menu.
        """
        return MenuItem.objects.filter(rank__gt=self.rank).count() == 0

    def increase_rank(self):
        """
        Changes position of this item with the next item in the
        menu. Does nothing if this item is the last one.
        """
        try:
            next_item = MenuItem.objects.filter(rank__gt=self.rank)[0]
        except IndexError:
            pass
        else:
            self.swap_ranks(next_item)

    def decrease_rank(self):
        """
        Changes position of this item with the previous item in the
        menu. Does nothing if this item is the first one.
        """
        try:
            prev_item = MenuItem.objects.filter(rank__lt=self.rank).reverse()[0]
        except IndexError:
            pass
        else:
            self.swap_ranks(prev_item)

    def swap_ranks(self, other):
        """
        Swap positions with ``other`` menu item.
        """
        maxrank = MenuItem.objects.reverse()[0].rank + 1
        prev_rank, self.rank = self.rank, maxrank
        self.save()
        self.rank, other.rank = other.rank, prev_rank
        other.save()
        self.save()
