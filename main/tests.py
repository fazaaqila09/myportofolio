from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import date

from main.models import Experience, Education, Project

SECRET = "rahasia"


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Ongoing")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        # Merender HTML secara langsung dengan data list kosong
        content = render_to_string("experience.html", {"experience_list": []}).lower()
        self.assertIn("no experience added yet", content)

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Completed")
        self.assertNotContains(response, "Ongoing")


@override_settings(PORTFOLIO_SECRET_KEY=SECRET)
class ExperienceEditTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )
        self.url = reverse("main:update_experience", args=[self.experience.id])

    def form_data(self, **overrides):
        data = {
            "title": "Asisten Dosen DDP",
            "role": "Mentor",
            "description": "Deskripsi baru.",
            "category": "organization",
            "thumbnail": "",
            "logo": "",
            "started_at": "2026-04-01",
            "ended_at": "",
            "secret_key": SECRET,
        }
        data.update(overrides)
        return data

    # 1. Tombol edit ada di card dan halaman edit terisi data lama
    def test_edit_page_is_prefilled(self):
        card = self.client.get(reverse("main:show_experience"))
        self.assertContains(card, f'href="{self.url}"')

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")
        self.assertContains(response, 'value="Asisten Dosen PBP"')

    # 2. Data berubah kalau kode akses benar
    def test_update_with_valid_code(self):
        response = self.client.post(self.url, self.form_data())

        self.assertRedirects(response, reverse("main:show_experience"))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Dosen DDP")
        self.assertEqual(self.experience.category, "organization")
        self.assertEqual(Experience.objects.count(), 1)  # diubah, bukan ditambah

    # 3. Data tidak berubah kalau kode akses salah
    def test_update_with_wrong_code_is_rejected(self):
        response = self.client.post(self.url, self.form_data(secret_key="salah"))

        self.assertContains(response, "Invalid access code.")
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Dosen PBP")


class EducationTest(TestCase):
    def setUp(self):
        self.education = Education.objects.create(
            school="Universitas Testing",
            major="Ilmu Komputer",
            level="bachelor",
            started_at=date(2025, 8, 1)
        )

    # 1. URL dapat diakses dan menggunakan template yang tepat
    def test_education_url_is_accessible(self):
        response = self.client.get(reverse("main:show_education"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    # 2. Data model muncul di halaman HTML ketika ada data
    def test_education_page_shows_data(self):
        response = self.client.get(reverse("main:show_education"))
        # Mengubah jadi huruf kecil agar kebal dari error case-sensitive
        content = response.content.decode('utf-8').lower()
        self.assertIn("universitas testing", content)
        self.assertIn("ilmu komputer", content)

    # 3. Halaman HTML menampilkan pesan kondisi kosong ketika belum ada data
    def test_empty_education_page(self):
        # Merender HTML secara langsung dengan data list kosong
        content = render_to_string("education.html", {"education_list": []}).lower()
        self.assertIn("belum ada riwayat pendidikan yang ditambahkan", content)


class ProjectTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Solilokui",
            description="Film pendek produksi Nabastala Production.",
            category="film",
            project_url="https://www.youtube.com/watch?v=abc123",
            thumbnail="https://example.com/poster.jpg",
        )

    # 1. URL dapat diakses dan menggunakan template yang tepat
    def test_projects_url_is_accessible(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    # 2. Data model muncul di card (judul, kategori, foto), tanpa tulisan Completed
    def test_projects_page_shows_data(self):
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "Solilokui")
        self.assertContains(response, "Film &amp; Video")  # tanda & di-escape di HTML
        self.assertContains(response, 'src="https://example.com/poster.jpg"')
        self.assertNotContains(response, "Completed")

    # 3. Halaman menampilkan pesan kondisi kosong ketika belum ada data
    def test_empty_projects_page(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "No projects added yet")

    # 4. Search mencari di judul, bukan di kategori
    def test_search_by_title(self):
        Project.objects.create(
            title="Portfolio Website",
            description="Website pribadi.",
            category="software",
            project_url="https://example.com",
        )
        by_title = self.client.get(reverse("main:show_projects"), {"q": "portfolio"})
        self.assertContains(by_title, "Portfolio Website")
        self.assertNotContains(by_title, "Solilokui")

        by_category = self.client.get(reverse("main:show_projects"), {"q": "software"})
        self.assertContains(by_category, "No projects match your search.")