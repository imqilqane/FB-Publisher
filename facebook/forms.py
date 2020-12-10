from django import forms
from .models import adCopy, fbAccountsModel

class editAdCopyForm(forms.ModelForm):
    descriprtion = forms.CharField(widget=forms.Textarea(attrs={"row":"4","class":"w-100"}))
    link = forms.CharField(widget=forms.TextInput(attrs={"class":"w-100"}))
    image = forms.CharField(widget=forms.TextInput(attrs={"class":"w-100"}), required=False)

    class Meta :
        model = adCopy
        fields = ('descriprtion','link','image')

class editFbAccountForm(forms.ModelForm):
    fullname = forms.CharField(widget=forms.TextInput(attrs={"class":"w-100"}))
    class Meta :
        model = fbAccountsModel
        fields = ('fullname',)