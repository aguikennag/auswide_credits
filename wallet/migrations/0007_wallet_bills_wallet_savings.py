# Generated by Django 4.1.7 on 2023-03-20 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0006_transaction_mail_is_sent'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='bills',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='wallet',
            name='savings',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=50),
            preserve_default=False,
        ),
    ]