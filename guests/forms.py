import io
import csv
from django import forms
from django.forms import ModelForm, modelformset_factory, BaseFormSet
from guests.models import Guest, MEALS, Party, UploadedGuestList

class UploadGuestListForm (forms.ModelForm):
    class Meta:
        model = UploadedGuestList
        fields = ('guest_list_file',) # This is in models.py. It is where the guest lists get defined and saved in admin


class AddGuestForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=100)
    last_name = forms.CharField(label="Last Name", max_length=100)
    email_address = forms.EmailField(label='Email Address')
    CATEGORIES = (('Bride', 'Bride'),('Groom', 'Groom'),)
    category = forms.ChoiceField(choices=CATEGORIES)
    meal = forms.ChoiceField(choices=MEALS)
    is_child = forms.BooleanField(label="Is this guest a child?", required=False)
    caboose_farm = forms.BooleanField(label="Invited to Caboose Farm?", required=False)