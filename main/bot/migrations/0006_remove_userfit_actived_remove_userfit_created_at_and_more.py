# Generated by Django 4.2.7 on 2024-03-24 22:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_alter_lessonfit_title_alter_timelessonfit_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userfit',
            name='actived',
        ),
        migrations.RemoveField(
            model_name='userfit',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='userfit',
            name='created_to',
        ),
        migrations.RemoveField(
            model_name='userfit',
            name='email',
        ),
    ]
