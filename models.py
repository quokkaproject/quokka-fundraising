# coding: utf-8

import datetime
from flask import current_app, url_for
from quokka.core.db import db
# from quokka.utils import get_current_user
from quokka.core.models.signature import Publishable
from quokka.core.models.channel import Channel
from quokka.modules.cart.models import BaseProduct, BaseProductReference, Cart
from quokka.modules.cart.models import Item


class Donations(db.EmbeddedDocument):
    donation = db.ReferenceField('Donation')
    status = db.StringField(default="pending", max_length=255)
    value = db.FloatField(default=0)
    donor = db.StringField(max_length=255)
    show_donor = db.BooleanField(default=True)
    display_name = db.StringField(max_length=255)


class Campaign(BaseProduct):
    description = db.StringField(required=True)
    start_date = db.DateTimeField(default=datetime.datetime.now)
    end_date = db.DateTimeField()
    min_value = db.FloatField(default=0)
    max_value = db.FloatField()
    goal = db.FloatField()
    balance = db.FloatField(default=0)
    open_for_donations = db.BooleanField(default=True)
    donations = db.ListField(db.EmbeddedDocumentField(Donations))

    def __unicode__(self):
        return self.title

    def update_donation(self, donation, value):
        don = self.donations.get(donation=donation)
        if don:
            don.status = donation.status
            don.value = value
            don.donor = donation.donor.name if donation.donor else None
            don.show_donor = donation.published
            don.display_name = donation.display_name
        else:
            don = Donations(
                donation=donation,
                status=donation.status,
                value=value,
                donor=donation.donor.name if donation.donor else None,
                show_donor=donation.published,
                display_name=donation.display_name
            )
            self.donations.append(don)
        self.save()

    def get_donor_list(self):
        return set([
            donation.display_name or donation.donor
            for donation in
            self.donations.filter(show_donor=True, status="confirmed") +
            self.donations.filter(show_donor=True, status="completed")
        ])

    def save(self, *args, **kwargs):
        if self.donations:
            self.balance = sum(
                [item.value
                 for item in self.donations.filter(status="confirmed") +
                 self.donations.filter(status="completed")]
            )
        super(Campaign, self).save(*args, **kwargs)


class Values(db.EmbeddedDocument):
    campaign = db.ReferenceField(Campaign)
    value = db.FloatField(default=0)

    def __unicode__(self):
        return u"{s.campaign} - {s.value}".format(s=self)


class Donation(BaseProductReference, Publishable, db.DynamicDocument):
    status = db.StringField(default="pending", max_length=255,
                            choices=Cart.STATUS)
    values = db.ListField(db.EmbeddedDocumentField(Values))
    total = db.FloatField(default=0)
    tax = db.FloatField(default=0)
    donor = db.ReferenceField('User',
                              # default=get_current_user,
                              required=False)
    display_name = db.StringField(max_length=255)
    cart = db.ReferenceField(Cart, reverse_delete_rule=db.NULLIFY)
    confirmed_date = db.DateTimeField()
    payment_method = db.StringField(max_length=255)

    search_helper = db.StringField()

    meta = {
        'ordering': ['-created_at']
    }

    def __unicode__(self):
        return u"{s.donor} - {s.total}".format(s=self)

    def get_admin_url(self):
        return url_for('donation.edit_view', id=self.id)

    def set_project_campaign(self, donation_to_project, cart=None):
        cart = cart or self.cart
        default_campaign = current_app.config.get(
            'FUNDRAISING_PROJECT_CAMPAIGN',
            {'slug': 'project-campaign',
             'title': 'Donation to project',
             'description': 'Donation to project',
             'published': True,
             'channel': Channel.get_homepage()}
        )

        try:
            campaign = Campaign.objects.get(slug=default_campaign.get('slug'))
        except Campaign.DoesNotExist:
            campaign = Campaign(**default_campaign)
            campaign.save()

        self.values.append(
            Values(campaign=campaign, value=float(donation_to_project))
        )

        cart.items.append(
            Item(
                uid=campaign.get_uid(),
                product=campaign,
                reference=self,
                title=campaign.get_title(),
                description=campaign.get_description(),
                unity_value=float(donation_to_project)
            )
        )
        cart.addlog(
            "Item added %s" % campaign.get_title(),
            save=False
        )
        self.save()

    def set_status(self, status, *args, **kwargs):
        self.status = status
        if status == "confirmed" and not self.confirmed_date:
            now = datetime.datetime.now()
            self.confirmed_date = kwargs.get('date', now)
        self.save()

    def set_tax(self, tax):
        self.tax = tax
        self.save()

    def get_response(self, response, identifier):
        pass

    def remove_item(self, **kwargs):
        uid = kwargs.get('uid')
        if uid:
            try:
                campaign = Campaign.objects.get(id=uid)
            except campaign.DoesNotExist:
                campaign = None

            if campaign:
                self.values.delete(campaign=campaign)
                # Commented out to avoid race conditions
                # implement a celery task to clean that donations
                # campaign.donations.delete(donation=self)
                self.save()

    def clean(self):
        unique_values = {
            unique: 0
            for unique in set([item.campaign for item in self.values])
        }
        for item in self.values:
            unique_values[item.campaign] += item.value

        self.values = [
            Values(campaign=campaign, value=value)
            for campaign, value in unique_values.items()
        ]

        if self.values:
            self.total = sum([item.value for item in self.values])
        else:
            self.total = 0

    def get_search_helper(self):
        if not self.donor:
            return ""
        user = self.donor
        return " ".join([
            user.name or "",
            user.email or "",
            self.display_name or ""
        ])

    def save(self, *args, **kwargs):

        if self.cart and self.cart.processor:
            self.payment_method = self.cart.processor.identifier

        self.search_helper = self.get_search_helper()
        super(Donation, self).save(*args, **kwargs)

        for item in self.values:
            item.campaign.update_donation(self, item.value)
