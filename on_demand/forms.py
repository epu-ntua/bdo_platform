from decimal import Decimal

from on_demand.models import *
from django.forms import ModelForm


class OnDemandRequestForm(ModelForm):
    class Meta:
        model = OnDemandRequest
        fields = ('title', 'description', 'keywords_raw', 'pricing', 'price', )

    def clean(self):
        cleaned_data = super(OnDemandRequestForm, self).clean()

        # validate price based on selected pricing model
        if cleaned_data['pricing'] == 'TBD':
            cleaned_data['price'] = None
        elif cleaned_data['pricing'] == 'FREE':
            cleaned_data['price'] = Decimal(0)

        return cleaned_data


class OnDemandReplyForm(ModelForm):
    class Meta:
        model = OnDemandReply
        fields = ('text', )
