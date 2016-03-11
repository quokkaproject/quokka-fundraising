# coding: utf-8

import logging

from flask.ext.script import Command, Option
from .models import Campaign

logger = logging.getLogger(__name__)


class ListCampaign(Command):
    '''prints a list of campaigns'''

    command_name = 'list_campaigns'

    option_list = (
        Option('--title', '-t', dest='title'),
    )

    def run(self, title=None):

        campaigns = Campaign.objects
        if title:
            campaigns = campaigns(title=title)

        for campaign in campaigns:
            logger.info('Campaign: {}'.format(campaign))
