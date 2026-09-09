from django.shortcuts import render
from main.models import Experience
from django.utils.dateparse import parse_datetime

def show_main(request):
    context = {
        "name": "Muhammad Faza Aqila",
        "npm": "2506613142",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Hello! I am Muhammad Faza Aqila, a Computer Science undergraduate at Universitas Indonesia. "
            "My core interests lie deeply at the intersection of Data Science and modern Web Development. "
            "I am passionate about extracting meaningful insights from complex, raw data to drive informed decisions, "
            "and translating those findings into intuitive, user-friendly web applications."
        ),
    }
    return render(request, "index.html", context)

def show_experience(request):
    # Trik Auto-Populate: Menyuntikkan seluruh 6 kartu jika database kosong
    if not Experience.objects.exists():
        # 1. COMPFEST 18
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

        # 2. BETIS Fasilkom UI
        e2 = Experience.objects.create(
            title="BETIS Fasilkom UI", 
            role="VPIC of Operational", 
            description="Oversaw daily operational workflows, managed equipment procurement, and ensured all logistical requirements were executed on schedule.", 
            category="volunteer", 
            thumbnail="/static/img/exp-betis.jpeg", 
            logo="/static/img/logo-betis.jpg"
        )
        e2.started_at = parse_datetime("2026-02-01T00:00:00Z")
        e2.ended_at = parse_datetime("2026-07-01T00:00:00Z")
        e2.save()

        # 3. Open House Fasilkom UI
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

        # 4. DDP0
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

        # 5. Nabastala Production
        e5 = Experience.objects.create(
            title="Nabastala Production", 
            role="Producer", 
            description="Supervised production timelines, managed essential equipment logistics, and coordinated team distributions for successful project delivery.", 
            category="freelance", 
            thumbnail="/static/img/exp-nabastala.jpeg", 
            logo="/static/img/logo-nabastala.jpeg"
        )
        e5.started_at = parse_datetime("2023-07-01T00:00:00Z")
        e5.ended_at = parse_datetime("2023-12-01T00:00:00Z")
        e5.save()

        # 6. RISMANSA
        e6 = Experience.objects.create(
            title="RISMANSA", 
            role="Head Division of PSDI", 
            description="Designed comprehensive event programs and collaborated closely with cross-functional divisions to ensure smooth and successful event executions.", 
            category="volunteer", 
            thumbnail="/static/img/exp-rismansa.jpeg", 
            logo="/static/img/logo-risma.jpg"
        )
        e6.started_at = parse_datetime("2023-07-01T00:00:00Z")
        e6.ended_at = parse_datetime("2024-07-01T00:00:00Z")
        e6.save()

    context = {
        "name": "Faza",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)