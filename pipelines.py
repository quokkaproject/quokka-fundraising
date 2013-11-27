# coding: utf-8

from flask import request
from quokka.modules.cart.pipelines.base import CartPipeline
from quokka.utils import get_current_user
from .models import Donation


class SetDonor(CartPipeline):
    def process(self):

        donations = Donation.objects.filter(
            cart=self.cart
        )

        user = get_current_user()
        for donation in donations:
            donation.donor = user
            donation.save()

        self.cart.sender_data = {
            "name": user.name,
            "email": user.email,
        }

        self.cart.addlog("SetDonor Pipeline: defined sender data")

        return self.go()


class CompleteInformation(CartPipeline):
    def process(self):
        user = get_current_user()
        confirm = request.form.get("fundraising_complete_information_confirm")
        if not confirm:
            return self.render('fundraising/complete_information.html')

        display_name = request.form.get('display_name', user.name)
        published = request.form.get('published', True)
        donation_to_project = request.form.get('donation_to_project')

        donations = Donation.objects.filter(
            cart=self.cart
        )

        for donation in donations:
            donation.published = (published == u'on')
            donation.display_name = display_name
            donation.save()

        if donation_to_project:
            donation.set_project_campaign(donation_to_project)

        self.cart.addlog("CompleteInformation Pipeline")
        return self.go()


