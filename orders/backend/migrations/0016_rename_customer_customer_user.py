# Generated by Django 3.2 on 2023-01-15 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0015_auto_20230115_1632'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='customer',
            new_name='user',
        ),
    ]
