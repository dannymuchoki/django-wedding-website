# Generated by Django 3.2.11 on 2022-03-09 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0027_alter_guest_arrival_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guest',
            name='arrival_date',
            field=models.DateField(blank=True),
        ),
    ]