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
    bits = token.split_contents()
    if len(bits) != 3 or bits[1] != 'as':
        raise TemplateSyntaxError("Incorrect tag arguments. "
                                  "Usage: %s as varname" % bits[0])
    return SimplemenuNode(bits[2])
