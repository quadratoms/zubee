# Generated by Django 3.2.16 on 2022-12-05 09:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('loanapp', '0003_auto_20221205_0947'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='customerImage')),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='customer_image', to='loanapp.customer')),
            ],
        ),
    ]