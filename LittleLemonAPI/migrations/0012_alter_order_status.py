# Generated by Django 4.2.5 on 2023-10-17 03:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonAPI', '0011_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Processing', 'Processing'), ('Delivered', 'Delivered')], default='Processing', max_length=20),
        ),
    ]
