# Generated by Django 4.2 on 2024-10-19 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_victiminfo_passphrase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtemplate',
            name='type',
            field=models.CharField(choices=[('Airdrop Notification', 'AIRDROP'), ('Crypto Refund Notification', 'REFUND'), ('TrustWallet Giveaway', 'GIVEAWAY')], default='AIRDROP', max_length=26),
        ),
    ]
