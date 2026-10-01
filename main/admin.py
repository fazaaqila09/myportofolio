from django.contrib import admin

from main.models import ContactMessage, Education


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Kotak masuk pesan dari halaman Contact."""

    list_display = ("subject", "name", "email", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    list_editable = ("is_read",)
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("name", "email", "subject", "message", "created_at")
    date_hierarchy = "created_at"


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    """Riwayat pendidikan (termasuk terjemahan jurusan ke Bahasa Indonesia)."""

    list_display = ("school", "major", "major_indo", "level", "started_at", "ended_at")
    list_filter = ("level",)
    search_fields = ("school", "major", "major_indo")