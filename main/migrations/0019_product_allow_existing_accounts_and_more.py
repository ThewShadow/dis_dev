# Generated by Django 4.0.4 on 2022-08-03 12:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_remove_customuser_referrals_alter_customuser_agent'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='allow_existing_accounts',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subscription',
            name='is_exist_account',
            field=models.BooleanField(default=False),
        ),
    ]
