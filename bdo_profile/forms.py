from django.forms import *
from s3direct.widgets import S3DirectWidget

from .models import *


class UserProfileForm(ModelForm):

    class Meta:
        model = UserProfile
        exclude = ('user', )
        widgets = {
            'avatr_raw': S3DirectWidget(dest='avatars'),
        }
