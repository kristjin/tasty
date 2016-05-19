
activate_this = '/var/www/tasty/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys

sys.path.insert(0, "/var/www/tasty")

from tasty import app as application
