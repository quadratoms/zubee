# Generated by Django 3.2.16 on 2022-12-08 17:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('loanapp', '0005_auto_20221208_0949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='virtualaccount',
            name='customer',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='loanapp.customer'),
        ),
    ]
