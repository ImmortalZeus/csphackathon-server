"""
WSGI config for server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

import socketio

from mainpage.views import sio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

django_app = get_wsgi_application()
application = socketio.WSGIApp(sio, django_app)

import eventlet
import eventlet.wsgi
from django.core.management.commands.runserver import Command as runserver
addr = runserver.default_addr
try:
    addr = (sys.argv[2].split(":"))[0]
except:
    addr = runserver.default_addr
eventlet.wsgi.server(eventlet.listen((addr, 80)), application)

# application = get_wsgi_application()
