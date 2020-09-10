# Generated by Django 2.2 on 2020-08-20 05:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contract', '0008_auto_20200813_0858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='destroyed',
            name='return_date',
            field=models.DateField(blank=True, null=True, verbose_name='DNA取回日期'),
        ),
        migrations.AlterField(
            model_name='examiner',
            name='box',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contract.Box', verbose_name='採樣盒'),
        ),
        migrations.AlterField(
            model_name='examiner',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.Customer', verbose_name='受測者'),
        ),
    ]