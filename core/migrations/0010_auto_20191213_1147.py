# Generated by Django 3.0 on 2019-12-13 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_stock_stock_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockdata',
            name='current_price',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]