# Generated by Django 4.0.4 on 2022-06-27 11:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_rename_name_sp_currency_name_es_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='currency',
            old_name='name_il',
            new_name='name_he',
        ),
        migrations.RenameField(
            model_name='offer',
            old_name='name_il',
            new_name='name_he',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='name_il',
            new_name='name_he',
        ),
        migrations.RenameField(
            model_name='rate',
            old_name='name_il',
            new_name='name_he',
        ),
    ]
