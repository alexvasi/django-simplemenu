from django import forms
from django.conf import settings
from django.conf.urls.defaults import patterns
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404

from simplemenu.models import MenuItem
from simplemenu.forms import MenuItemForm

class MenuItemAdmin(admin.ModelAdmin):
    form = MenuItemForm
    list_display = ('item_name', 'move', 'page')

    def save_model(self, request, obj, form, change):
        obj.page = form.selected_page()
        obj.save()

    def item_name(self, obj):
        # just to forbid to sort by name
        return obj.name

    def page(self, obj):
        return obj.page.name()

    def move(sefl, obj):
        button = '<a href="%s"><img src="%simg/admin/arrow-%s.gif" /> %s</a>'
        prefix = settings.ADMIN_MEDIA_PREFIX
        
        link = '%d/move_up/' % obj.pk
        html = button % (link, prefix, 'up', 'up') + " | "
        link = '%d/move_down/' % obj.pk
        html += button % (link, prefix, 'down', 'down')
        return html
    move.allow_tags = True

    def get_urls(self):
        urls = patterns('',
            (r'^(?P<item_pk>\d+)/move_up/$', self.admin_site.admin_view(self.move_up)),
            (r'^(?P<item_pk>\d+)/move_down/$', self.admin_site.admin_view(self.move_down)),
        )
        return urls + super(MenuItemAdmin, self).get_urls()

    def move_up(self, request, item_pk):
        if self.has_change_permission(request):
            item = get_object_or_404(MenuItem, pk=item_pk)
            item.decrease_rank()
        else:
            raise PermissionDenied
        return redirect('admin:simplemenu_menuitem_changelist')

    def move_down(self, request, item_pk):
        if self.has_change_permission(request):
            item = get_object_or_404(MenuItem, pk=item_pk)
            item.increase_rank()
        else:
            raise PermissionDenied
        return redirect('admin:simplemenu_menuitem_changelist')

admin.site.register(MenuItem, MenuItemAdmin)
