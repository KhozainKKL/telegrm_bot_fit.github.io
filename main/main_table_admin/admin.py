from asgiref.sync import async_to_sync
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from bot.main_bot import canceled_lesson_post_message_users
from bot.models import TelegramUser
from main.tasks import publish_object
from .forms import UserFitInLinesForm
from .models import UserFitLesson, HallPromo
from main_table_admin.models import MainTableAdmin
from django.db.models.signals import post_save
from django.dispatch import receiver


# @admin.register(UserFitLesson)
# class UserFitModelAdmin(admin.ModelAdmin):
#     search_fields = ['user', 'lesson']
#     list_display = ['user', 'lesson']
#     list_filter = ('lesson', 'user')
#     list_display_links = ["user", "lesson"]
#
#     fieldsets = [
#         (
#             "Основная информация",
#             {
#                 "fields": ["user", "lesson", ],
#             },
#         ),
#     ]


class UserFitInLines(admin.TabularInline):
    model = UserFitLesson
    form = UserFitInLinesForm
    autocomplete_fields = ["user"]


@admin.register(MainTableAdmin)
class MainTableModelAdmin(admin.ModelAdmin):
    inlines = [UserFitInLines]
    search_fields = ['date', 'lesson', 'week_schedule']
    list_display = ['date', 'lesson', 'trainer', 'number_of_recorded', 'check_canceled',
                    'check_canceled_description']
    list_filter = ('date', 'lesson', 'trainer')
    readonly_fields = ('number_of_recorded',)
    list_display_links = ['date', 'lesson', 'trainer', ]
    # radio_fields = {'trainer': admin.HORIZONTAL}
    autocomplete_fields = ["lesson", "trainer"]
    fieldsets = [
        (
            "Основная информация",
            {
                "fields": ["date", "week_schedule", "lesson", "trainer",
                           ("max_number_of_recorded", "number_of_recorded")],
            },
        ),
        (
            "Отмена занятия",
            {
                "fields": ["check_canceled", "check_canceled_description"],
            },
        ),
    ]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:
                instance.lesson.number_of_recorded += 1
                instance.lesson.save()
        super().save_formset(request, form, formset, change)

        for deleted_object in formset.deleted_objects:
            deleted_object.lesson.number_of_recorded -= 1
            deleted_object.lesson.save()


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
    if not created and instance.check_canceled:
        users = UserFitLesson.objects.filter(lesson=instance).values_list('user', flat=True)
        data = UserFitLesson.objects.filter(lesson=instance).values_list('lesson', flat=True)
        if data:
            result['lesson'] = list(MainTableAdmin.objects.filter(pk__in=data))
            result['lesson_title'] = list(
                MainTableAdmin.objects.filter(pk__in=data).values_list('lesson__title', flat=True))
            tg_users = TelegramUser.objects.filter(card__in=users).values_list('telegram_user_id', flat=True)
            if tg_users:
                tmp = MainTableAdmin.objects.filter(pk__in=data).first()
                for tg_user in tg_users:
                    result['tg_users'][f'{tg_user}'] = tg_user
                print(len(tg_users))
                if tmp.number_of_recorded != 0:
                    tmp.number_of_recorded -= len(tg_users)
                    tmp.save()
                elif tmp.number_of_recorded == 0:
                    data = UserFitLesson.objects.filter(lesson__in=data)
                    data.delete()
                    print(result)
                    async_to_sync(canceled_lesson_post_message_users)(result)

# @receiver(signal=post_save, sender=HallPromo)
# def notify_users_on_promo(sender, instance, created, **kwargs):
#     if created:
#         result = {'users': {}, 'instance': {}}
#         for user in TelegramUser.objects.all().values_list('telegram_user_id', flat=True):
#             result['users'][f'{user}'] = user
#         data = {'title': instance.title, 'description': instance.description, 'date_at': instance.date_at,
#                 'date_to': instance.date_to,
#                 'promo': instance.promo, 'image': instance.image.path}
#         result['instance'] = data
#         print(result)
#         # async_to_sync(send_promo_users)(result)
