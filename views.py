# coding: utf-8
from flask import request, redirect, url_for, current_app
from flask.views import MethodView
from quokka.utils import get_current_user
from quokka.modules.cart.models import Cart, Item
from quokka.core.templates import render_template
from quokka.core.models import Channel

from .models import Donation, Campaign, Values


class TransactionListView(MethodView):
    def get(self):
        context = {}

        donations = Donation.objects(
            status='confirmed'
        ).order_by('confirmed_date')

        if not donations:
            return render_template('fundraising/transaction_empty.html')

        context['donations'] = donations

        context['total'] = donations.sum('total')
        context['taxes'] = donations.sum('tax')
        context['balance'] = context['total'] - context['taxes']

        collection = Donation._get_collection()

        aggregated = collection.aggregate([
            {"$match": {"status": 'confirmed'}},
            {
                "$group": {
                    "_id": "$payment_method",
                    "total": {"$sum": "$total"},
                    "taxes": {"$sum": "$tax"},
                    "count": {"$sum": 1}
                }
            }
        ])

        context['aggregated'] = aggregated.get('result')
        context['campaigns'] = Campaign.objects().order_by('title')

        base_channel = current_app.config.get(
            'FUNDRAISING_BASE_CHANNEL', 'home'
        )
        campaign_collection = Campaign._get_collection()
        aggregate_by_channel = campaign_collection.aggregate([
            {"$match": {"mpath": {"$regex": "^,{0}".format(base_channel)}}},
            {
                "$group": {
                    "_id": "$channel",
                    "total": {"$sum": "$balance"},
                    "count": {"$sum": 1}
                }
            }
        ])
        context['aggregate_by_channel'] = aggregate_by_channel.get('result')
        for item in context['aggregate_by_channel']:
            item['channel'] = Channel.objects.get(id=item['_id'])

        project_donation_slugs = current_app.config.get(
            'FUNDRAISING_TRANSACTION_EXTRA', ['project-campaign']
        )
        if project_donation_slugs:
            for project_donation_slug in project_donation_slugs:
                try:
                    project_donation = Campaign.objects.get(
                        slug=project_donation_slug
                    )
                    context['aggregate_by_channel'].append(
                        {
                            "total": project_donation.balance,
                            "count": len(project_donation.donations or []),
                            "channel": project_donation.channel
                        }
                    )
                except Campaign.DoesNotExist:
                    pass

        return render_template('fundraising/transaction_list.html', **context)


class DonationView(MethodView):
    def post(self):
        campaign_id = request.form.get('campaign_id')
        value = request.form.get('value')
        if not value:
            return redirect(url_for('list'))
        self.current_user = get_current_user()
        self.cart = Cart.get_cart()

        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            self.cart.addlog("Error getting campaign %s" % campaign_id)
            return render_template('fundraising/donation_error.html')

        donation = None
        if hasattr(self.cart, 'fundraising_donation_id'):
            try:
                donation = Donation.objects.get(
                    id=self.cart.fundraising_donation_id
                )
            except Donation.DoesNotExist:
                donation = None

        if not donation:
            donation = Donation(
                donor=self.current_user,
                cart=self.cart
            )
            donation.save()
            self.cart.fundraising_donation_id = donation.id
            self.cart.addlog("Created a new Donation", save=True)

        donation.values.append(
            Values(campaign=campaign, value=float(value))
        )
        donation.save()

        self.cart.reference = donation

        cart_items = []
        for item in donation.values:
            cart_items.append(
                Item(
                    uid=item.campaign.get_uid(),
                    product=item.campaign,
                    reference=donation,
                    title=item.campaign.get_title(),
                    description=item.campaign.get_description(),
                    unity_value=item.value
                )
            )
            self.cart.addlog(
                "Item added/updated %s" % item.campaign.get_title(),
                save=False
            )

        self.cart.items = cart_items

        self.cart.requires_login = current_app.config.get(
            "FUNDRAISING_CART_REQUIRES_LOGIN",
            self.cart.requires_login
        )
        self.cart.continue_shopping_url = current_app.config.get(
            "FUNDRAISING_CART_CONTINUE_SHOPPING_URL",
            self.cart.continue_shopping_url
        )
        self.cart.pipeline = current_app.config.get(
            "FUNDRAISING_CART_PIPELINE",
            self.cart.pipeline
        )
        self.cart.config = current_app.config.get(
            "FUNDRAISING_CART_CONFIG",
            self.cart.config
        )

        self.cart.fundraising_donation_id = donation.id
        self.cart.addlog(u"%s items added" % len(cart_items), save=True)

        return redirect(url_for('cart.cart'))
