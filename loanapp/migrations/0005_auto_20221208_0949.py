# Generated by Django 3.2.16 on 2022-12-08 09:49

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('loanapp', '0004_customerimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', jsonfield.fields.JSONField(default=dict)),
            ],
        ),
        migrations.RenameField(
            model_name='bankdetail',
            old_name='bank_name',
            new_name='bank_code',
        ),
    ]