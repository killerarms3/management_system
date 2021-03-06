"""
WSGI config for management_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/home/jackyhsu/management_system_env/lib/python3.6/site-packages')

# Add the app's directory to the PYTHONAPTH
sys.path.append('/home/jackyhsu/management_system')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management_system.settings')

# Activate virtual env
activate_env=os.path.expanduser("/home/jackyhsu/management_system_env/bin/activate_this.py")
exec(compile(open(activate_env, "rb").read(), activate_env, 'exec'), dict(__file__=activate_env))
application = get_wsgi_application()