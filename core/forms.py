from django import forms
from .models import Portfolio
from django.forms import HiddenInput

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ('user', 'stock', 'quantity', "bought_price")
        widgets={'user': HiddenInput()}
