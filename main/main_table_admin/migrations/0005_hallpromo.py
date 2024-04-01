# Generated by Django 4.2.7 on 2024-04-01 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_table_admin', '0004_maintableadmin_max_number_of_recorded'),
    ]

    operations = [
        migrations.CreateModel(
            name='HallPromo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50, verbose_name='Название')),
                ('description', models.CharField(max_length=255, verbose_name='Описание')),
                ('date_at', models.DateField(verbose_name='Начало кации')),
                ('date_to', models.DateField(verbose_name='Конец акции')),
                ('promo', models.CharField(max_length=5, verbose_name='Промокод')),
            ],
            options={
                'verbose_name': 'Акция фитнес-зала',
                'verbose_name_plural': 'Акции фитнес-зала',
            },
        ),
    ]