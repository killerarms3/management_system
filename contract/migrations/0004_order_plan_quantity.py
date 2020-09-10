# Generated by Django 2.2 on 2020-08-04 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
        ('contract', '0003_auto_20200803_0322'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order_Plan_quantity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantuty', models.PositiveIntegerField(blank=True, null=True)),
                ('order', models.ForeignKey(on_delete='CASCADE', to='contract.Order')),
                ('plan', models.ForeignKey(on_delete='CASCADE', to='product.Plan')),
            ],
        ),
    ]