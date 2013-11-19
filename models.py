# coding: utf-8

from quokka.core.db import db
from quokka.core.models import Publishable
from quokka.modules.cart.models import BaseProduct


class Campaign(BaseProduct):
    body = db.StringField(required=True)
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    min_value = db.FloatField()
    max_value = db.FloatField()
    goal = db.FloatField()
    balance = db.FloatField()
    open_for_donations = db.BooleanField(default=True)


class Values(db.EmbeddedDocument):
    campaign = db.ReferenceField(Campaign)
    value = db.FloatField()


class Donation(Publishable, db.DynamicDocument):
    status = db.StringField()
    values = db.ListField(db.EmbeddedDocumentField(Values))
    total = db.FloatField()
    tax = db.FloatField()

    @property
    def donor(self):
        return self.created_by

    @donor.setter
    def donor(self, value):
        self.created_by = value
