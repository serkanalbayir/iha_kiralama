from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UAV, RentalRecord

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class UAVForm(forms.ModelForm):
    class Meta:
        model = UAV
        fields = ['brand', 'model', 'weight', 'category']

class RentalRecordForm(forms.ModelForm):
    rental_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    return_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), required=False)

    class Meta:
        model = RentalRecord
        fields = ['uav', 'rental_date', 'return_date']

class UAVFilterForm(forms.Form):
    brand = forms.CharField(max_length=100, required=False)
    model = forms.CharField(max_length=100, required=False)
    min_weight = forms.FloatField(required=False)
    max_weight = forms.FloatField(required=False)
    category = forms.CharField(max_length=100, required=False)
