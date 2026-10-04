from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import date
from pathlib import Path

from main.models import ContactMessage, Experience, Education, Project

PASSWORD = "Namorstrange33"

def make_users():
    """Buat akun untuk tiap peran: pemilik (superuser), editor (grup Editor), dan user biasa."""
    User.objects.create_superuser("pemilik", password=PASSWORD)
    editor = User.objects.create_user("editor1", password=PASSWORD)
    editor.groups.add(Group.objects.get_or_create(name="Editor")[0])
    User.objects.create_user("biasa", password=PASSWORD)

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
        # Halaman hanya kerangka; datanya datang dari endpoint JSON (Tugas 5)
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, f'data-endpoint="{reverse("main:get_experience_json")}"')
        self.assertContains(response, "js/experience.js")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

        fields = self.client.get(reverse("main:get_experience_json")).json()[0]["fields"]
        self.assertEqual(fields["title"], self.experience.title)
        self.assertEqual(fields["description"], self.experience.description)
        self.assertEqual(fields["category_display"], "Part-Time")
        self.assertTrue(fields["is_ongoing"])

    def test_empty_experience_page(self):
        # Merender HTML secara langsung dengan data list kosong
        content = render_to_string("experience.html", {"experience_list": []}).lower()
        self.assertIn("no experience added yet", content)

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        fields = self.client.get(reverse("main:get_experience_json")).json()[0]["fields"]

        self.assertFalse(self.experience.is_ongoing)
        self.assertFalse(fields["is_ongoing"])
        self.assertEqual(fields["ended_at"], self.experience.ended_at.date().isoformat())


class ExperienceEditTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )
        self.url = reverse("main:update_experience", args=[self.experience.id])
        make_users()
        self.client.login(username="pemilik", password=PASSWORD)

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
        }
        data.update(overrides)
        return data

    # 1. Tombol edit ada di card dan halaman edit terisi data lama
    def test_edit_page_is_prefilled(self):
        # Kartu dibuat JavaScript: URL edit diambil dari template URL + id dari JSON
        page = self.client.get(reverse("main:show_experience"))
        dummy = reverse("main:update_experience", args=["00000000-0000-0000-0000-000000000000"])
        self.assertContains(page, f'data-edit-url="{dummy}"')
        self.assertContains(page, 'data-can-edit="true"')
        pk = self.client.get(reverse("main:get_experience_json")).json()[0]["pk"]
        self.assertEqual(dummy.replace("00000000-0000-0000-0000-000000000000", pk), self.url)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")
        self.assertContains(response, 'value="Asisten Dosen PBP"')

    # 2. Data berubah kalau yang mengubah berhak (tanpa access code lagi)
    def test_update_by_authorized_user(self):
        response = self.client.post(self.url, self.form_data())

        self.assertRedirects(response, reverse("main:show_experience"))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Dosen DDP")
        self.assertEqual(self.experience.category, "organization")
        self.assertEqual(Experience.objects.count(), 1)  # diubah, bukan ditambah

    # 3. Form tidak lagi meminta Access Code
    def test_form_has_no_access_code_field(self):
        response = self.client.get(self.url)
        self.assertNotContains(response, "secret_key")


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

    # 2. Data proyek kini diambil lewat AJAX: cek endpoint JSON-nya
    def test_projects_api_shows_data(self):
        response = self.client.get(reverse("main:get_project_json"))
        self.assertEqual(response.status_code, 200)
        fields = response.json()[0]["fields"]
        self.assertEqual(fields["title"], "Solilokui")
        self.assertEqual(fields["category_display"], "Film & Video")
        self.assertEqual(fields["thumbnail"], "https://example.com/poster.jpg")
        self.assertEqual(fields["star_count"], 0)
        self.assertFalse(fields["is_starred"])

    # 3. Halaman hanya berisi kerangka + pesan kondisi kosong; API mengembalikan []
    def test_empty_projects_page(self):
        Project.objects.all().delete()
        self.assertEqual(self.client.get(reverse("main:get_project_json")).json(), [])
        response = self.client.get(reverse("main:show_projects"))
        self.assertContains(response, "No projects added yet")
        self.assertContains(response, 'id="grid"')

    # 4. Search mencari di judul/deskripsi, bukan di kategori
    def test_search_by_title(self):
        Project.objects.create(
            title="Portfolio Website",
            description="Website pribadi.",
            category="software",
            project_url="https://example.com",
        )
        url = reverse("main:get_project_json")
        by_title = self.client.get(url, {"q": "portfolio"}).json()
        self.assertEqual([p["fields"]["title"] for p in by_title], ["Portfolio Website"])

        by_category = self.client.get(url, {"q": "software"}).json()
        self.assertEqual(by_category, [])

    # 5. is_starred mengikuti user yang sedang login
    def test_api_is_starred_follows_user(self):
        make_users()
        self.project.starred_by.add(User.objects.get(username="biasa"))
        url = reverse("main:get_project_json")
        self.assertFalse(self.client.get(url).json()[0]["fields"]["is_starred"])
        self.client.login(username="biasa", password=PASSWORD)
        fields = self.client.get(url).json()[0]["fields"]
        self.assertTrue(fields["is_starred"])
        self.assertEqual(fields["star_count"], 1)


