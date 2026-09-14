from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import date

from main.models import Experience, Education


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
        self.assertIn("belum ada pengalaman yang ditambahkan", content)

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Completed")
        self.assertNotContains(response, "Ongoing")

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