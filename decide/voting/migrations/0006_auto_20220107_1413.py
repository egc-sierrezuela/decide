# Generated by Django 2.0 on 2022-01-07 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0005_auto_20220107_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='type',
            field=models.IntegerField(choices=[(0, 'IDENTITY'), (3, 'SAINTE_LAGUE'), (2, 'BORDA'), (1, 'DHONT'), (4, 'EQUALITY')], default=1),
        ),
    ]
