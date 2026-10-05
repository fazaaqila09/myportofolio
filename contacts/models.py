from django.db import models


class Contact(models.Model):
    """Kontak untuk Tutorial 6 (HTMX)."""

    name = models.CharField(max_length=100)
    email = models.EmailField()

    class Meta:
        # Urutan tetap (sesuai waktu dibuat), supaya baris tidak berpindah setelah diedit.
        ordering = ["id"]

    def __str__(self):
        return self.name