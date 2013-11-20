# coding: utf-8

from quokka.core.app import QuokkaModule
from .functions import get_random_campaign
module = QuokkaModule("fundraising", __name__, template_folder="templates")

module.add_app_template_global(get_random_campaign)

# Register the urls if needed
from .views import ListView, DetailView
module.add_url_rule('/fundraising/',
                    view_func=ListView.as_view('list'))
module.add_url_rule('/fundraising/<slug>/',
                    view_func=DetailView.as_view('detail'))
