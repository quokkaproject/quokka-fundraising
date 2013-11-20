# coding: utf-8

from random import sample
from .models import Campaign


def get_random_campaign(items=3, current_id=None):
    filters = {}
    if current_id:
        filters['id__ne'] = current_id

    queryset = Campaign.available_objects(**filters)
    total = queryset.count()
    if items > total:
        items = total
    return sample(queryset, items)
