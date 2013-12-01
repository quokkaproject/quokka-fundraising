# coding : utf -8

from quokka import admin
from quokka.core.admin import _, _l
from quokka.core.admin.models import ModelAdmin, BaseContentAdmin
from quokka.core.admin.fields import ThumbField
from quokka.core.widgets import TextEditor, PrepopulatedText

from .models import Campaign, Donation


class CampaignAdmin(BaseContentAdmin):

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
                    'tags', 'values', 'template_type', 'donations']

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


class DonationAdmin(ModelAdmin):
    roles_accepted = ('admin', 'editor')
    column_list = ['donor', 'created_at', 'values', 'total', 'tax',
                   'status', 'published']
    form_columns = ['donor', 'created_at', 'values', 'total', 'tax',
                    'status', 'published',
                    'confirmed_date']


admin.register(Campaign, CampaignAdmin,
               category=_("Fundraising"), name=_l("Campaign"))
admin.register(Donation, DonationAdmin,
               category=_("Fundraising"), name=_l("Donation"))
