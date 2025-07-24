from django import forms

class AccountableFormForm(forms.ModelForm):
	class Meta:
		model = AccountableFormForm
		fields = '__all__'
