from django import forms
from .models import settingModel2
from django.contrib.auth.models import User

subscription_options = [
    ('1-month', '1-Month subscription ($12.49 USD/Mon)'),
    ('6-month', '6-Month subscription Save $10 ($10.82 USD/Mon)'),
    ('1-year', '1-Year subscription Save $25 ($10.40 USD/Mon)'),
]


class SubscriptionForm(forms.Form):
    plans = forms.ChoiceField(choices=subscription_options)

class settingsForm(forms.ModelForm):
    class Meta:
        model = settingModel2
        fields = ['group_join_per_time','post_per_time']


class profileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','email','username','password']