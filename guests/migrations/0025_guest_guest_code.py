# Generated by Django 3.2.11 on 2022-02-26 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guests', '0024_alter_guest_caboose_farm'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='guest_code',
            field=models.PositiveIntegerField(default='78610'),
        ),
    ]
