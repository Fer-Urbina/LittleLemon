# Generated by Django 4.2.5 on 2023-10-13 03:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0008_alter_cart_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LittleLemonAPI.order'),
        ),
    ]
