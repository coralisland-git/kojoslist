# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class GeneralConfig(AppConfig):
    name = 'general'

    def ready(self):
        import general.signals
       