class CreateProjectAjaxTest(TestCase):
    """Endpoint POST /projects/add-ajax/: hanya pemilik, validasi lewat ProjectForm."""

    VALID = {
        "title": "Proyek Baru", "description": "Deskripsi.", "category": "software",
        "thumbnail": "", "project_url": "https://example.com",
    }

    def setUp(self):
        make_users()
        self.url = reverse("main:create_project_ajax")

    def test_get_not_allowed(self):
        self.client.login(username="pemilik", password=PASSWORD)
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_visitor_regular_user_and_editor_get_403_json(self):
        for username in (None, "biasa", "editor1"):
            if username:
                self.client.login(username=username, password=PASSWORD)
            response = self.client.post(self.url, self.VALID)
            self.assertEqual(response.status_code, 403)
            self.assertIn("message", response.json())
            self.client.logout()
        self.assertFalse(Project.objects.exists())

    def test_owner_creates_project(self):
        self.client.login(username="pemilik", password=PASSWORD)
        response = self.client.post(self.url, self.VALID)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Project.objects.filter(title="Proyek Baru").exists())

    def test_invalid_data_returns_400_with_errors(self):
        self.client.login(username="pemilik", password=PASSWORD)
        response = self.client.post(self.url, {**self.VALID, "title": "   ", "project_url": "nope"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])
        self.assertIn("project_url", response.json()["errors"])
        self.assertFalse(Project.objects.exists())

    def test_javascript_url_is_rejected(self):
        self.client.login(username="pemilik", password=PASSWORD)
        response = self.client.post(self.url, {**self.VALID, "project_url": "javascript:alert(1)"})
        self.assertEqual(response.status_code, 400)

    def test_html_tags_are_stripped(self):
        self.client.login(username="pemilik", password=PASSWORD)
        self.client.post(self.url, {**self.VALID, "title": "Halo <b>dunia</b>", "description": "<script>x</script>Isi"})
        project = Project.objects.get()
        self.assertEqual(project.title, "Halo dunia")
        self.assertNotIn("<", project.description)

    def test_title_of_only_tags_is_rejected(self):
        self.client.login(username="pemilik", password=PASSWORD)
        response = self.client.post(self.url, {**self.VALID, "title": "<img src=x onerror=alert(1)>"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Project.objects.exists())

    def test_csrf_is_enforced(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.login(username="pemilik", password=PASSWORD)
        self.assertEqual(client.post(self.url, self.VALID).status_code, 403)
        self.assertFalse(Project.objects.exists())


class RoleAccessTest(TestCase):
    """Hak akses 4 peran (pengunjung, user biasa, Editor, pemilik) pada Experience dan Project."""

    def setUp(self):
        self.experience = Experience.objects.create(
            title="COMPFEST", description="Panitia.", category="committee",
        )
        self.project = Project.objects.create(
            title="Solilokui", description="Film pendek.", category="film",
            project_url="https://example.com",
        )
        make_users()
        self.add_urls = [reverse("main:create_experience"), reverse("main:create_project")]
        self.edit_urls = [
            reverse("main:update_experience", args=[self.experience.id]),
            reverse("main:update_project", args=[self.project.id]),
        ]
        self.delete_urls = [
            reverse("main:delete_experience", args=[self.experience.id]),
            reverse("main:delete_project", args=[self.project.id]),
        ]

    def login(self, username):
        self.client.login(username=username, password=PASSWORD)

    def data_still_exists(self):
        return (
            Experience.objects.filter(pk=self.experience.pk).exists()
            and Project.objects.filter(pk=self.project.pk).exists()
        )

    # --- Pengunjung: diarahkan ke login ---
    def test_visitor_is_redirected_to_login(self):
        for url in self.add_urls + self.edit_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith("/login/?next="))
        for url in self.delete_urls:
            response = self.client.post(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith("/login/"))
        self.assertTrue(self.data_still_exists())

    # --- User biasa: 403 untuk semua aksi ubah data ---
    def test_regular_user_gets_403(self):
        self.login("biasa")
        for url in self.add_urls + self.edit_urls:
            self.assertEqual(self.client.get(url).status_code, 403)
        for url in self.delete_urls:
            self.assertEqual(self.client.post(url).status_code, 403)
        self.assertTrue(self.data_still_exists())

    # --- Editor: boleh edit, tidak boleh tambah/hapus ---
    def test_editor_can_edit_but_not_create_or_delete(self):
        self.login("editor1")
        for url in self.edit_urls:
            self.assertEqual(self.client.get(url).status_code, 200)
        for url in self.add_urls:
            self.assertEqual(self.client.get(url).status_code, 403)
        for url in self.delete_urls:
            self.assertEqual(self.client.post(url).status_code, 403)
        self.assertTrue(self.data_still_exists())

    def test_editor_can_save_changes(self):
        self.login("editor1")
        self.client.post(self.edit_urls[0], {
            "title": "COMPFEST 18", "role": "", "description": "Panitia.",
            "category": "committee", "thumbnail": "", "logo": "",
            "started_at": "2026-04-01", "ended_at": "",
        })
        self.client.post(self.edit_urls[1], {
            "title": "Solilokui 2", "description": "Film pendek.", "category": "film",
            "thumbnail": "", "project_url": "https://example.com",
        })
        self.experience.refresh_from_db()
        self.project.refresh_from_db()
        self.assertEqual(self.experience.title, "COMPFEST 18")
        self.assertEqual(self.project.title, "Solilokui 2")

    # --- Pemilik: semua boleh ---
    def test_owner_has_full_access(self):
        self.login("pemilik")
        for url in self.add_urls + self.edit_urls:
            self.assertEqual(self.client.get(url).status_code, 200)
        for url in self.delete_urls:
            self.assertEqual(self.client.post(url).status_code, 302)
        self.assertFalse(Experience.objects.exists())
        self.assertFalse(Project.objects.exists())

    # --- Tombol di template mengikuti peran ---
    def assert_buttons(self, username, add, edit, delete):
        if username:
            self.login(username)
        # Experience dirender lewat AJAX: yang ada di HTML hanya modal dan flag peran untuk JavaScript
        html = self.client.get(reverse("main:show_experience")).content.decode()
        self.assertEqual('id="add-experience-modal"' in html, add, f"{username}: modal add di experience")
        self.assertEqual('data-can-edit="true"' in html, edit, f"{username}: data-can-edit di experience")
        self.assertEqual('data-is-owner="true"' in html, delete, f"{username}: data-is-owner di experience")
        # Project dirender lewat AJAX: yang ada di HTML hanya modal dan flag peran untuk JavaScript
        html = self.client.get(reverse("main:show_projects")).content.decode()
        self.assertEqual('id="add-project-modal"' in html, add, f"{username}: modal add di projects")
        self.assertEqual('const CAN_EDIT = "true"' in html, edit, f"{username}: CAN_EDIT di projects")
        self.assertEqual('const IS_SUPERUSER = "true"' in html, delete, f"{username}: IS_SUPERUSER di projects")
        self.client.logout()

    def test_buttons_follow_role(self):
        self.assert_buttons(None, add=False, edit=False, delete=False)
        self.assert_buttons("biasa", add=False, edit=False, delete=False)
        self.assert_buttons("editor1", add=False, edit=True, delete=False)
        self.assert_buttons("pemilik", add=True, edit=True, delete=True)


class StarTest(TestCase):
    """Star pada Experience dan Project: butuh login, maksimal satu per pengguna, API tidak bocor."""

    def setUp(self):
        self.experience = Experience.objects.create(
            title="COMPFEST", description="Panitia.", category="committee",
        )
        self.project = Project.objects.create(
            title="Solilokui", description="Film pendek.", category="film",
            project_url="https://example.com",
        )
        make_users()
        self.targets = [
            (self.experience, reverse("main:toggle_star_experience", args=[self.experience.id])),
            (self.project, reverse("main:toggle_star", args=[self.project.id])),
        ]

    def test_visitor_cannot_star(self):
        for obj, url in self.targets:
            response = self.client.post(url)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith("/login/"))
            self.assertEqual(obj.starred_by.count(), 0)

    def test_toggle_adds_then_removes_and_max_one_per_user(self):
        self.client.login(username="biasa", password=PASSWORD)
        for obj, url in self.targets:
            self.client.post(url)
            self.assertEqual(obj.starred_by.count(), 1)
            self.client.post(url)
            self.assertEqual(obj.starred_by.count(), 0)

    def test_get_does_not_change_star(self):
        self.client.login(username="biasa", password=PASSWORD)
        for obj, url in self.targets:
            self.client.get(url)
            self.assertEqual(obj.starred_by.count(), 0)

    def test_page_shows_count_and_user_state(self):
        self.client.login(username="biasa", password=PASSWORD)
        for obj, url in self.targets:
            self.client.post(url)
        # Experience dan Project: status star datang dari API, bukan dari HTML halaman
        for name in ("main:get_experience_json", "main:get_project_json"):
            fields = self.client.get(reverse(name)).json()[0]["fields"]
            self.assertTrue(fields["is_starred"], name)
            self.assertEqual(fields["star_count"], 1, name)

    def test_api_shows_usernames_only(self):
        user = User.objects.get(username="biasa")
        self.experience.starred_by.add(user)
        self.project.starred_by.add(user)
        for name in ("main:get_experience_json", "main:get_project_json"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.json()[0]["fields"]["starred_by"], [["biasa"]])
            body = response.content.decode().lower()
            self.assertNotIn("password", body)
            self.assertNotIn("email", body)

    # --- Star lewat AJAX (tanpa reload) ---
    def test_ajax_toggle_returns_json(self):
        self.client.login(username="biasa", password=PASSWORD)
        for obj, url in self.targets:
            response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json(),
                {"is_starred": True, "star_count": 1, "starred_by_names": "biasa"},
            )
            response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.json()["is_starred"], False)
            self.assertEqual(response.json()["star_count"], 0)

    def test_ajax_visitor_gets_401_json(self):
        for obj, url in self.targets:
            response = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json()["login_url"], "/login/")
            self.assertEqual(obj.starred_by.count(), 0)


