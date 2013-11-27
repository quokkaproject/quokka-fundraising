# coding: utf-8

from random import sample
from .models import Campaign, Donation


def get_random_campaign(items=3, current_id=None, **kwargs):
    filters = kwargs
    if current_id:
        filters['id__ne'] = current_id

    queryset = Campaign.available_objects(**filters)
    total = queryset.count()
    if items > total:
        items = total
    return sample(queryset, items)


def get_latest_donations(limit=None, order_by='-confirmed_date', **kwargs):
    donations = Donation.objects.filter(
        published=True,
        status='confirmed',
        **kwargs
    ).order_by(order_by)

    if limit:
        donations = donations[:limit]

    return donations
