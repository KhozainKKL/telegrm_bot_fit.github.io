from collections import defaultdict
from datetime import timedelta

from asgiref.sync import async_to_sync
from custom_modal_admin.admin import CustomModalAdmin
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from import_export.admin import ImportExportActionModelAdmin

from bot.import_export.resourse import MainTableAdminResource
from bot.main_bot import canceled_lesson_post_message_users, get_for_user_is_not_reserve, \
    change_lesson_post_message_users
from bot.models import TelegramUser, UserFit
from main.tasks import publish_object
from .forms import UserFitInLinesForm
from .models import UserFitLesson, HallPromo, MONTHS_RU
from main_table_admin.models import MainTableAdmin
from django.db.models.signals import post_save
from django.dispatch import receiver
from admincharts.admin import AdminChartMixin


class DateMonthFilter(admin.SimpleListFilter):
    title = 'По месяцу'
    parameter_name = 'date_month'

    def lookups(self, request, model_admin):
        # Получаем список месяцев, по которым есть записи
        months = model_admin.get_queryset(request).datetimes('date', 'month')
        return [(month.month, MONTHS_RU[month.month]) for month in months]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__month=self.value())
        else:
            return queryset


class UserFitInLines(admin.TabularInline):
    model = UserFitLesson
    form = UserFitInLinesForm
    autocomplete_fields = ["user"]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        date_check = timezone.now() - timedelta(days=3)
        if obj and obj.date < date_check:
            # Если занятие уже прошло, делаем все поля только для чтения
            return [field.name for field in self.model._meta.fields]
        return readonly_fields


