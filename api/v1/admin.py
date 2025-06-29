from django.contrib import admin
from django.db.models import Count, Sum, Q
from django.utils.html import format_html
from django.utils.timezone import now
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponse
import csv
from datetime import timedelta
from .models import TgUsers, IdScript, Answer, Referral


class ExportCsvMixin:

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='application/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'

        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Экспорт в CSV"


@admin.register(TgUsers)
class TgUsersAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = [
        'user_id_display', 'username_display', 'is_admin',
        'scripts_count', 'active_scripts_count', 'total_usage',
        'referrals_count', 'created_at'
    ]
    list_filter = [
        'is_admin', 'created_at',
        ('scripts__is_active', admin.BooleanFieldListFilter),
    ]
    search_fields = ['user', 'username']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'username', 'is_admin')
        }),
        ('Статистика', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['export_as_csv', 'make_admin', 'unmake_admin']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'scripts', 'invited', 'referral_source'
        ).annotate(
            scripts_count=Count('scripts'),
            active_scripts_count=Count('scripts', filter=Q(scripts__is_active=True)),
            total_usage=Sum('scripts__used'),
            referrals_count=Count('invited')
        )

    def user_id_display(self, obj):
        return format_html(
            '<strong>{}</strong>',
            obj.user
        )

    user_id_display.short_description = 'User ID'
    user_id_display.admin_order_field = 'user'

    def username_display(self, obj):
        if obj.username:
            return format_html(
                '<span style="color: #0066cc;">@{}</span>',
                obj.username
            )
        return '-'

    username_display.short_description = 'Username'
    username_display.admin_order_field = 'username'

    def scripts_count(self, obj):
        count = obj.scripts_count
        if count > 0:
            url = reverse('admin:v1_idscript_changelist') + f'?owner__id__exact={obj.id}'
            return format_html('<a href="{}">{}</a>', url, count)
        return count

    scripts_count.short_description = 'Скрипты'
    scripts_count.admin_order_field = 'scripts_count'

    def active_scripts_count(self, obj):
        count = obj.active_scripts_count
        if count > 0:
            return format_html('<span style="color: #28a745; font-weight: bold;">{}</span>', count)
        return count

    active_scripts_count.short_description = 'Активные'
    active_scripts_count.admin_order_field = 'active_scripts_count'

    def total_usage(self, obj):
        usage = obj.total_usage or 0
        if usage > 0:
            return format_html('<span style="color: #dc3545; font-weight: bold;">{}</span>', usage)
        return usage

    total_usage.short_description = 'Использований'
    total_usage.admin_order_field = 'total_usage'

    def referrals_count(self, obj):
        count = obj.referrals_count
        if count > 0:
            return format_html('<span style="color: #fd7e14; font-weight: bold;">{}</span>', count)
        return count

    referrals_count.short_description = 'Рефералы'
    referrals_count.admin_order_field = 'referrals_count'

    def make_admin(self, request, queryset):
        queryset.update(is_admin=True)

    make_admin.short_description = "Сделать администратором"

    def unmake_admin(self, request, queryset):
        queryset.update(is_admin=False)

    unmake_admin.short_description = "Убрать права администратора"


