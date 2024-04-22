
from django import forms
from . models import *

class RegitrationForm(forms.ModelForm):
    class Meta:
        model= Buyer_Seller
        fields=['phone','address']

