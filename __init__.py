# coding: utf-8

from quokka.core.app import QuokkaModule
from .views import DonationView
from .functions import get_random_campaign

module = QuokkaModule("fundraising", __name__, template_folder="templates")

module.add_app_template_global(get_random_campaign)

module.add_url_rule('/fundraising/donate/',
                    view_func=DonationView.as_view('donate'))
