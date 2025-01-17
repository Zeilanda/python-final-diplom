# Generated by Django 3.2 on 2023-01-13 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_confirmemailtoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=False, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),
    ]
