# Generated by Django 4.0.4 on 2022-07-21 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_remove_subscription_payment_type_delete_paymenttype'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='comment',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
