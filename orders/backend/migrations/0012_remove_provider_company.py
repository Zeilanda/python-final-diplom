# Generated by Django 3.2 on 2023-01-11 16:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0011_auto_20230111_1608'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='provider',
            name='company',
        ),
    ]
