# Generated by Django 2.0 on 2021-12-19 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0004_voting_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voting',
            name='url',
            field=models.URLField(help_text='http://localhost:8000/booth/'),
        ),
    ]
