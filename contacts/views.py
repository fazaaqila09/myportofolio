from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import ContactForm
from .models import Contact


def owner_only(view):
    """Hanya pemilik portofolio (superuser) yang boleh memakai halaman Kontak."""
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


@owner_only
def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, "contacts/index.html", {"contacts": contacts})


@owner_only
@require_http_methods(["POST"])
def contact_add(request):
    """Simpan kontak baru, lalu kirim ulang semua baris (bukan halaman utuh)."""
    form = ContactForm(request.POST)
    if form.is_valid():
        form.save()
    contacts = Contact.objects.all()
    return render(request, "contacts/_contact_rows.html", {"contacts": contacts})