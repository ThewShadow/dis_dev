# Generated by Django 4.0.4 on 2022-07-21 10:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_transaction_pay_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscription',
            name='payment_type',
        ),
        migrations.DeleteModel(
            name='PaymentType',
        ),
    ]
