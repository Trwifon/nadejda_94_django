# Generated by Django 5.0.4 on 2025-04-26 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('glasses', '0008_alter_glasses_first_glass_alter_glasses_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='glasses',
            name='module',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='glasses',
            name='thickness',
            field=models.IntegerField(choices=[(4, '4'), (5, '5'), (6, '6'), (8, '8'), (10, '10'), (12, '12'), (14, '14'), (16, '16'), (18, '18'), (20, '20'), (22, '22'), (24, '24'), (25, '25'), (26, '26'), (27, '27'), (28, '28'), (30, '30'), (32, '32'), (34, '34'), (36, '36'), (38, '38'), (40, '40'), (42, '42'), (44, '44')]),
        ),
    ]
