from django.forms import ModelForm
from service_builder.models import Service

# Create the form class.
class ServiceForm(ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'private', 'description', 'price']