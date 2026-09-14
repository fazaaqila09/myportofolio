from django.shortcuts import render
from main.models import Experience, Education
from django.utils.dateparse import parse_datetime
from datetime import date

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
            logo="/static/img/logo-betis.png"
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
            logo="/static/img/logo-nabastala.png"
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
            logo="/static/img/logo-risma.png"
        )
        e6.started_at = parse_datetime("2023-07-01T00:00:00Z")
        e6.ended_at = parse_datetime("2024-07-01T00:00:00Z")
        e6.save()

    context = {
        "name": "Faza",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


def show_education(request):
    # Auto-populate: isi 3 riwayat pendidikan kalau database masih kosong.
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