# Generated by Django 2.0 on 2022-01-03 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0008_auto_20220103_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='postproc_type',
            field=models.IntegerField(choices=[(0, 'IDENTITY'), (2, 'BORDA'), (4, 'EQUALITY'), (1, 'DHONT'), (3, 'SAINTE_LAGUE')], default=1),
        ),
    ]
