# Generated by Django 3.2.16 on 2022-11-27 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loanapp', '0021_auto_20221127_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='loan',
            name='last_share',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
