#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import os


from django.conf import settings
from django.conf.urls import url
from django.http import HttpResponse
from django.views import View


import settings as app_settings

class RedisSessionsView(View):
    def get(self, request):
        return HttpResponse('Home')


urlpatterns = [
    url(r'^$', RedisSessionsView.as_view()),
]


from django.core.wsgi import get_wsgi_application
def return_application():
    return get_wsgi_application()

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
else:
    return_application()