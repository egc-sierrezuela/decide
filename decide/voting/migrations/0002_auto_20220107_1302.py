# Generated by Django 2.0 on 2022-01-07 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='type',
            field=models.IntegerField(choices=[(2, 'BORDA'), (0, 'IDENTITY'), (4, 'EQUALITY'), (1, 'DHONT'), (3, 'SAINTE_LAGUE')], default=1),
        ),
    ]
