# coding: utf-8

from flask.ext.script import Command, Option
from .models import Campaign


class ListCampaign(Command):
    "prints a list of campaigns"

    command_name = 'list_campaigns'

    option_list = (
        Option('--title', '-t', dest='title'),
    )

    def run(self, title=None):

        campaigns = Campaign.objects
        if title:
            campaigns = campaigns(title=title)

        for campaign in campaigns:
            print(campaign)  # noqa
