from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import render

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