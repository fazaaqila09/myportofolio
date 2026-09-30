from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_datetime
from datetime import date, datetime
from django.utils import timezone
from django.views.decorators.http import require_POST
from main.models import Experience, Education, Project
from main.forms import ExperienceForm, ProjectForm


EDITOR_GROUP = "Editor"


def is_editor(user):
    """True jika user sudah login dan tergabung dalam grup 'Editor'
    (grup dibuat dan diisi lewat Django Admin)."""
    return user.is_authenticated and user.groups.filter(name=EDITOR_GROUP).exists()


def can_edit(user):
    """Hak mengubah data: pemilik portofolio (superuser) atau Editor.
    Membuat dan menghapus data tetap khusus superuser."""
    return user.is_superuser or is_editor(user)


def is_ajax(request):
    """True jika permintaan dikirim lewat fetch() dari star.js."""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def toggle_star_for(request, obj, fallback_url_name):
    """Tambah/batalkan star milik user yang sedang login pada obj (Project/Experience).

    Permintaan AJAX dijawab JSON supaya halaman tidak perlu reload;
    permintaan biasa tetap di-redirect seperti sebelumnya."""
    if not request.user.is_authenticated:
        if is_ajax(request):
            return JsonResponse(
                {"message": "Login dulu untuk memberi star.", "login_url": "/login/"},
                status=401,
            )
        return redirect_to_login(request.get_full_path(), login_url="/login/")

    if request.method == "POST":
        # Sudah pernah di-star akun ini -> batalkan; belum -> tambahkan.
        if request.user in obj.starred_by.all():
            obj.starred_by.remove(request.user)
        else:
            obj.starred_by.add(request.user)

    if is_ajax(request):
        starred_users = list(obj.starred_by.all())
        return JsonResponse({
            "is_starred": request.user in starred_users,
            "star_count": len(starred_users),
            "starred_by_names": ", ".join(u.username for u in starred_users),
        })
    return redirect(fallback_url_name)


def show_main(request):
    last_login = request.COOKIES.get("last_login", "Belum ada sesi login / Cookie tidak ditemukan")
    context = {
        "name": "Muhammad Faza Aqila",
        "npm": "2506613142",
        "study_program": "Computer Science",
        "bio": (
            "Hello! I am Muhammad Faza Aqila, a Computer Science undergraduate at Universitas Indonesia. "
            "My core interests lie deeply at the intersection of Data Science and modern Web Development. "
            "I am passionate about extracting meaningful insights from complex, raw data to drive informed decisions, "
            "and translating those findings into intuitive, user-friendly web applications."
        ),
        "last_login": last_login,
        "education_list": get_education_list(),
    }
    return render(request, "index.html", context)


