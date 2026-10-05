from django import forms

from .models import Contact


class ContactForm(forms.ModelForm):
    """Validasi data kontak (nama wajib, email harus valid)."""

    class Meta:
        model = Contact
        fields = ["name", "email"]