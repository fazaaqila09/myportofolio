import uuid
from django.db import models

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    role = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    logo = models.URLField(blank=True, null=True) 
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    
    
    def __str__(self):
        return self.title
        
    @property
    def is_ongoing(self):
        return self.ended_at is None

class Education(models.Model):
    """Riwayat pendidikan, ditampilkan sebagai timeline di halaman Education.

    Catatan soal tanggal: di sini dipakai DateField BIASA, bukan
    DateTimeField(auto_now_add=True) seperti pada Experience.
    auto_now_add memaksa nilainya diisi waktu saat data dibuat dan
    TIDAK BISA diubah lewat admin — itu sebabnya di views Experience
    tanggalnya harus ditimpa manual setelah create(). DateField biasa
    bisa langsung diisi tahun masuk yang sebenarnya.
    """

    LEVEL_CHOICES = [
        ('elementary', 'Elementary School'),
        ('junior', 'Junior High School'),
        ('senior', 'Senior High School'),
        ('bachelor', "Bachelor's Degree"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.CharField(max_length=255)
    major = models.CharField(max_length=255, null=True, blank=True)
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
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    thumbnail = models.URLField(blank=True, null=True)
    project_url = models.URLField()

    def __str__(self):
        return self.title