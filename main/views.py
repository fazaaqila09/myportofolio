from django.conf import settings
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_datetime
from datetime import date, datetime
from django.utils import timezone
from main.models import Experience, Education, Project
from main.forms import ExperienceForm, ProjectForm


def is_authorized(request):
    """Cek kode rahasia: dari header (buat klien non-browser seperti
    Postman/fetch) atau dari field form 'secret_key' (buat form HTML
    biasa yang nggak bisa set custom header tanpa JavaScript)."""
    secret = getattr(settings, "PORTFOLIO_SECRET_KEY", "")
    if not secret:
        return False
    provided = request.POST.get("secret_key") or request.headers.get("X-Portfolio-Key", "")
    return provided == secret


def show_main(request):
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
    }
    return render(request, "index.html", context)


def show_experience(request):
    if not Experience.objects.exists():
        e1 = Experience.objects.create(
            title="COMPFEST 18",
            role="VPIC of Transportation & Venue",
            description="Managed venue logistics and coordinated transportation schedules to ensure the timely distribution of event equipment.",
            category="volunteer",
            thumbnail="/static/img/exp-cf.jpg",
            logo="/static/img/logo-cf.png"
        )
        e1.started_at = parse_datetime("2026-04-01T00:00:00Z")
        e1.save()

        e2 = Experience.objects.create(
            title="BETIS Fasilkom UI",
            role="VPIC of Operational",
            description="Oversaw daily operational workflows, managed equipment procurement, and ensured all logistical requirements were executed on schedule.",
            category="volunteer",
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
            category="volunteer",
            thumbnail="/static/img/exp-oh.jpg",
            logo="/static/img/logo-oh.png"
        )
        e3.started_at = parse_datetime("2026-08-01T00:00:00Z")
        e3.save()

        e4 = Experience.objects.create(
            title="DDP0",
            role="Mentor",
            description="Mentored students, managed class logistics, and provided guidance for foundational programming concepts.",
            category="part-time",
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
            category="freelance",
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
            category="volunteer",
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
    }
    return render(request, "experience.html", context)


def create_experience(request):
    form = ExperienceForm(request.POST or None)
    auth_error = None

    if request.method == "POST":
        if not is_authorized(request):
            auth_error = "Invalid access code."
        elif form.is_valid():
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
        "auth_error": auth_error,
    }
    return render(request, "experience_form.html", context)


def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experience = Experience.objects.all()

    if title_query:
        experience = experience.filter(title__icontains=title_query)

    experience_json = serializers.serialize("json", experience)
    return HttpResponse(experience_json, content_type="application/json")


def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        if not is_authorized(request):
            messages.error(request, "Invalid access code. Experience was not deleted.")
            return redirect("main:show_experience")
        experience.delete()
        messages.success(request, "Experience deleted successfully!")
    return redirect("main:show_experience")


def show_education(request):
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

    context = {
        "name": "Faza",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)

def show_projects(request):
    json_response = get_project_json(request)
    project_list = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    project_list = [item.object for item in project_list]

    category_query = request.GET.get("category", "").strip()

    context = {
        "name": "Faza",
        "project_list": project_list,
        "category_query": category_query,
    }
    return render(request, "projects.html", context)


def create_project(request):
    form = ProjectForm(request.POST or None)
    auth_error = None

    if request.method == "POST":
        if not is_authorized(request):
            auth_error = "Invalid access code."
        elif form.is_valid():
            form.save()
            messages.success(request, "New project added successfully!")
            return redirect("main:show_projects")

    context = {
        "name": "Faza",
        "form": form,
        "auth_error": auth_error,
    }
    return render(request, "project_form.html", context)


def update_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)
    auth_error = None

    if request.method == "POST":
        if not is_authorized(request):
            auth_error = "Invalid access code."
        elif form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully!")
            return redirect("main:show_projects")

    context = {
        "name": "Faza",
        "form": form,
        "project": project,
        "auth_error": auth_error,
    }
    return render(request, "project_form.html", context)


def get_project_json(request):
    category_query = request.GET.get("category", "").strip()
    projects = Project.objects.all()

    if category_query:
        projects = projects.filter(category__icontains=category_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")


def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        if not is_authorized(request):
            messages.error(request, "Invalid access code. Project was not deleted.")
            return redirect("main:show_projects")
        project.delete()
        messages.success(request, "Project deleted successfully!")
    return redirect("main:show_projects")