from django.shortcuts import render
from main.models import Experience

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
    context = {
        "name": "Muhammad Faza Aqila",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)