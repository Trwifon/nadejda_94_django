# Generated by Django 5.0.4 on 2025-01-10 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='order_type',
            field=models.CharField(choices=[('C', 'Каса'), ('B', 'Банка'), ('S', 'Продажба'), ('A', 'Поръчка Алуминий'), ('P', 'Поръчка PVC')], max_length=2),
        ),
    ]
