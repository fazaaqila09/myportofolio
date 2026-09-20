from django import forms
from django.forms import ModelForm, TextInput, Textarea, URLInput, Select, DateInput
from main.models import Experience, Project


class ExperienceForm(ModelForm):
    started_at = forms.DateField(
        label="Start Date",
        widget=DateInput(attrs={"type": "date"}),
    )

    field_order = ["title", "role", "description", "category", "thumbnail", "logo", "started_at", "ended_at"]

    class Meta:
        model = Experience
        fields = ["title", "role", "description", "category", "thumbnail", "logo", "ended_at"]
        labels = {
            "title": "Organization / Activity Name",
            "role": "Role / Position",
            "description": "Description",
            "category": "Category",
            "thumbnail": "Documentation Photo URL",
            "logo": "Logo URL",
            "ended_at": "End Date (leave blank if ongoing)",
        }
        widgets = {
            "title": TextInput(attrs={"placeholder": "COMPFEST 18"}),
            "role": TextInput(attrs={"placeholder": "VPIC of Transportation"}),
            "description": Textarea(attrs={"rows": 3, "placeholder": "Tell us about your experience"}),
            "category": Select(),
            "thumbnail": URLInput(attrs={"placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000"}),
            "logo": URLInput(attrs={"placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000"}),
            "ended_at": DateInput(attrs={"type": "date"}),
        }

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "category", "project_url", "completed_at"]
        labels = {
            "title": "Project Name",
            "description": "Description",
            "category": "Category",
            "project_url": "Project URL (optional)",
            "completed_at": "Completion Date (leave blank if ongoing)",
        }
        widgets = {
            "title": TextInput(attrs={"placeholder": "Nabastala"}),
            "description": Textarea(attrs={"rows": 3, "placeholder": "Tell us about this project"}),
            "category": Select(),
            "project_url": URLInput(attrs={"placeholder": "https://youtube.com/..."}),
            "completed_at": DateInput(attrs={"type": "date"}),
        }