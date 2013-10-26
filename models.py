# coding: utf-8

from quokka.core.db import db
from quokka.core.models import Publishable, Content
#from quokka.modules.accounts.models import User


class Campaign(Content):
    body = db.StringField(required=True)


class Values(db.EmbeddedDocument):
    campaign = db.ReferenceField(Campaign)
    campaign_name = db.StringField()
    value = db.FloatField()


class Payment(db.EmbeddedDocument):
    uid = db.StringField()
    method = db.StringField()
    value = db.FloatField()
    date = db.DateTimeField()
    confirmed_at = db.DateTimeField()
    status = db.StringField()


class Donation(Publishable, db.DynamicDocument):
    status = db.StringField()
    values = db.ListField(db.EmbeddedDocumentField(Values))
    total = db.FloatField()
    tax = db.FloatField()
    payment = db.EmbeddedDocumentField(Payment)

    @property
    def donor(self):
        return self.created_by

    @donor.setter
    def donor(self, value):
        self.created_by = value
