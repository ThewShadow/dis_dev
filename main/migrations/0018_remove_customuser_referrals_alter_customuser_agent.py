# Generated by Django 4.0.4 on 2022-07-30 10:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_rename_referral_customuser_referrals'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='referrals',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='agent',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='referrals', to=settings.AUTH_USER_MODEL),
        ),
    ]