class NavbarTest(TestCase):
    """Navbar: ikon orang + "Login" (pengunjung) atau + username dan menu Logout (sudah login)."""

    def test_guest_sees_login(self):
        html = self.client.get(reverse("main:show_main")).content.decode()
        self.assertIn('class="nav-account"', html)
        self.assertIn(f'href="{reverse("main:login")}"', html)
        self.assertIn('class="nav-account__name">Login<', html)
        self.assertNotIn('id="profile-menu"', html)
        self.assertNotIn(reverse("main:logout"), html)

    def test_logged_in_sees_username_and_logout(self):
        make_users()
        self.client.login(username="biasa", password=PASSWORD)
        html = self.client.get(reverse("main:show_main")).content.decode()
        self.assertIn('class="nav-account__name">biasa<', html)
        self.assertIn('id="profile-menu"', html)
        self.assertIn(f'href="{reverse("main:logout")}"', html)
        self.assertNotIn('class="nav-account__name">Login<', html)

    def test_about_has_no_email(self):
        html = self.client.get(reverse("main:show_main")).content.decode()
        # hanya section About (sampai section Skills); footer boleh memuat email
        about = html[html.index('id="about"'):html.index('id="skills"')]
        self.assertNotIn("Email", about)
        self.assertNotIn("mailto:", about)


