# Generated by Django 3.0.7 on 2020-10-07 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_auto_20201005_2319'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderitem',
            options={'verbose_name': 'состав заказа', 'verbose_name_plural': 'состав заказа'},
        ),
        migrations.AlterField(
            model_name='order',
            name='phonenumber',
            field=models.CharField(max_length=100, verbose_name='адрес доставки'),
        ),
    ]
