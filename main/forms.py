from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.html import strip_tags
from django.forms import ModelForm, TextInput, Textarea, URLInput, Select, DateInput
from main.models import ContactMessage, Experience, Project


class ExperienceForm(ModelForm):
    started_at = forms.DateField(
        label="Start Date",
        widget=DateInput(attrs={"type": "date"}),
    )

    field_order = ["title", "role", "role_indo", "description", "description_indo", "category", "thumbnail", "photos", "logo", "started_at", "ended_at"]

    class Meta:
        model = Experience
        fields = ["title", "role", "role_indo", "description", "description_indo", "category", "thumbnail", "photos", "logo", "ended_at"]
        labels = {
            "title": "Organization / Activity Name",
            "role": "Role / Position",
            "role_indo": "Role / Position (Indonesian, optional)",
            "description": "Description",
            "description_indo": "Description (Indonesian, optional)",
            "category": "Category",
            "thumbnail": "Documentation Photo URL",
            "photos": "More Photo URLs (one per line, optional)",
            "logo": "Logo URL",
            "ended_at": "End Date (leave blank if ongoing)",
        }
        widgets = {
            "title": TextInput(attrs={"placeholder": "COMPFEST 18"}),
            "role": TextInput(attrs={"placeholder": "VPIC of Transportation"}),
            "role_indo": TextInput(attrs={"placeholder": "VPIC Transportasi"}),
            "description": Textarea(attrs={"rows": 3, "placeholder": "Tell us about your experience"}),
            "description_indo": Textarea(attrs={"rows": 3, "placeholder": "Ceritakan pengalaman Anda (opsional)"}),
            "category": Select(),
            "thumbnail": URLInput(attrs={"placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000"}),
            "photos": Textarea(attrs={"rows": 3, "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000\nhttps://drive.google.com/thumbnail?id=...&sz=w1000"}),
            "logo": URLInput(attrs={"placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000"}),
            "ended_at": DateInput(attrs={"type": "date"}),
        }

    # --- Pembersihan input teks (perlindungan XSS di sisi server) ---
    # strip_tags membuang semua tag HTML, jadi input seperti
    # <img src="x" onerror="alert('XSS!')"> tidak pernah tersimpan sebagai HTML.
    def _strip(self, field, required_message=None):
        value = strip_tags(self.cleaned_data.get(field) or "").strip()
        if required_message and not value:
            raise ValidationError(required_message)
        return value

    def clean_title(self):
        return self._strip("title", "Organization / activity name cannot contain only HTML tags.")

    def clean_role(self):
        return self._strip("role")

    def clean_role_indo(self):
        return self._strip("role_indo")

    def clean_description(self):
        return self._strip("description", "Description cannot contain only HTML tags.")

    def clean_description_indo(self):
        return self._strip("description_indo")

    def clean(self):
        cleaned = super().clean()
        started = cleaned.get("started_at")
        ended = cleaned.get("ended_at")
        if started and ended and ended.date() < started:
            self.add_error("ended_at", "End date cannot be earlier than the start date.")
        return cleaned

    def clean_photos(self):
        """Satu URL per baris; baris kosong dibuang, tag HTML dibuang, tiap baris harus URL yang valid."""
        validate = URLValidator(schemes=["http", "https"])
        lines = []
        for raw in strip_tags(self.cleaned_data.get("photos", "")).splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                validate(line)
            except ValidationError:
                raise ValidationError("Each line must be a valid URL (starting with http:// or https://).")
            if line not in lines:
                lines.append(line)
        if len(lines) > 20:
            raise ValidationError("Please add at most 20 extra photos.")
        return "\n".join(lines)

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ["title", "title_indo", "description", "description_indo", "category", "thumbnail", "project_url"]
        labels = {
            "title": "Project Name",
            "title_indo": "Project Name (Indonesian, optional)",
            "description": "Description",
            "description_indo": "Description (Indonesian, optional)",
            "category": "Category",
            "thumbnail": "Thumbnail Photo URL",
            "project_url": "Project URL",
        }
        widgets = {
            "title": TextInput(attrs={"placeholder": "Nabastala"}),
            "title_indo": TextInput(attrs={"placeholder": "Kosongkan jika sama dengan nama Inggris"}),
            "description": Textarea(attrs={"rows": 3, "placeholder": "Tell us about this project"}),
            "description_indo": Textarea(attrs={"rows": 3, "placeholder": "Ceritakan proyek ini (opsional)"}),
            "category": Select(),
            "thumbnail": URLInput(attrs={"placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000"}),
            "project_url": URLInput(attrs={"placeholder": "https://youtube.com/..."}),
        }

    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Nama proyek tidak boleh hanya berisi tag HTML.")
        return title

    def clean_description(self):
        return strip_tags(self.cleaned_data["description"]).strip()

    def clean_title_indo(self):
        return strip_tags(self.cleaned_data["title_indo"]).strip()

    def clean_description_indo(self):
        return strip_tags(self.cleaned_data["description_indo"]).strip()


class ContactForm(ModelForm):
    """Form Contact. Pesan error sengaja tanpa angka/parameter supaya bisa
    diterjemahkan ID/EN oleh i18n.js (lihat kamus AUTO di sana)."""

    # Kolom jebakan untuk bot: disembunyikan dengan CSS, manusia tidak mengisinya.
    website = forms.CharField(required=False, widget=TextInput(attrs={
        "tabindex": "-1", "autocomplete": "off", "aria-hidden": "true",
    }))

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": TextInput(attrs={"placeholder": "Your name", "autocomplete": "name", "maxlength": 100, "data-i18n-attr": "placeholder:contact.ph.name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email", "maxlength": 254}),
            "subject": TextInput(attrs={"placeholder": "What is this about?", "maxlength": 150, "data-i18n-attr": "placeholder:contact.ph.subject"}),
            "message": Textarea(attrs={"rows": 6, "placeholder": "Write your message here...", "maxlength": 2000, "data-i18n-attr": "placeholder:contact.ph.message"}),
        }
        error_messages = {
            "name": {"required": "Please enter your name.", "max_length": "This is too long."},
            "email": {"required": "Please enter your email address.", "invalid": "Please enter a valid email address."},
            "subject": {"required": "Please enter a subject.", "max_length": "This is too long."},
            "message": {"required": "Please write a message.", "max_length": "This is too long."},
        }

    def _clean_text(self, field, message):
        value = strip_tags(self.cleaned_data[field]).strip()
        if not value:
            raise ValidationError(message)
        return value

    def clean_name(self):
        return self._clean_text("name", "Please enter your name.")

    def clean_subject(self):
        return self._clean_text("subject", "Please enter a subject.")

    def clean_message(self):
        value = self._clean_text("message", "Please write a message.")
        if len(value) < 10:
            raise ValidationError("Your message is too short.")
        return value