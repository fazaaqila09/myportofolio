from datetime import datetime, time

from django.utils import timezone
from django.utils.html import strip_tags
from rest_framework import serializers

from main.forms import clean_photo_urls
from main.models import Experience, Project


def clean_text(value, empty_message=None):
    """Buang tag HTML dan spasi di ujung teks (setara clean_<field> pada form).

    Jika `empty_message` diisi, teks yang kosong setelah dibersihkan ditolak
    dengan pesan tersebut (misalnya judul yang hanya berisi tag HTML).
    """
    cleaned = strip_tags(value or "").strip()
    if empty_message and not cleaned:
        raise serializers.ValidationError(empty_message)
    return cleaned


class StarInfoMixin(serializers.Serializer):
    """Informasi star (Tugas 4) sebagai field hasil perhitungan yang read-only.

    Dipakai bersama oleh ProjectSerializer dan ExperienceSerializer. Model yang
    memakainya harus punya relasi `starred_by` ke User. Hanya username yang
    ditampilkan; email dan password hash tidak pernah ikut dikirim.
    """

    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    # .all() memakai cache prefetch_related("starred_by") dari view, jadi tidak
    # ada query tambahan per baris saat menampilkan daftar.
    def get_star_count(self, obj):
        return len(obj.starred_by.all())

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return any(user.pk == request.user.pk for user in obj.starred_by.all())

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class DateOnlyField(serializers.DateField):
    """Tanggal saja ("YYYY-MM-DD") untuk kolom DateTimeField di model.

    Experience menyimpan started_at/ended_at sebagai DateTimeField, tetapi form
    dan halaman hanya memakai tanggal. Saat dibaca, waktu dibuang; saat ditulis,
    tanggal diubah menjadi pukul 00.00 di zona waktu proyek (sama seperti
    set_start_date pada view lama).
    """

    def to_representation(self, value):
        if isinstance(value, datetime):
            value = timezone.localtime(value).date()
        return super().to_representation(value)

    def to_internal_value(self, value):
        day = super().to_internal_value(value)
        return timezone.make_aware(datetime.combine(day, time.min))


class ProjectSerializer(StarInfoMixin, serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id", "title", "title_indo", "description", "description_indo",
            "category", "category_display", "thumbnail", "project_url",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    # Validasi sepadan dengan clean_* di ProjectForm, karena input API
    # tidak melewati form tersebut.
    def validate_title(self, value):
        return clean_text(value, "Title cannot be empty.")

    def validate_description(self, value):
        return clean_text(value)

    def validate_title_indo(self, value):
        return clean_text(value)

    def validate_description_indo(self, value):
        return clean_text(value)


class ExperienceSerializer(StarInfoMixin, serializers.ModelSerializer):
    """Representasi dan validasi Experience untuk API /api/v1/experience/.

    Aturan validasinya sama dengan ExperienceForm (Tugas 3 & 5) supaya data yang
    masuk lewat API dan lewat halaman HTML diperlakukan sama.
    """

    category_display = serializers.CharField(source="get_category_display", read_only=True)
    # `photos` = teks mentah (satu URL per baris) untuk diedit;
    # `all_photos` = daftar siap pakai untuk lightbox (foto utama + tambahan).
    all_photos = serializers.ListField(child=serializers.CharField(), read_only=True)
    started_at = DateOnlyField()
    ended_at = DateOnlyField(required=False, allow_null=True)
    is_ongoing = serializers.BooleanField(read_only=True)

    class Meta:
        model = Experience
        fields = [
            "id", "title", "role", "role_indo", "description", "description_indo",
            "category", "category_display", "thumbnail", "logo", "photos", "all_photos",
            "started_at", "ended_at", "is_ongoing",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    # validate_<field>: padanan clean_<field> di ExperienceForm
    def validate_title(self, value):
        return clean_text(value, "Organization / activity name cannot contain only HTML tags.")

    def validate_role(self, value):
        return clean_text(value)

    def validate_role_indo(self, value):
        return clean_text(value)

    def validate_description(self, value):
        return clean_text(value, "Description cannot contain only HTML tags.")

    def validate_description_indo(self, value):
        return clean_text(value)

    def validate_photos(self, value):
        return clean_photo_urls(value)

    def validate(self, attrs):
        # Pada PATCH, tanggal yang tidak dikirim diambil dari data yang tersimpan.
        started = attrs.get("started_at", getattr(self.instance, "started_at", None))
        ended = attrs.get("ended_at", getattr(self.instance, "ended_at", None))
        if started and ended and ended < started:
            raise serializers.ValidationError(
                {"ended_at": "End date cannot be earlier than the start date."}
            )
        return attrs

    def create(self, validated_data):
        # started_at memakai auto_now_add, yang selalu menimpa nilainya saat INSERT.
        # Karena itu tanggal dari klien disimpan lewat UPDATE setelah data dibuat.
        started_at = validated_data.pop("started_at")
        experience = super().create(validated_data)
        experience.started_at = started_at
        experience.save(update_fields=["started_at"])
        return experience
