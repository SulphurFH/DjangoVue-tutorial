# Generated by Django 2.0.5 on 2018-05-14 10:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Book',
            new_name='Books',
        ),
    ]
