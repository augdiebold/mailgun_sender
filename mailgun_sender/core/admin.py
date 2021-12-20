from django.contrib import admin
from django.utils.html import format_html

from mailgun_sender.core.models import Email


class EmailModelAdmin(admin.ModelAdmin):
    exclude = ('status', 'json_response')
    list_display = ('subject', '_from', 'to', 'colored_status', 'sent_at')
    search_fields = ('subject', '_from', 'to')
    date_hierarchy = 'sent_at'
    list_filter = ('status', 'sent_at')
    actions = ['send_again']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            # All model fields as read_only
            return self.readonly_fields + tuple([field.name for field in obj._meta.fields])
        return self.readonly_fields

    def colored_status(self, obj):
        """Change font color of displayed status"""
        colors = {
            '2': 'green',
            '1': 'orange',
            '3': 'red',
        }

        return format_html(
            '<b style="color:{};">{}</b>',
            colors[obj.status],
            obj.get_status_display(),
        )

    colored_status.short_description = 'Status'
    colored_status.admin_order_field = 'status'

    def send_again(self, request, queryset):
        """Action that create and send again all selected Email objects."""

        for obj in queryset:
            obj.pk = None
            obj.status = '1'
            obj.json_response = None

            obj.save()

        count = queryset.count()

        if count == 1:
            msg = '{} email added.'
        else:
            msg = '{} emails added.'

        self.message_user(request, msg.format(count))


admin.site.register(Email, EmailModelAdmin)
