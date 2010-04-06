from django import forms

from simplemenu.models import MenuItem
from simplemenu.pages import get_registered_pages

class MenuItemForm(forms.ModelForm):
    page = forms.ChoiceField()

    class Meta:
        model = MenuItem
        fields = ('name',)

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=forms.util.ErrorList,
                 label_suffix=':', empty_permitted=False, instance=None):
        if instance:
            if not initial:
                initial = {}
            initial['page'] = instance.page.strkey()
        super(MenuItemForm, self).__init__(data, files, auto_id, prefix,
                                           initial, error_class, label_suffix,
                                           empty_permitted, instance)
        self._registered_pages_cache = get_registered_pages()
        self.fields['page'].choices = self.page_choices()

    def page_choices(self):
        choices = []
        for p in self._registered_pages_cache:
            choices.append((p.strkey(), p.name()))
        choices.sort(key=lambda x: x[1])
        return choices

    def selected_page(self):
        key = self.cleaned_data['page']
        for p in self._registered_pages_cache:
            if p.strkey() == key:
                return p
        return None

