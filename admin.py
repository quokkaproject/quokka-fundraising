# coding : utf -8

from quokka import admin
from quokka.utils.translation import _, _l
from quokka.core.admin.models import ModelAdmin, BaseContentAdmin
from quokka.core.admin.fields import ThumbField
from quokka.core.widgets import TextEditor, PrepopulatedText

from .models import Campaign, Donation


def difference(self, request, obj, fieldname, *args, **kwargs):
    if not obj.goal:
        return 0
    return float(obj.balance or 0) - float(obj.goal or 0)


class CampaignAdmin(BaseContentAdmin):

    column_list = ('title', 'slug', 'channel',
                   'balance', 'goal', 'difference',
                   'published', 'created_at',
                   'available_at', 'view_on_site')

    column_searchable_list = ('title', 'description', 'summary')

    form_args = {
        "description": {"widget": TextEditor()},
        "slug": {"widget": PrepopulatedText(master='title')}
    }

    form_columns = ['title', 'slug', 'channel', 'related_channels', 'summary',
                    'content_format', 'description', 'published',
                    'start_date', 'end_date',
                    'min_value', 'max_value',
                    'goal', 'balance',
                    'open_for_donations',
                    'add_image', 'contents',
                    'show_on_channel', 'available_at', 'available_until',
                    'tags', 'values', 'template_type']

    form_subdocuments = {
        'contents': {
            'form_subdocuments': {
                None: {
                    'form_columns': ('content', 'caption', 'purpose',
                                     'order', 'thumb'),
                    'form_ajax_refs': {
                        'content': {
                            'fields': ['title', 'long_slug', 'summary']
                        }
                    },
                    'form_extra_fields': {
                        'thumb': ThumbField('thumb', endpoint="media")
                    }
                }
            }
        },
    }

    column_formatters = {
        'view_on_site': ModelAdmin.formatters.get('view_on_site'),
        'created_at': ModelAdmin.formatters.get('datetime'),
        'available_at': ModelAdmin.formatters.get('datetime'),
        'difference': difference
    }


class DonationAdmin(ModelAdmin):
    roles_accepted = ('admin', 'editor')
    column_list = ['donor', 'created_at', 'values', 'total', 'tax',
                   'payment_method', 'status', 'confirmed_date', 'published']
    column_searchable_list = ['search_helper', 'payment_method']
    column_filters = ('status', 'created_at', 'confirmed_date',
                      'payment_method', 'display_name', 'total', 'tax')
    form_columns = ['donor', 'created_at',
                    'values',
                    'total', 'tax',
                    'payment_method', 'status', 'published',
                    'confirmed_date', 'display_name']

    column_formatters = {
        'created_at': ModelAdmin.formatters.get('datetime'),
        'available_at': ModelAdmin.formatters.get('datetime'),
        'values': ModelAdmin.formatters.get('ul'),
        'status': ModelAdmin.formatters.get('status'),
    }

    column_formatters_args = {
        'ul': {
            'values': {
                'placeholder': u"{item.campaign.title} - {item.value}",
                'style': "min-width:200px;max-width:300px;"
            }
        },
        'status': {
            'status': {
                'labels': {
                    'confirmed': 'success',
                    'checked_out': 'warning',
                    'cancelled': 'important',
                    'completed': 'success'
                },
                'style': 'min-height:18px;'
            }
        }
    }


admin.register(Campaign, CampaignAdmin,
               category=_("Fundraising"), name=_l("Campaign"))
admin.register(Donation, DonationAdmin,
               category=_("Fundraising"), name=_l("Donation"))
