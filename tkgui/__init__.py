import gettext
import os
import sys

def get_locale_dir():
    this_module = get_locale_dir.__module__
    this_file = os.path.abspath(sys.modules[this_module].__file__)
    this_directory = os.path.dirname(this_file)
    return os.path.join(this_directory, 'locale')

gettext.install('alexandriagui', get_locale_dir())