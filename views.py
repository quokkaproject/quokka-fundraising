#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask.views import MethodView
from quokka.core.templates import render_template

from .models import Campaign

import logging
logger = logging.getLogger()


class ListView(MethodView):

    def get(self):
        logger.info('getting list of campaign')
        campaigns = Campaign.objects.all()
        return render_template(['fundraising/list.html'], campaigns=campaigns)


class DetailView(MethodView):

    def get_context(self, slug):
        campaign = Campaign.objects.get_or_404(slug=slug)

        context = {
            "campaign": campaign
        }
        return context

    def get(self, slug):
        context = self.get_context(slug)
        return render_template('fundraising/detail.html', **context)
