# Generated by Django 2.2 on 2020-08-04 02:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
        ('contract', '0004_order_plan_quantity'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Order_Plan_quantity',
            new_name='Order_quantity',
        ),
        migrations.RenameField(
            model_name='order_quantity',
            old_name='quantuty',
            new_name='quantity',
        ),
    ]
