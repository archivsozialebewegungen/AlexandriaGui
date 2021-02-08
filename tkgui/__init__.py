import gettext
import os
import sys


packagedir = os.path.abspath(os.path.dirname(__file__))
localedir = os.path.join(packagedir, 'locale')
translate = gettext.translation('tkgui', localedir, fallback=True)
_ = translate.gettext
