import json
import uuid
from django.db import models
from django.contrib.auth.models import User

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('organization', 'Organization'),
        ('committee', 'Committee'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('internship', 'Internship'),
    ]
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    role = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    # Terjemahan Bahasa Indonesia (opsional). Kosong = pakai teks Inggris di atas.
    role_indo = models.CharField("Role (Indonesian)", max_length=100, blank=True, default="")
    description_indo = models.TextField("Description (Indonesian)", blank=True, default="")
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    # Foto dokumentasi tambahan (satu URL per baris). Foto utama tetap `thumbnail`;
    # semuanya bisa digeser di lightbox pada kartu Experience yang sama.
    photos = models.TextField("More photos (one URL per line)", blank=True, default="")
    logo = models.URLField(blank=True, null=True) 
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    starred_by = models.ManyToManyField(
        User, related_name="starred_experiences", blank=True
    )
    
    
    def __str__(self):
        return self.title
        
    @property
    def is_ongoing(self):
        return self.ended_at is None

    @property
    def all_photos(self):
        """Semua foto kegiatan ini: foto utama dulu, lalu foto tambahan (tanpa duplikat)."""
        urls = [self.thumbnail] if self.thumbnail else []
        for line in (self.photos or "").splitlines():
            line = line.strip()
            if line and line not in urls:
                urls.append(line)
        return urls

    @property
    def photos_json(self):
        """all_photos sebagai teks JSON, untuk atribut data-photos di template."""
        return json.dumps(self.all_photos)

class Education(models.Model):
    """Riwayat pendidikan (timeline di section Education).
    Tanggal memakai DateField biasa (bukan auto_now_add) supaya bisa diisi tahun yang sebenarnya."""

    LEVEL_CHOICES = [
        ('elementary', 'Elementary School'),
        ('junior', 'Junior High School'),
        ('senior', 'Senior High School'),
        ('bachelor', "Bachelor's Degree"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.CharField(max_length=255)
    major = models.CharField(max_length=255, null=True, blank=True)
    # Terjemahan Bahasa Indonesia (opsional). Kosong = pakai teks Inggris di atas.
    major_indo = models.CharField("Major (Indonesian)", max_length=255, blank=True, default="")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='bachelor')
    logo = models.URLField(blank=True, null=True)
    started_at = models.DateField()
    ended_at = models.DateField(blank=True, null=True)

    class Meta:
        # Terbaru di atas — sesuai urutan timeline yang sekarang
        ordering = ['-started_at']

    def __str__(self):
        return self.school

    @property
    def is_ongoing(self):
        return self.ended_at is None

class Project(models.Model):
    CATEGORY_CHOICES = [
        ("film", "Film & Video"),
        ("software", "Software / Web"),
        ("design", "Design"),
        ("writing", "Writing"),
        ("music", "Music / Audio"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    # Terjemahan Bahasa Indonesia (opsional). Kosong = pakai teks Inggris di atas.
    title_indo = models.CharField("Title (Indonesian)", max_length=255, blank=True, default="")
    description_indo = models.TextField("Description (Indonesian)", blank=True, default="")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    thumbnail = models.URLField(blank=True, null=True)
    project_url = models.URLField()
    starred_by = models.ManyToManyField(
        User, related_name="starred_projects", blank=True
    )

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    """Pesan dari halaman Contact. Dibaca pemilik di halaman Inbox (tanpa kirim email)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}: {self.subject}"