from django.contrib import admin
from .models import History

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'content_type',
        'object_id',
        'action_flag',
        'change_message',
        'date',
    )
# Register your models here.