@admin.register(IdScript)
class IdScriptAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = [
        'script_display', 'owner_display', 'script_type', 'status_display',
        'usage_display', 'fingerprint_display', 'time_range_display',
        'created_at'
    ]
    list_filter = [
        'is_active', 'script_type', 'created_at', 'start_at', 'stop_at',
        ('fingerprint', admin.EmptyFieldListFilter),
        ('first_activate', admin.EmptyFieldListFilter),
        'owner__is_admin'
    ]
    search_fields = ['script', 'key', 'owner__username', 'owner__user', 'fingerprint']
    readonly_fields = [
        'created_at', 'updated_at', 'first_activate', 'first_seen',
        'script', 'key', 'usage_progress'
    ]

    fieldsets = (
        ('Основная информация', {
            'fields': ('owner', 'script', 'key', 'script_type')
        }),
        ('Настройки активности', {
            'fields': ('is_active', 'start_at', 'stop_at', 'fingerprint')
        }),
        ('Использование', {
            'fields': ('used', 'max_usage', 'usage_progress')
        }),
        ('Статистика', {
            'fields': ('first_activate', 'first_seen', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['export_as_csv', 'activate_scripts', 'deactivate_scripts', 'reset_usage']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner').prefetch_related('answers')

    def script_display(self, obj):
        return format_html(
            '<code style="background: #f8f9fa; padding: 2px 4px; border-radius: 3px;">{}</code>',
            obj.script
        )

    script_display.short_description = 'Скрипт'
    script_display.admin_order_field = 'script'

    def owner_display(self, obj):
        username = f"@{obj.owner.username}" if obj.owner.username else str(obj.owner.user)
        admin_badge = " 👑" if obj.owner.is_admin else ""
        return format_html(
            '<a href="{}">{}{}</a>',
            reverse('admin:v1_tgusers_change', args=[obj.owner.id]),
            username,
            admin_badge
        )

    owner_display.short_description = 'Владелец'
    owner_display.admin_order_field = 'owner__username'

    def status_display(self, obj):
        current_time = now()
        is_time_valid = obj.start_at <= current_time <= obj.stop_at

        if obj.is_active and is_time_valid:
            status = "🟢 Активен"
            color = "#28a745"
        elif obj.is_active and not is_time_valid:
            status = "🟡 Неактивен (время)"
            color = "#ffc107"
        elif not obj.is_active:
            status = "🔴 Отключен"
            color = "#dc3545"
        else:
            status = "❓ Неизвестно"
            color = "#6c757d"

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )

    status_display.short_description = 'Статус'

    def usage_display(self, obj):
        percentage = (obj.used / obj.max_usage) * 100 if obj.max_usage > 0 else 0

        if percentage >= 90:
            color = "#dc3545"
        elif percentage >= 70:
            color = "#ffc107"
        else:
            color = "#28a745"

        return format_html(
            '<div style="display: flex; align-items: center;">'
            '<div style="width: 100px; background: #e9ecef; border-radius: 10px; height: 20px; margin-right: 10px;">'
            '<div style="width: {}%; background: {}; height: 100%; border-radius: 10px;"></div>'
            '</div>'
            '<span style="font-weight: bold;">{}/{} ({}%)</span>'
            '</div>',
            percentage, color, obj.used, obj.max_usage, int(percentage)
        )

    usage_display.short_description = 'Использование'

    def fingerprint_display(self, obj):
        if obj.fingerprint:
            return format_html(
                '<code style="background: #d4edda; padding: 2px 4px; border-radius: 3px; font-size: 11px;">{}</code>',
                obj.fingerprint[:20] + '...' if len(obj.fingerprint) > 20 else obj.fingerprint
            )
        return format_html('<span style="color: #6c757d;">Не задан</span>')

    fingerprint_display.short_description = 'Отпечаток'

    def time_range_display(self, obj):
        start = obj.start_at.strftime('%d.%m %H:%M')
        stop = obj.stop_at.strftime('%d.%m %H:%M')
        return format_html(
            '<small>{} — {}</small>',
            start, stop
        )

    time_range_display.short_description = 'Время действия'

    def usage_progress(self, obj):
        percentage = (obj.used / obj.max_usage) * 100 if obj.max_usage > 0 else 0
        return format_html(
            '<div style="width: 200px; background: #e9ecef; border-radius: 10px; height: 25px; position: relative;">'
            '<div style="width: {}%; background: linear-gradient(90deg, #28a745, #20c997); height: 100%; border-radius: 10px;"></div>'
            '<span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-weight: bold; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">'
            '{}/{} ({}%)'
            '</span>'
            '</div>',
            percentage, obj.used, obj.max_usage, int(percentage)
        )

    usage_progress.short_description = 'Прогресс использования'

    def activate_scripts(self, request, queryset):
        queryset.update(is_active=True)

    activate_scripts.short_description = "Активировать скрипты"

    def deactivate_scripts(self, request, queryset):
        queryset.update(is_active=False)

    deactivate_scripts.short_description = "Деактивировать скрипты"

    def reset_usage(self, request, queryset):
        queryset.update(used=0)

    reset_usage.short_description = "Сбросить счетчик использований"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = [
        'id', 'script_display', 'owner_display', 'image_preview',
        'has_answer', 'created_at'
    ]
    list_filter = [
        'created_at', 'script__script_type', 'script__owner__is_admin',
        ('answer', admin.EmptyFieldListFilter)
    ]
    search_fields = [
        'script__script', 'script__owner__username',
        'script__owner__user', 'answer'
    ]
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']

    fieldsets = (
        ('Основная информация', {
            'fields': ('script', 'image', 'image_preview_large')
        }),
        ('Ответ', {
            'fields': ('answer',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['export_as_csv', 'delete_selected_answers']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('script__owner')

    def script_display(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:v1_idscript_change', args=[obj.script.id]),
            obj.script.script
        )

    script_display.short_description = 'Скрипт'
    script_display.admin_order_field = 'script__script'

    def owner_display(self, obj):
        username = f"@{obj.script.owner.username}" if obj.script.owner.username else str(obj.script.owner.user)
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:v1_tgusers_change', args=[obj.script.owner.id]),
            username
        )

    owner_display.short_description = 'Владелец'
    owner_display.admin_order_field = 'script__owner__username'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 5px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return '-'

    image_preview.short_description = 'Превью'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 500px; max-height: 500px; border-radius: 10px; border: 2px solid #ddd;" />',
                obj.image.url
            )
        return '-'

    image_preview_large.short_description = 'Изображение'

    def has_answer(self, obj):
        if obj.answer:
            return format_html('✅ <span style="color: #28a745;">Да</span>')
        return format_html('❌ <span style="color: #dc3545;">Нет</span>')

    has_answer.short_description = 'Есть ответ'

    def delete_selected_answers(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'Удалено {count} ответов.')

    delete_selected_answers.short_description = "Удалить выбранные ответы"


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = [
        'inviter_display', 'invited_display', 'used_display',
        'created_at', 'days_since_created'
    ]
    list_filter = [
        'used', 'created_at',
        'inviter__is_admin', 'invited__is_admin'
    ]
    search_fields = [
        'inviter__username', 'inviter__user',
        'invited__username', 'invited__user'
    ]
    readonly_fields = ['created_at', 'days_since_created']

    fieldsets = (
        ('Информация о реферале', {
            'fields': ('inviter', 'invited', 'used')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'days_since_created'),
            'classes': ('collapse',)
        }),
    )

    actions = ['export_as_csv', 'mark_as_used', 'mark_as_unused']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('inviter', 'invited')

    def inviter_display(self, obj):
        username = f"@{obj.inviter.username}" if obj.inviter.username else str(obj.inviter.user)
        admin_badge = " 👑" if obj.inviter.is_admin else ""
        return format_html(
            '<a href="{}">{}{}</a>',
            reverse('admin:v1_tgusers_change', args=[obj.inviter.id]),
            username,
            admin_badge
        )

    inviter_display.short_description = 'Пригласивший'
    inviter_display.admin_order_field = 'inviter__username'

    def invited_display(self, obj):
        username = f"@{obj.invited.username}" if obj.invited.username else str(obj.invited.user)
        admin_badge = " 👑" if obj.invited.is_admin else ""
        return format_html(
            '<a href="{}">{}{}</a>',
            reverse('admin:v1_tgusers_change', args=[obj.invited.id]),
            username,
            admin_badge
        )

    invited_display.short_description = 'Приглашенный'
    invited_display.admin_order_field = 'invited__username'

    def used_display(self, obj):
        if obj.used:
            return format_html('✅ <span style="color: #28a745; font-weight: bold;">Использован</span>')
        return format_html('⏳ <span style="color: #ffc107; font-weight: bold;">Ожидает</span>')

    used_display.short_description = 'Статус'
    used_display.admin_order_field = 'used'

    def days_since_created(self, obj):
        days = (now() - obj.created_at).days
        if days == 0:
            return "Сегодня"
        elif days == 1:
            return "Вчера"
        else:
            return f"{days} дн. назад"

    days_since_created.short_description = 'Давность'

    def mark_as_used(self, request, queryset):
        queryset.update(used=True)

    mark_as_used.short_description = "Отметить как использованные"

    def mark_as_unused(self, request, queryset):
        queryset.update(used=False)

    mark_as_unused.short_description = "Отметить как неиспользованные"


admin.site.site_header = "🚀 Управление системой"
admin.site.site_title = "Admin Panel"
admin.site.index_title = "Добро пожаловать в панель управления"