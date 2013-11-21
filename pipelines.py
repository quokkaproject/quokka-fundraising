# coding: utf-8

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
