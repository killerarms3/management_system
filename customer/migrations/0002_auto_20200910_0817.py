# Generated by Django 2.2 on 2020-09-10 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
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
        migrations.RenameField(
            model_name='customer',
            old_name='phone_number',
            new_name='mobile',
        ),
        migrations.AddField(
            model_name='customer',
            name='tel',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='is_other',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='title',
            field=models.ForeignKey(null=True, on_delete='CASCADE', to='customer.Title'),
        ),
        migrations.AddField(
            model_name='customer',
            name='job',
            field=models.ForeignKey(null=True, on_delete='CASCADE', to='customer.Job'),
        ),
    ]
