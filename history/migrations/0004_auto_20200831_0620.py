# Generated by Django 2.2 on 2020-08-31 06:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0003_auto_20200824_0940'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='history',
            options={'permissions': [('can_view_self_history', 'can view self history')]},
        ),
    ]