# Generated by Django 4.1.9 on 2023-05-20 17:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docpi_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='createdOn',
        ),
    ]
