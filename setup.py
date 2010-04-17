from distutils.core import setup
import simplemenu

setup(name='django-simplemenu',
      version=simplemenu.__version__,
      url='http://github.com/alexvasi/django-simplemenu',
      license='BSD',
      description='Menu app for Django with ordering and ability to link menu item with model instance, view or URL.',
      author='Alex Vasi',
      author_email='eee@someuser.com',
      packages=['simplemenu'])
