from django.contrib.auth.models import User
from django import forms
from requestservice.models import UserRequests, Messages


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)



class RequestForm(forms.ModelForm):
    file = forms.FileField(required=False)
    deadline = forms.DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = UserRequests
        exclude = ['user', 'views', 'downloads', 'closed']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Give A Descriptive Title'}),
            'keywords': forms.Textarea(attrs={'cols': 40, 'rows': 3, 'style': 'resize:none;',
                                                    'placeholder': 'Provide Keywords Seperated With "," '}),
            'service_description': forms.Textarea(attrs={'cols': 40, 'rows': 5, 'style': 'resize:none;',
                                                    'placeholder': 'Give A Description About Your Request'}),
        }


class MessageForm(forms.ModelForm):

    class Meta:
        model = Messages
        fields = ['message']
