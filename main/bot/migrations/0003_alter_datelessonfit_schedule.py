# Generated by Django 4.2.7 on 2024-04-15 11:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_alter_telegramuser_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datelessonfit',
            name='schedule',
            field=models.ImageField(upload_to='bot/lesson_schedule/', validators=[django.core.validators.RegexValidator(message='Название файла должно содержать интервал месяц и день, например: 01.13-01.20', regex='^\\d{2}.\\d{2}-\\d{2}.\\d{2}$')], verbose_name='Расписание'),
        ),
    ]
