# Generated by Django 4.2.7 on 2024-03-25 12:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_table_admin', '0003_remove_userfitlesson_date_and_more'),
        ('bot', '0002_delete_userfitlesson'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TimeLessonFit',
        ),
    ]
