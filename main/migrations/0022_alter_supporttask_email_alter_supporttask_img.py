# Generated by Django 4.0.4 on 2022-08-06 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_rename_text_supporttask_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supporttask',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='supporttask',
            name='img',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]