#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request
from flask.views import MethodView
from quokka.core.templates import render_template

from .models import Fundraising

import logging
logger = logging.getLogger()


class ListView(MethodView):

    def get(self):
        logger.info('getting list of fundraising')
        fundraisings = Fundraising.objects.all()
        return render_template('fundraising/list.html', fundraisings=fundraisings)


class DetailView(MethodView):

    def get_context(self, slug):
        fundraising = Fundraising.objects.get_or_404(slug=slug)

        context = {
            "fundraising": fundraising
        }
        return context

    def get(self, slug):
        context = self.get_context(slug)
        return render_template('fundraisings/detail.html', **context)
        