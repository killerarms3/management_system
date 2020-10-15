# Generated by Django 2.2 on 2020-10-13 03:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(max_length=32)),
                ('first_name', models.CharField(max_length=32)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('line_id', models.CharField(blank=True, max_length=32, null=True)),
                ('email', models.CharField(blank=True, max_length=320, null=True)),
                ('tel', models.CharField(blank=True, max_length=32, null=True)),
                ('mobile', models.CharField(blank=True, max_length=32, null=True)),
                ('address', models.CharField(blank=True, max_length=320, null=True)),
                ('memo', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Customer_Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('is_other', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('department', models.CharField(max_length=256)),
                ('is_other', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Title',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('is_other', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback', models.TextField()),
                ('feedback_date', models.DateField()),
                ('customer', models.ForeignKey(on_delete='CASCADE', to='customer.Customer')),
                ('product', models.ForeignKey(on_delete='CASCADE', to='product.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Customer_Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.ForeignKey(on_delete='CASCADE', to='customer.Customer')),
                ('organization', models.ForeignKey(on_delete='CASCADE', to='customer.Organization')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='customer_type',
            field=models.ForeignKey(on_delete='CASCADE', to='customer.Customer_Type'),
        ),
        migrations.AddField(
            model_name='customer',
            name='job',
            field=models.ForeignKey(on_delete='CASCADE', to='customer.Job'),
        ),
        migrations.AddField(
            model_name='customer',
            name='title',
            field=models.ForeignKey(on_delete='CASCADE', to='customer.Title'),
        ),
    ]