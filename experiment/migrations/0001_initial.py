# Generated by Django 2.2 on 2020-07-30 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contract', '0001_initial'),
        ('accounts', '0007_auto_20200730_0956'),
    ]

    operations = [
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiving_date', models.DateField(blank=True, null=True)),
                ('complete_date', models.DateField(blank=True, null=True)),
                ('data_transfer_date', models.DateField(blank=True, null=True)),
                ('box', models.ForeignKey(on_delete='CASCADE', to='contract.Box')),
                ('organization', models.ForeignKey(on_delete='CASCADE', to='accounts.Organization')),
                ('transfer_organization', models.ForeignKey(on_delete='CASCADE', related_name='transfer_organization', to='accounts.Organization')),
            ],
        ),
    ]