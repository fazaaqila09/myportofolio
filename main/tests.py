from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import date

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
        card = self.client.get(reverse("main:show_experience"))
        self.assertContains(card, f'href="{self.url}"')

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
        # Experience masih dirender server
        html = self.client.get(reverse("main:show_experience")).content.decode()
        self.assertEqual(reverse("main:create_experience") in html, add, f"{username}: add di experience")
        self.assertEqual(self.edit_urls[0] in html, edit, f"{username}: edit di experience")
        self.assertEqual("delete-experience-" in html, delete, f"{username}: delete di experience")
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
        html = self.client.get(reverse("main:show_experience")).content.decode()
        self.assertIn("Unstar", html)
        self.assertIn("star-count", html)
        # Project: status star datang dari API, bukan dari HTML halaman
        fields = self.client.get(reverse("main:get_project_json")).json()[0]["fields"]
        self.assertTrue(fields["is_starred"])
        self.assertEqual(fields["star_count"], 1)

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
        about = html[html.index('id="about"'):]
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