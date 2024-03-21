# Generated by Django 4.2.7 on 2024-03-21 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DateLessonFit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_at', models.DateField(verbose_name='Дата начала:')),
                ('create_to', models.DateField(verbose_name='Дата окончания:')),
                ('schedule', models.ImageField(upload_to='media/bot/', verbose_name='Расписание занятий')),
            ],
            options={
                'verbose_name': 'Расписание группового занятия',
                'verbose_name_plural': 'Расписание групповых занятий',
            },
        ),
        migrations.CreateModel(
            name='TimeLessonFit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(verbose_name='Время занятия')),
            ],
            options={
                'verbose_name': 'Время группового занятия',
                'verbose_name_plural': 'Время групповых занятий',
            },
        ),
        migrations.CreateModel(
            name='UserFit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card', models.PositiveIntegerField(blank=True, db_index=True, null=True, verbose_name='Номер карты')),
                ('first_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='Фамилия')),
                ('created_at', models.DateTimeField(blank=True, null=True, verbose_name='Начало абонемента')),
                ('created_to', models.DateTimeField(blank=True, null=True, verbose_name='Коне абонемента')),
                ('actived', models.BooleanField(default=False, verbose_name='Активен')),
                ('phone', models.IntegerField(verbose_name='Телефон')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='Почта')),
            ],
            options={
                'verbose_name': 'Клиент тренажерного зала',
                'verbose_name_plural': 'Клиенты тренажерного зала',
            },
        ),
        migrations.CreateModel(
            name='TrainerFit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='Фамилия')),
                ('dae_lesson', models.ManyToManyField(blank=True, related_name='trainerfit_lessonfit', to='bot.datelessonfit', verbose_name='Неделя проведения занятий')),
            ],
            options={
                'verbose_name': 'Тренер тренажерного зала',
                'verbose_name_plural': 'Тренеры тренажерного зала',
            },
        ),
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_user_id', models.PositiveBigIntegerField(blank=True, db_index=True, null=True, unique=True, verbose_name='ID пользователя telegram')),
                ('is_authenticated', models.BooleanField(default=False, verbose_name='Авторизация')),
                ('username', models.CharField(blank=True, max_length=20, null=True, verbose_name='Никнейм')),
                ('first_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='Фамилия')),
                ('card', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.userfit', verbose_name='Номер карты')),
            ],
            options={
                'verbose_name': 'Пользователь тлеграмма',
                'verbose_name_plural': 'Пользователи телеграмма',
            },
        ),
        migrations.CreateModel(
            name='LessonFit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=25, null=True, verbose_name='Название')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Описание')),
                ('time', models.ManyToManyField(blank=True, related_name='lessonfit_timelessonfit', to='bot.timelessonfit', verbose_name='Дата и время занятия')),
            ],
            options={
                'verbose_name': 'Групповое занятие',
                'verbose_name_plural': 'Групповые занятия',
            },
        ),
        migrations.AddField(
            model_name='datelessonfit',
            name='lesson',
            field=models.ManyToManyField(blank=True, related_name='datelessonfit_lessonfit', to='bot.lessonfit', verbose_name='Занятия на текущей неделе'),
        ),
    ]