class ContactTest(TestCase):
    """Halaman Contact: form pesan yang disimpan ke database."""

    VALID = {
        "name": "Budi Santoso",
        "email": "budi@example.com",
        "subject": "Halo Faza",
        "message": "Saya tertarik dengan proyek portofolio Anda, bisa ngobrol?",
    }

    def test_contact_page_is_accessible(self):
        response = self.client.get(reverse("main:show_contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact.html")
        for field in ("name", "email", "subject", "message"):
            self.assertContains(response, f'name="{field}"')

    def test_valid_message_is_saved(self):
        response = self.client.post(reverse("main:show_contact"), self.VALID)
        # fetch_redirect_response=False: pesan sukses baru dibaca saat halaman tujuan dibuka di bawah
        self.assertRedirects(response, reverse("main:show_contact"), fetch_redirect_response=False)
        saved = ContactMessage.objects.get()
        self.assertEqual(saved.name, "Budi Santoso")
        self.assertEqual(saved.email, "budi@example.com")
        self.assertFalse(saved.is_read)
        self.assertEqual(str(saved), "Budi Santoso: Halo Faza")
        follow = self.client.get(reverse("main:show_contact"))
        self.assertContains(follow, "Thank you! Your message has been sent.")

    def test_invalid_message_shows_errors_and_is_not_saved(self):
        response = self.client.post(reverse("main:show_contact"), {"name": "", "email": "bukan-email", "subject": "", "message": "pendek"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter your name.")
        self.assertContains(response, "Please enter a valid email address.")
        self.assertContains(response, "Please enter a subject.")
        self.assertContains(response, "Your message is too short.")
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_html_tags_are_stripped(self):
        self.client.post(reverse("main:show_contact"), {**self.VALID, "name": "<b>Budi</b>", "message": "<script>alert(1)</script>Halo, ini pesan uji yang cukup panjang."})
        saved = ContactMessage.objects.get()
        self.assertEqual(saved.name, "Budi")
        self.assertNotIn("<script>", saved.message)

    def test_name_of_only_tags_is_rejected(self):
        response = self.client.post(reverse("main:show_contact"), {**self.VALID, "name": "<b></b>"})
        self.assertContains(response, "Please enter your name.")
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_honeypot_blocks_bots_silently(self):
        response = self.client.post(reverse("main:show_contact"), {**self.VALID, "website": "http://spam.example"})
        self.assertRedirects(response, reverse("main:show_contact"))
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_second_message_too_fast_is_rejected(self):
        self.client.post(reverse("main:show_contact"), self.VALID)
        response = self.client.post(reverse("main:show_contact"), self.VALID)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please wait a moment before sending another message.")
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_admin_can_read_messages(self):
        from django.contrib import admin
        self.assertIn(ContactMessage, admin.site._registry)
        make_users()
        ContactMessage.objects.create(**self.VALID)
        self.client.login(username="pemilik", password=PASSWORD)
        response = self.client.get("/admin/main/contactmessage/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Halo Faza")


class SkillsSectionTest(TestCase):
    """Section Skills ada di antara About dan Education, lengkap dengan menu navbarnya."""

    def setUp(self):
        self.html = self.client.get(reverse("main:show_main")).content.decode()

    def test_skills_section_sits_between_about_and_education(self):
        about = self.html.index('id="about"')
        skills = self.html.index('id="skills"')
        education = self.html.index('id="education"')
        self.assertLess(about, skills)
        self.assertLess(skills, education)

    def test_skills_section_lists_tech_stack(self):
        for skill in ("Python", "Django", "Git"):
            self.assertContains(self.client.get(reverse("main:show_main")), skill)

    def test_skills_are_a_marquee_with_hidden_copies(self):
        # satu daftar asli untuk pembaca layar, sisanya salinan aria-hidden untuk animasi
        section = self.html[self.html.index('id="skills"'):self.html.index('id="education"')]
        self.assertIn("marquee__track", section)
        self.assertEqual(section.count('class="skill-row"'), 3)
        self.assertEqual(section.count("<li class=\"skill-chip\">"), 16)
        self.assertGreater(section.count('skill-chip is-copy" aria-hidden="true"'), 16)

    def test_navbar_has_skills_and_contact_in_order(self):
        nav = self.html[self.html.index('class="nav-menu"'):self.html.index('class="nav-right"')]
        order = ["#home", "#about", "#skills", "#education", reverse("main:show_experience"), reverse("main:show_projects"), reverse("main:show_contact")]
        positions = [nav.index(item) for item in order]
        self.assertEqual(positions, sorted(positions))

    def test_navbar_links_exist_on_other_pages(self):
        html = self.client.get(reverse("main:show_contact")).content.decode()
        self.assertIn(f'href="{reverse("main:show_main")}#skills"', html)
        self.assertIn(f'href="{reverse("main:show_contact")}"', html)


class LanguageToggleTest(TestCase):
    """Toggle bahasa ID/EN: tombol di navbar + berkas kamus dimuat di semua halaman."""

    def test_toggle_and_dictionary_on_every_page(self):
        for name in ("main:show_main", "main:show_experience", "main:show_projects", "main:show_contact", "main:show_education", "main:login"):
            html = self.client.get(reverse(name)).content.decode()
            self.assertIn("data-lang-toggle", html, name)
            self.assertIn("js/i18n.js", html, name)
            self.assertIn('data-l="id"', html, name)
            self.assertIn('data-l="en"', html, name)

    def test_english_is_the_default_text(self):
        html = self.client.get(reverse("main:show_main")).content.decode()
        self.assertIn('data-i18n="nav.education">Education<', html)
        self.assertIn('<html lang="en">', html)

    def test_dictionary_has_every_key_used_in_templates(self):
        import re
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent
        source = (base / "static" / "js" / "i18n.js").read_text(encoding="utf-8")
        english = source[source.index("en: {"):source.index("id: {")]
        indonesian = source[source.index("id: {"):source.index("AUTO_PAIRS")]
        used = set()
        for template in (base / "templates").rglob("*.html"):
            used |= set(re.findall(r'data-i18n(?:-html)?="([\w.]+)"', template.read_text(encoding="utf-8")))
        # kunci yang sengaja hanya ada di ID: teks Inggrisnya diambil dari view (bio & subtitle)
        server_text_only = {"about.bio", "hero.subtitle"}
        for key in used:
            self.assertIn(f"'{key}'", indonesian, f"Kunci '{key}' belum ada di kamus ID")
            if key not in server_text_only:
                self.assertIn(f"'{key}'", english, f"Kunci '{key}' belum ada di kamus EN")


class InboxTest(TestCase):
    """Kotak masuk pesan Contact: hanya untuk pemilik (superuser)."""

    def setUp(self):
        make_users()
        self.unread = ContactMessage.objects.create(
            name="Budi", email="budi@example.com", subject="Tanya proyek", message="Halo, saya ingin bertanya soal proyekmu.")
        self.read = ContactMessage.objects.create(
            name="Sari", email="sari@example.com", subject="Kolaborasi", message="Ayo kolaborasi bikin film pendek!", is_read=True)

    def login(self, username="pemilik"):
        self.client.login(username=username, password=PASSWORD)

    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(reverse("main:show_inbox"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_non_owner_is_forbidden(self):
        for username in ("editor1", "biasa"):
            self.client.logout()
            self.login(username)
            self.assertEqual(self.client.get(reverse("main:show_inbox")).status_code, 403, username)

    def test_owner_sees_messages_and_counts(self):
        self.login()
        response = self.client.get(reverse("main:show_inbox"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "inbox.html")
        self.assertContains(response, "Tanya proyek")
        self.assertContains(response, "Kolaborasi")
        self.assertEqual(response.context["counts"], {"all": 2, "unread": 1, "read": 1})

    def test_filter_and_search(self):
        self.login()
        unread = self.client.get(reverse("main:show_inbox"), {"filter": "unread"})
        self.assertContains(unread, "Tanya proyek")
        self.assertNotContains(unread, "Ayo kolaborasi")
        found = self.client.get(reverse("main:show_inbox"), {"q": "sari"})
        self.assertContains(found, "Kolaborasi")
        self.assertNotContains(found, "Tanya proyek")
        # filter yang tidak dikenal jatuh kembali ke "all"
        weird = self.client.get(reverse("main:show_inbox"), {"filter": "<script>"})
        self.assertEqual(weird.context["status"], "all")

    def test_message_html_is_escaped(self):
        ContactMessage.objects.create(name="X", email="x@example.com", subject="s", message="<script>alert(1)</script> pesan cukup panjang")
        self.login()
        html = self.client.get(reverse("main:show_inbox")).content.decode()
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)

    def test_toggle_read_and_unread(self):
        self.login()
        url = reverse("main:inbox_toggle_read", args=[self.unread.id])
        self.client.post(url)
        self.unread.refresh_from_db()
        self.assertTrue(self.unread.is_read)
        self.client.post(url)
        self.unread.refresh_from_db()
        self.assertFalse(self.unread.is_read)

    def test_ajax_mark_read_returns_json_with_unread_count(self):
        self.login()
        response = self.client.post(
            reverse("main:inbox_toggle_read", args=[self.unread.id]), {"set": "read"},
            headers={"X-Requested-With": "XMLHttpRequest"})
        self.assertEqual(response.json(), {"is_read": True, "unread": 0})

    def test_toggle_requires_post_and_owner(self):
        url = reverse("main:inbox_toggle_read", args=[self.unread.id])
        self.login("editor1")
        self.assertEqual(self.client.post(url).status_code, 403)
        self.client.logout()
        self.login()
        self.assertEqual(self.client.get(url).status_code, 405)

    def test_mark_all_read(self):
        self.login()
        response = self.client.post(reverse("main:inbox_mark_all_read"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.filter(is_read=False).count(), 0)

    def test_delete_message(self):
        self.login()
        response = self.client.post(reverse("main:inbox_delete", args=[self.read.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ContactMessage.objects.filter(pk=self.read.pk).exists())

    def test_non_owner_cannot_delete(self):
        self.login("editor1")
        response = self.client.post(reverse("main:inbox_delete", args=[self.read.id]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(ContactMessage.objects.filter(pk=self.read.pk).exists())

    def test_nav_badge_only_for_owner(self):
        self.login()
        html = self.client.get(reverse("main:show_main")).content.decode()
        self.assertIn("data-inbox-badge", html)
        self.assertIn(reverse("main:show_inbox"), html)
        self.client.logout()
        self.login("biasa")
        html = self.client.get(reverse("main:show_main")).content.decode()
        self.assertNotIn("data-inbox-badge", html)
        self.assertNotIn(reverse("main:show_inbox"), html)

    def test_unread_tag_counts(self):
        from main.templatetags.inbox_tags import unread_messages
        class R:  # permintaan tiruan
            def __init__(self, user): self.user = user
        owner = User.objects.get(username="pemilik")
        biasa = User.objects.get(username="biasa")
        self.assertEqual(unread_messages({"request": R(owner)}), 1)
        self.assertEqual(unread_messages({"request": R(biasa)}), 0)


class DatabaseTranslationTest(TestCase):
    """Isi database punya terjemahan Indonesia (kolom *_indo) yang dipakai toggle bahasa."""

    def test_experience_page_carries_indonesian_text(self):
        Experience.objects.create(
            title="Lomba", role="Mentor", role_indo="Pembimbing",
            description="Guided students.", description_indo="Membimbing mahasiswa.",
        )
        fields = self.client.get(reverse("main:get_experience_json")).json()[0]["fields"]
        self.assertEqual((fields["role"], fields["role_indo"]), ("Mentor", "Pembimbing"))
        self.assertEqual(fields["description_indo"], "Membimbing mahasiswa.")

    def test_education_page_carries_indonesian_text(self):
        Education.objects.create(school="UI", major="Computer Science", major_indo="Ilmu Komputer", started_at=date(2025, 8, 1))
        html = self.client.get(reverse("main:show_education")).content.decode()
        self.assertIn('data-id-text="Ilmu Komputer">Computer Science<', html)

    def test_seeded_data_has_indonesian_text(self):
        self.client.get(reverse("main:show_experience"))
        self.client.get(reverse("main:show_education"))
        self.assertFalse(Experience.objects.filter(role_indo="").exists())
        self.assertFalse(Experience.objects.filter(description_indo="").exists())
        self.assertFalse(Education.objects.filter(major_indo="").exists())

    def test_project_json_includes_and_searches_indonesian_text(self):
        Project.objects.create(
            title="Film", title_indo="Film Pendek", description="A short film.",
            description_indo="Sebuah film pendek tentang kota.", project_url="https://example.com")
        data = self.client.get(reverse("main:get_project_json")).json()
        self.assertEqual(data[0]["fields"]["title_indo"], "Film Pendek")
        found = self.client.get(reverse("main:get_project_json"), {"q": "tentang kota"}).json()
        self.assertEqual(len(found), 1)

    def test_translation_fields_are_optional_in_forms(self):
        from main.forms import ProjectForm
        form = ProjectForm({"title": "Tanpa Terjemahan", "description": "Cuma Inggris.",
                            "category": "other", "project_url": "https://example.com"})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().title_indo, "")

    def test_indonesian_text_is_stripped_of_html(self):
        from main.forms import ProjectForm
        form = ProjectForm({"title": "T", "title_indo": "<b>Judul</b>", "description": "D",
                            "description_indo": "<script>x</script>Deskripsi", "category": "other",
                            "project_url": "https://example.com"})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["title_indo"], "Judul")
        self.assertNotIn("<script>", form.cleaned_data["description_indo"])


class MotionAndLightboxTest(TestCase):
    """Lightbox foto Experience, tombol magnetik, bentuk kursor, dan transisi halaman."""

    def setUp(self):
        Experience.objects.create(title="Lomba", description="Deskripsi", thumbnail="/static/img/exp-cf.jpg")

    def test_experience_photo_is_lightbox_ready(self):
        html = self.client.get(reverse("main:show_experience")).content.decode()
        self.assertIn("js/lightbox.js", html)
        js = (Path(__file__).resolve().parent.parent / "static" / "js" / "experience.js").read_text(encoding="utf-8")
        self.assertIn('class="exp-photo"', js)

    def test_motion_script_and_fallback_flag_on_every_page(self):
        for name in ("main:show_main", "main:show_experience", "main:show_projects", "main:show_contact", "main:login"):
            html = self.client.get(reverse(name)).content.decode()
            self.assertIn("js/motion.js", html, name)
            self.assertIn("CSSViewTransitionRule", html, name)   # penanda cadangan 'no-vt'

    def test_page_transition_css_is_present(self):
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent / "static" / "css"
        self.assertIn("@view-transition", (base / "effects.css").read_text(encoding="utf-8"))
        extras = (base / "extras.css").read_text(encoding="utf-8")
        self.assertIn("view-transition-name: site-nav", extras)
        self.assertIn("prefers-reduced-motion", extras)

    def test_dictionary_has_lightbox_and_inbox_keys_in_both_languages(self):
        from pathlib import Path
        source = (Path(__file__).resolve().parent.parent / "static" / "js" / "i18n.js").read_text(encoding="utf-8")
        english = source[source.index("en: {"):source.index("id: {")]
        indonesian = source[source.index("id: {"):source.index("AUTO_PAIRS")]
        keys = ["lb.label", "lb.close", "lb.prev", "lb.next", "lb.enlarge", "lb.enlarge.short",
                "lb.hint.switch", "lb.hint.close", "nav.inbox", "inbox.title", "inbox.empty", "inbox.delete.confirm"]
        for key in keys:
            self.assertIn(f"'{key}'", english, key)
            self.assertIn(f"'{key}'", indonesian, key)


class FillMissingTranslationsTest(TestCase):
    """Data lama yang kolom Indonesia-nya kosong diisi otomatis (tanpa migrasi data)."""

    def test_existing_seed_rows_get_translations_when_pages_open(self):
        Experience.objects.create(title="COMPFEST 18", role="VPIC of Transportation & Venue", description="x")
        Education.objects.create(school="UI", major="Bachelor of Computer Science", started_at=date(2025, 8, 1))
        self.client.get(reverse("main:show_experience"))
        self.client.get(reverse("main:show_education"))
        self.assertEqual(Experience.objects.get(title="COMPFEST 18").role_indo, "VPIC Transportasi & Venue")
        self.assertEqual(Education.objects.get(school="UI").major_indo, "S1 Ilmu Komputer")

    def test_own_translation_is_not_overwritten(self):
        Experience.objects.create(title="DDP0", role="Mentor", role_indo="Pembimbing Kelas", description="x")
        self.client.get(reverse("main:show_experience"))
        self.assertEqual(Experience.objects.get(title="DDP0").role_indo, "Pembimbing Kelas")


class ExperienceGalleryTest(TestCase):
    """Satu Experience bisa punya beberapa foto; lightbox hanya memindah foto di kegiatan itu."""

    def make(self, **extra):
        return Experience.objects.create(title="Lomba", description="Deskripsi", thumbnail="https://example.com/a.jpg", **extra)

    def test_all_photos_main_first_then_extras_without_duplicates(self):
        exp = self.make(photos="https://example.com/b.jpg\n\n  https://example.com/c.jpg  \nhttps://example.com/a.jpg")
        self.assertEqual(exp.all_photos, ["https://example.com/a.jpg", "https://example.com/b.jpg", "https://example.com/c.jpg"])

    def test_no_extra_photos_gives_just_the_main_one(self):
        self.assertEqual(self.make().all_photos, ["https://example.com/a.jpg"])
        self.assertEqual(Experience.objects.create(title="Kosong", description="x").all_photos, [])

    def test_card_carries_photo_list_and_count_badge(self):
        self.make(photos="https://example.com/b.jpg")
        fields = self.client.get(reverse("main:get_experience_json")).json()[0]["fields"]
        self.assertEqual(fields["photos"], ["https://example.com/a.jpg", "https://example.com/b.jpg"])
        js = (Path(__file__).resolve().parent.parent / "static" / "js" / "experience.js").read_text(encoding="utf-8")
        self.assertIn("data-photos=", js)
        self.assertIn("exp-photo__count", js)

    def test_single_photo_gives_one_item_list(self):
        self.make()
        fields = self.client.get(reverse("main:get_experience_json")).json()[0]["fields"]
        self.assertEqual(fields["photos"], ["https://example.com/a.jpg"])

    def test_form_accepts_urls_one_per_line_and_cleans_them(self):
        from main.forms import ExperienceForm
        form = ExperienceForm({"title": "T", "description": "D", "category": "committee", "started_at": "2026-01-01",
                               "photos": "https://example.com/1.jpg\r\n\r\nhttps://example.com/2.jpg\r\nhttps://example.com/1.jpg"})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["photos"], "https://example.com/1.jpg\nhttps://example.com/2.jpg")

    def test_form_rejects_a_line_that_is_not_a_url(self):
        from main.forms import ExperienceForm
        form = ExperienceForm({"title": "T", "description": "D", "category": "committee", "started_at": "2026-01-01",
                               "photos": "https://example.com/1.jpg\nbukan url\njavascript:alert(1)"})
        self.assertFalse(form.is_valid())
        self.assertIn("photos", form.errors)

    def test_photos_are_optional(self):
        from main.forms import ExperienceForm
        form = ExperienceForm({"title": "T", "description": "D", "category": "committee", "started_at": "2026-01-01"})
        self.assertTrue(form.is_valid(), form.errors)

    def test_lightbox_script_stays_inside_one_experience(self):
        from pathlib import Path
        js = (Path(__file__).resolve().parent.parent / "static" / "js" / "lightbox.js").read_text(encoding="utf-8")
        self.assertIn("data-photos", js)
        self.assertNotIn("cards.length", js.split("function open(")[1])   # tidak memutar antar kartu

class ExperienceAjaxTest(TestCase):
    """Tugas 5: Experience lewat AJAX (endpoint JSON, tambah via modal, CSRF, XSS)."""

    VALID = {
        "title": "Pesta Rakyat Komputer",
        "role": "Staff Acara",
        "description": "Menyusun rundown acara.",
        "category": "committee",
        "started_at": "2026-03-01",
        "ended_at": "",
    }

    def setUp(self):
        make_users()
        self.url = reverse("main:create_experience_ajax")
        self.api = reverse("main:get_experience_json")

    def login(self, username):
        self.client.login(username=username, password=PASSWORD)

    # --- Halaman hanya kerangka, data dari JSON ---
    def test_page_renders_skeleton_only(self):
        Experience.objects.create(title="Rahasia Kartu", description="x")
        html = self.client.get(reverse("main:show_experience")).content.decode()
        for element_id in ("exp-loading", "exp-error", "exp-empty", "exp-grid", "exp-search-input"):
            self.assertIn(f'id="{element_id}"', html)
        self.assertNotIn("Rahasia Kartu", html)          # kartu tidak dirender server
        self.assertIn("csrfmiddlewaretoken", html)        # token tersedia untuk POST dari JS

    def test_json_is_built_manually_with_star_info(self):
        exp = Experience.objects.create(title="COMPFEST", description="x", category="committee")
        biasa = User.objects.get(username="biasa")
        exp.starred_by.add(biasa)

        anonymous = self.client.get(self.api)
        self.assertEqual(anonymous.status_code, 200)
        self.assertEqual(anonymous["Content-Type"], "application/json")
        item = anonymous.json()[0]
        self.assertEqual(item["pk"], str(exp.id))
        self.assertEqual(item["fields"]["category_display"], "Committee")
        self.assertEqual(item["fields"]["star_count"], 1)
        self.assertFalse(item["fields"]["is_starred"])     # pengunjung belum login

        self.login("biasa")
        self.assertTrue(self.client.get(self.api).json()[0]["fields"]["is_starred"])

    def test_search_by_title_and_role(self):
        Experience.objects.create(title="COMPFEST 18", role="Staff", description="x")
        Experience.objects.create(title="BETIS", role="Mentor", role_indo="Pembimbing", description="x")
        titles = lambda q: [i["fields"]["title"] for i in self.client.get(self.api, {"title": q}).json()]
        self.assertEqual(titles("compfest"), ["COMPFEST 18"])
        self.assertEqual(titles("pembimbing"), ["BETIS"])
        self.assertEqual(titles("tidak-ada"), [])

    # --- Tambah data lewat AJAX ---
    def test_owner_gets_201_and_data_is_saved(self):
        self.login("pemilik")
        response = self.client.post(self.url, self.VALID)
        self.assertEqual(response.status_code, 201)
        body = response.json()
        saved = Experience.objects.get(pk=body["pk"])
        self.assertEqual(saved.title, "Pesta Rakyat Komputer")
        self.assertEqual(saved.started_at.date(), date(2026, 3, 1))
        self.assertEqual(body["experience"]["fields"]["started_at"], "2026-03-01")

    def test_invalid_input_gets_400_with_errors_and_labels(self):
        self.login("pemilik")
        response = self.client.post(self.url, {**self.VALID, "title": "", "category": "bukan-kategori"})
        self.assertEqual(response.status_code, 400)
        body = response.json()
        self.assertIn("title", body["errors"])
        self.assertIn("category", body["errors"])
        self.assertEqual(body["labels"]["title"], "Organization / Activity Name")
        self.assertFalse(Experience.objects.filter(title="").exists())

    def test_end_date_before_start_is_rejected(self):
        self.login("pemilik")
        response = self.client.post(self.url, {**self.VALID, "ended_at": "2026-01-01"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("ended_at", response.json()["errors"])

    def test_non_owner_gets_403_json(self):
        for username in (None, "biasa", "editor1"):
            self.client.logout()
            if username:
                self.login(username)
            response = self.client.post(self.url, self.VALID)
            self.assertEqual(response.status_code, 403, username)
            self.assertIn("message", response.json())
        self.assertFalse(Experience.objects.filter(title=self.VALID["title"]).exists())

    def test_get_is_not_allowed(self):
        self.login("pemilik")
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_csrf_token_is_required(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        client.login(username="pemilik", password=PASSWORD)
        self.assertEqual(client.post(self.url, self.VALID).status_code, 403)    # tanpa token: ditolak
        client.get(reverse("main:show_experience"))                            # mengisi cookie csrftoken
        token = client.cookies["csrftoken"].value
        response = client.post(self.url, self.VALID, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 201)

    # --- XSS ---
    def test_html_is_stripped_on_the_server(self):
        self.login("pemilik")
        payload = {**self.VALID,
                   "title": '<img src="x" onerror="alert(\'XSS!\')">Lomba Aman',
                   "role": "<script>alert(1)</script>Ketua",
                   "description": "<b>Tebal</b> biasa"}
        pk = self.client.post(self.url, payload).json()["pk"]
        saved = Experience.objects.get(pk=pk)
        self.assertEqual(saved.title, "Lomba Aman")
        self.assertNotIn("<", saved.role + saved.description)

    def test_title_with_only_html_is_rejected(self):
        self.login("pemilik")
        response = self.client.post(self.url, {**self.VALID, "title": '<img src="x" onerror="alert(\'XSS!\')">'})
        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])

    def test_page_script_escapes_every_inserted_text(self):
        js = (Path(__file__).resolve().parent.parent / "static" / "js" / "experience.js").read_text(encoding="utf-8")
        self.assertIn("escapeHtml(title)", js)
        self.assertIn("escapeHtml(description)", js)
        self.assertIn("'X-CSRFToken': getCsrfToken()", js)
        utils = (Path(__file__).resolve().parent.parent / "static" / "js" / "ajax-utils.js").read_text(encoding="utf-8")
        self.assertIn("function escapeHtml", utils)
        self.assertIn("function debounce", utils)

    def test_modal_only_for_owner(self):
        self.login("pemilik")
        html = self.client.get(reverse("main:show_experience")).content.decode()
        self.assertIn('id="add-experience-modal"', html)
        self.assertIn('id="experience-form"', html)
        self.assertIn('name="title"', html)