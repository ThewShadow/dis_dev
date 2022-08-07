# Generated by Django 4.0.4 on 2022-08-03 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_product_allow_existing_accounts_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='communication_preferences',
            field=models.CharField(choices=[('email', 'email'), ('wa', 'whatsapp')], default='email', max_length=250),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='service_password',
            field=models.CharField(max_length=250),
        ),
    ]