def show_experience(request):
    if not Experience.objects.exists():
        e1 = Experience.objects.create(
            title="COMPFEST 18",
            role="VPIC of Transportation & Venue",
            description="Managed venue logistics and coordinated transportation schedules to ensure the timely distribution of event equipment.",
            category="committee",
            thumbnail="/static/img/exp-cf.jpg",
            logo="/static/img/logo-cf.png"
        )
        e1.started_at = parse_datetime("2026-04-01T00:00:00Z")
        e1.save()

        e2 = Experience.objects.create(
            title="BETIS Fasilkom UI",
            role="VPIC of Operational",
            description="Oversaw daily operational workflows, managed equipment procurement, and ensured all logistical requirements were executed on schedule.",
            category="committee",
            thumbnail="/static/img/exp-betis.jpeg",
            logo="/static/img/logo-betis.png"
        )
        e2.started_at = parse_datetime("2026-02-01T00:00:00Z")
        e2.ended_at = parse_datetime("2026-07-01T00:00:00Z")
        e2.save()

        e3 = Experience.objects.create(
            title="Open House Fasilkom UI",
            role="VPIC of Operational",
            description="Directed operational preparations and coordinated cross-team equipment distribution to guarantee a seamless event execution.",
            category="committee",
            thumbnail="/static/img/exp-oh.jpg",
            logo="/static/img/logo-oh.png"
        )
        e3.started_at = parse_datetime("2026-08-01T00:00:00Z")
        e3.save()

        e4 = Experience.objects.create(
            title="DDP0",
            role="Mentor",
            description="Mentored students, managed class logistics, and provided guidance for foundational programming concepts.",
            category="volunteer",
            thumbnail="/static/img/exp-ddp0.jpeg",
            logo="/static/img/logo-ddp0.png"
        )
        e4.started_at = parse_datetime("2026-07-01T00:00:00Z")
        e4.ended_at = parse_datetime("2026-08-01T00:00:00Z")
        e4.save()

        e5 = Experience.objects.create(
            title="Nabastala Production",
            role="Producer",
            description="Supervised production timelines, managed essential equipment logistics, and coordinated team distributions for successful project delivery.",
            category="organization",
            thumbnail="/static/img/exp-nabastala.jpeg",
            logo="/static/img/logo-nabastala.png"
        )
        e5.started_at = parse_datetime("2023-07-01T00:00:00Z")
        e5.ended_at = parse_datetime("2023-12-01T00:00:00Z")
        e5.save()

        e6 = Experience.objects.create(
            title="RISMANSA",
            role="Head Division of PSDI",
            description="Designed comprehensive event programs and collaborated closely with cross-functional divisions to ensure smooth and successful event executions.",
            category="organization",
            thumbnail="/static/img/exp-rismansa.jpeg",
            logo="/static/img/logo-risma.png"
        )
        e6.started_at = parse_datetime("2023-07-01T00:00:00Z")
        e6.ended_at = parse_datetime("2024-07-01T00:00:00Z")
        e6.save()

    json_response = get_experience_json(request)
    experience_list = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    experience_list = [item.object for item in experience_list]

    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Faza",
        "experience_list": experience_list,
        "title_query": title_query,
        "can_edit": can_edit(request.user),
    }
    return render(request, "experience.html", context)


@login_required(login_url="/login/")
def create_experience(request):
    # Hanya pemilik portofolio (superuser) yang boleh menambah data.
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        experience = form.save(commit=False)
        experience.save()  # INSERT pertama -> auto_now_add mengisi started_at = sekarang
        started_date = form.cleaned_data["started_at"]
        experience.started_at = timezone.make_aware(datetime.combine(started_date, datetime.min.time()))
        experience.save()  # UPDATE -> pakai tanggal dari form (jam otomatis 00:00)
        messages.success(request, "New experience added successfully!")
        return redirect("main:show_experience")

    context = {
        "name": "Faza",
        "form": form,
    }
    return render(request, "experience_form.html", context)


@login_required(login_url="/login/")
def update_experience(request, experience_id):
    # Pemilik (superuser) dan Editor boleh mengubah data.
    if not can_edit(request.user):
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)
    # started_at bukan field model yang bisa diedit (auto_now_add), jadi
    # diisi manual ke form sebagai tanggal awal.
    initial = {"started_at": timezone.localtime(experience.started_at).date()}
    form = ExperienceForm(request.POST or None, instance=experience, initial=initial)

    if request.method == "POST" and form.is_valid():
        experience = form.save(commit=False)
        started_date = form.cleaned_data["started_at"]
        experience.started_at = timezone.make_aware(datetime.combine(started_date, datetime.min.time()))
        experience.save()
        messages.success(request, "Experience updated successfully!")
        return redirect("main:show_experience")

    context = {
        "name": "Faza",
        "form": form,
        "experience": experience,
    }
    return render(request, "experience_form.html", context)


def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experience = Experience.objects.all()

    if title_query:
        experience = experience.filter(title__icontains=title_query)

    # use_natural_foreign_keys: starred_by berisi username, bukan id database.
    experience_json = serializers.serialize(
        "json", experience, use_natural_foreign_keys=True
    )
    return HttpResponse(experience_json, content_type="application/json")


