# Generated by Django 4.0.4 on 2022-07-21 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_transaction_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='comment',
            field=models.TextField(null=True),
        ),
    ]