@admin.register(MainTableAdmin)
class MainTableModelAdmin(AdminChartMixin, CustomModalAdmin, admin.ModelAdmin):
    inlines = [UserFitInLines]
    search_fields = ['date', 'lesson__title', 'trainer__first_name', 'trainer__last_name']
    list_display = ['date', 'lesson', 'trainer', 'number_of_recorded', 'check_canceled',
                    'check_canceled_description']
    list_filter = (DateMonthFilter, 'date', 'lesson', 'trainer')
    readonly_fields = ('number_of_recorded',)
    list_display_links = ['date', 'lesson', 'trainer', ]
    autocomplete_fields = ["lesson", "trainer"]
    list_chart_options = {"aspectRatio": 8}
    change_form_template = 'admin/confirm_save_modal.html'
    ordering = ['date']
    list_per_page = 50
    fieldsets = [
        (
            "Основная информация",
            {
                "fields": ["date", "lesson", "trainer",
                           ("max_number_of_recorded", "number_of_recorded")],
            },
        ),
        (
            "ОТМЕНА И ИЗМЕНЕНИЕ",
            {
                "classes": ["collapse", "wide"],
                "fields": [("check_canceled", "check_canceled_description"), "check_change_description"],
            },

        ),
    ]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.date < timezone.now():
            # Если занятие уже прошло, делаем определенные поля только для чтения
            return ['date', 'lesson', 'trainer', 'number_of_recorded', 'max_number_of_recorded',
                    'check_canceled', 'check_canceled_description', 'check_change_description']
        return readonly_fields

    def get_list_chart_config(self, queryset):
        # Получаем базовую конфигурацию
        config = super().get_list_chart_config(queryset)

        # Добавляем настройки анимации
        config['options']['animation'] = {
            'duration': 1000,  # Длительность анимации в миллисекундах
            'easing': 'easeInOutQuad',  # Функция плавности анимации
        }

        return config

    def get_list_chart_data(self, queryset):
        if not queryset:
            return {}

        data = defaultdict(int)
        for item in queryset:
            date_key = item.date.date()  # Получаем только дату без времени
            data[date_key] += item.number_of_recorded
        start_date = min(data.keys())
        end_date = max(data.keys())
        start_date = start_date.replace(day=1)
        end_date = (end_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        all_dates = {}
        current_date = start_date
        while current_date <= end_date:
            all_dates[current_date] = 0
            current_date += timedelta(days=1)
        for date_key, value in data.items():
            all_dates[date_key] = value
        labels = [date.strftime("%d-%m-%Y") for date in sorted(all_dates.keys())]
        totals = [all_dates[date] for date in sorted(all_dates.keys())]

        return {
            "labels": labels,
            "datasets": [
                {"label": "Клиенты за день", "data": totals, "backgroundColor": "#297762"},
            ],
        }

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:
                instance.lesson.number_of_recorded += 1
                instance.lesson.save()
        super().save_formset(request, form, formset, change)

        for deleted_object in formset.deleted_objects:
            if deleted_object.lesson.number_of_recorded != 0:
                deleted_object.lesson.number_of_recorded -= 1
            deleted_object.lesson.save()


@admin.register(UserFitLesson)
class UserFitLessonAdmin(ImportExportActionModelAdmin):
    resource_class = MainTableAdminResource
    readonly_fields = ('user', 'lesson', 'is_reserve', 'is_come')

    def has_delete_permission(self, request, obj=None):
        return False

    def get_import_formats(self):
        return []
    

@admin.register(HallPromo)
class HallPromoModelAdmin(admin.ModelAdmin):
    search_fields = ['title', 'description']
    list_display = ['title', 'description', 'date_at', 'date_to', 'promo']
    list_display_links = ["title", "description"]
    fieldsets = [
        (
            "Основная информация",
            {
                "fields": ['title', 'description', 'date_at', 'date_to', 'promo', 'image'],
            },
        ),
    ]

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if request.method == 'POST' and '_publish' in request.POST:
            publish_object.delay(request.POST, object_id)
            messages.add_message(request, messages.INFO,
                                 f'Акционная рассылка "{request.POST["title"]}" успешно отправлена пользователям.')
            return HttpResponseRedirect(reverse('admin:main_table_admin_hallpromo_changelist'))
        else:
            self.change_form_template = 'admin/main_table_admin/hallpromo_change_form.html'
            return super().change_view(request, object_id, form_url, extra_context)


@receiver(signal=post_save, sender=MainTableAdmin, dispatch_uid="unique_id_for_notify_users_on_cancel")
def notify_users_on_cancel(sender, instance, created, **kwargs):
    result = {'lesson': None, 'lesson_title': None, 'tg_users': {}}
    users = UserFitLesson.objects.filter(lesson=instance).values_list('user', flat=True)
    data = UserFitLesson.objects.filter(lesson=instance).values_list('lesson', flat=True)
    if not created and instance.check_canceled:
        if data:
            result['lesson'] = list(MainTableAdmin.objects.filter(pk__in=data))
            result['lesson_title'] = list(
                MainTableAdmin.objects.filter(pk__in=data).values_list('lesson__title', flat=True))
            tg_users = TelegramUser.objects.filter(card__in=users).values_list('telegram_user_id', flat=True)
            if tg_users:
                tmp = MainTableAdmin.objects.filter(pk__in=data).first()
                for tg_user in tg_users:
                    result['tg_users'][f'{tg_user}'] = tg_user
                if tmp.number_of_recorded != 0:
                    tmp.number_of_recorded -= len(tg_users)
                    tmp.save()
                elif tmp.number_of_recorded == 0:
                    data = UserFitLesson.objects.filter(lesson__in=data)
                    data.delete()
                    async_to_sync(canceled_lesson_post_message_users)(result)

    elif not instance.check_canceled and instance.tracker.changed() and instance.check_change_description:
        if data:
            result['lesson'] = list(MainTableAdmin.objects.filter(pk__in=data))
            result['lesson_title'] = list(
                MainTableAdmin.objects.filter(pk__in=data).values_list('lesson__title', 'trainer__first_name',
                                                                       'check_change_description'))
            tg_users = TelegramUser.objects.filter(card__in=users).values_list('telegram_user_id', flat=True)
            if tg_users:
                for tg_user in tg_users:
                    result['tg_users'][f'{tg_user}'] = tg_user
                async_to_sync(change_lesson_post_message_users)(result)
                MainTableAdmin.objects.filter(pk=instance.pk).update(check_change_description=None)


@receiver(signal=post_save, sender=UserFitLesson, dispatch_uid="unique_id_for_notify_users_on_cancel")
def check_user_is_not_reserve(sender, instance, created, **kwargs):
    result = {'lesson': None, 'lesson_title': None, 'tg_users': {}}
    if not created and not instance.is_reserve:
        user = UserFit.objects.filter(card=instance.user.card).values_list('pk', flat=True)
        tg_user = TelegramUser.objects.filter(card__in=user).values_list('telegram_user_id', flat=True).first()
        data = UserFitLesson.objects.filter(lesson=instance.lesson).values_list('lesson', flat=True)
        if data:
            result['lesson'] = list(MainTableAdmin.objects.filter(pk__in=data))
            result['lesson_title'] = list(
                MainTableAdmin.objects.filter(pk__in=data).values_list('lesson__title', flat=True))
            if tg_user:
                result['tg_users'][f'{tg_user}'] = tg_user
                async_to_sync(get_for_user_is_not_reserve)(result)
