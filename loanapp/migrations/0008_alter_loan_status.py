# Generated by Django 4.0.4 on 2022-10-10 16:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('loanapp', '0007_bankdetail_is_verify'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='loanapp.loanstatus'),
        ),
    ]
