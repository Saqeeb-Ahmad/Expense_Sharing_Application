# Generated by Django 5.1.2 on 2024-10-21 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses_app', '0005_alter_user_managers_remove_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='split_details',
            field=models.JSONField(default=dict),
        ),
    ]
