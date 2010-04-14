from django.template import Library, Node, TemplateSyntaxError
from simplemenu.models import MenuItem

register = Library()

class SimplemenuNode(Node):
    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        context[self.varname] = MenuItem.objects.all()
        return ''

@register.tag
def get_simplemenu(parser, token):
    """
    Loads all ``simplemenu.models.MenuItems`` and stores them in a
    context variable.

    Usage::

        {% get_simplemenu as [varname] %}

    Example::

        {% get_simplemenu as menu_items %}
        {% for item in menu_items %}
          <a href="{{ item.page.url }}">{{ item.name }}</a>
        {% endfor %}

    """
    bits = token.split_contents()
    if len(bits) != 3 or bits[1] != 'as':
        raise TemplateSyntaxError("Incorrect tag arguments. "
                                  "Usage: %s as varname" % bits[0])
    return SimplemenuNode(bits[2])
