# Generated by Django 4.0.4 on 2022-07-30 10:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_customuser_referral'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='referral',
            new_name='referrals',
        ),
    ]
