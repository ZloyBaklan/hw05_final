# Generated by Django 2.2.6 on 2021-01-23 07:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_post'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Post',
        ),
    ]
