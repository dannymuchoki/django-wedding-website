# Generated by Django 3.2.11 on 2022-02-26 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0022_rename_arrival_dates_guest_arrival_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='party',
            name='is_invited',
            field=models.BooleanField(default=True),
        ),
    ]
