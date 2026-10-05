from functools import wraps

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, QueryDict
from django.shortcuts import get_object_or_404, render
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


@owner_only
@require_http_methods(["DELETE"])
def contact_delete(request, pk):
    """Balasan kosong (status 200) membuat HTMX menghapus baris tersebut."""
    contact = get_object_or_404(Contact, pk=pk)
    contact.delete()
    return HttpResponse("")


@owner_only
def contact_search(request):
    """Baris yang namanya mengandung kata kunci (tanpa membedakan huruf besar/kecil)."""
    query = request.GET.get("q", "").strip()
    contacts = Contact.objects.filter(name__icontains=query) if query else Contact.objects.all()
    return render(request, "contacts/_contact_rows.html", {"contacts": contacts})


@owner_only
def contact_edit(request, pk):
    """Baris versi form edit."""
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, "contacts/_contact_edit_row.html", {"contact": contact})


@owner_only
def contact_row(request, pk):
    """Baris versi tampilan biasa (dipakai tombol Batal)."""
    contact = get_object_or_404(Contact, pk=pk)
    return render(request, "contacts/_contact_row.html", {"contact": contact})


@owner_only
@require_http_methods(["PUT"])
def contact_update(request, pk):
    """Data PUT tidak masuk ke request.POST, jadi dibaca dari request.body lewat QueryDict."""
    contact = get_object_or_404(Contact, pk=pk)
    data = QueryDict(request.body)
    form = ContactForm(data, instance=contact)
    if not form.is_valid():
        # Data tidak valid: baris tetap dalam mode edit
        return render(request, "contacts/_contact_edit_row.html", {"contact": contact})
    form.save()
    return render(request, "contacts/_contact_row.html", {"contact": contact})