@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    # Hanya pemilik portofolio (superuser) yang boleh menghapus data.
    if not request.user.is_superuser:
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        experience.delete()
        messages.success(request, "Experience deleted successfully!")
    return redirect("main:show_experience")


# Semua akun yang sudah login boleh memberi star (tanpa cek peran).
def toggle_star_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    return toggle_star_for(request, experience, "main:show_experience")


def get_education_list():
    """Isi data awal (sekali saja) lalu kembalikan semua riwayat pendidikan."""
    if not Education.objects.exists():
        Education.objects.create(
            school="Universitas Indonesia",
            major="Bachelor of Computer Science",
            level="bachelor",
            logo="/static/img/logo-ui.png",
            started_at=date(2025, 8, 1),
        )
        Education.objects.create(
            school="Universitas Diponegoro",
            major="Bachelor of Computer Science",
            level="bachelor",
            logo="/static/img/logo-undip.png",
            started_at=date(2024, 8, 1),
            ended_at=date(2025, 6, 1),
        )
        Education.objects.create(
            school="SMAN 1 Kota Serang",
            major="Senior High School (STEM)",
            level="senior",
            logo="/static/img/logo-sma.png",
            started_at=date(2021, 7, 1),
            ended_at=date(2024, 6, 1),
        )
        Education.objects.create(
            school="SMPN 1 Kota Serang",
            major="Middle High School",
            level="junior",
            logo="/static/img/logo-smp.png",
            started_at=date(2018, 7, 1),
            ended_at=date(2021, 6, 1),
        )
    return Education.objects.all()


def show_education(request):
    context = {
        "name": "Faza",
        "education_list": get_education_list(),
    }
    return render(request, "education.html", context)


def show_projects(request):
    # Data proyek tidak lagi dikirim lewat context: halaman mengambilnya
    # sendiri lewat AJAX ke get_project_json.
    context = {
        "name": "Faza",
        "search_query": request.GET.get("q", "").strip(),
        "can_edit": can_edit(request.user),
        "form": ProjectForm(),  # form kosong untuk modal Add Project
    }
    return render(request, "projects.html", context)


@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "New project added successfully!")
        return redirect("main:show_projects")

    context = {
        "name": "Faza",
        "form": form,
        "can_edit": can_edit(request.user),
    }
    return render(request, "project_form.html", context)


@login_required(login_url="/login/")
def update_project(request, project_id):
    if not can_edit(request.user):
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project updated successfully!")
        return redirect("main:show_projects")

    context = {
        "name": "Faza",
        "form": form,
        "project": project,
    }
    return render(request, "project_form.html", context)

def get_project_json(request):
    search_query = request.GET.get("q", "").strip()
    projects = Project.objects.prefetch_related("starred_by")

    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    # JSON dirakit manual (bukan serializers.serialize) supaya bisa memuat
    # is_starred, yaitu status star untuk user yang sedang login.
    data = []
    for project in projects:
        starred_users = list(project.starred_by.all())
        is_starred = request.user.is_authenticated and request.user in starred_users

        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "category": project.category,
                "category_display": project.get_category_display(),
                "thumbnail": project.thumbnail or "",
                "project_url": project.project_url,
                "starred_by": [[u.username] for u in starred_users],  # hanya username
                "star_count": len(starred_users),
                "is_starred": is_starred,
                "starred_by_names": ", ".join(u.username for u in starred_users),
            },
        })

    return JsonResponse(data, safe=False)


@require_POST
def create_project_ajax(request):
    # Tanpa @login_required: dekorator itu me-redirect ke halaman login (HTML, status 200
    # setelah diikuti fetch), sehingga JavaScript tidak bisa mengenali kegagalannya.
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)},
            status=201,
        )

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully!")
    return redirect("main:show_projects")


# Tanpa cek is_superuser: semua akun yang sudah login boleh memberi star
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return toggle_star_for(request, project, "main:show_projects")


def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Faza",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie("last_login", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return response

    context = {
        "name": "Faza",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response