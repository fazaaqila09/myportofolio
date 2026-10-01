from django.contrib import admin

from main.models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Kotak masuk pesan dari halaman Contact."""

    list_display = ("subject", "name", "email", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    list_editable = ("is_read",)
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at")
    date_hierarchy = "created_at"