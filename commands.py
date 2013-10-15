# coding: utf-8

from flask.ext.script import Command, Option
from .models import Fundraising


class ListFundraising(Command):
    "prints a list of fundraisings"

    command_name = 'list_fundraisings'

    option_list = (
        Option('--title', '-t', dest='title'),
    )

    def run(self, title=None):

        fundraisings = Fundraising.objects
        if title:
            fundraisings = fundraisings(title=title)

        for fundraising in fundraisings:
            print(fundraising)