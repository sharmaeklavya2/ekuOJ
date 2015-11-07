from django import forms
from django.contrib.auth.models import User

class EditProfileForm(forms.ModelForm):
	first_name = forms.CharField(max_length=30,required=True)
	class Meta:
		model = User
		fields = ("first_name", "last_name", "email")
