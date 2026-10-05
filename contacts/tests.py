from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Contact


class ContactsTestBase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser("owner", "owner@example.com", "pass12345")
        self.ani = Contact.objects.create(name="Ani Lestari", email="ani@example.com")
        self.budi = Contact.objects.create(name="Budi Santoso", email="budi@example.com")
        self.client.force_login(self.owner)


class ContactsAccessTest(TestCase):
    """Halaman Kontak hanya untuk pemilik (superuser)."""

    def test_visitor_and_normal_user_get_403(self):
        contact = Contact.objects.create(name="Ani", email="ani@example.com")
        urls = [
            reverse("contacts:contact_list"),
            reverse("contacts:contact_search"),
            reverse("contacts:contact_edit", args=[contact.id]),
            reverse("contacts:contact_row", args=[contact.id]),
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 403, url)

        User.objects.create_user("biasa", password="pass12345")
        self.client.login(username="biasa", password="pass12345")
        self.assertEqual(self.client.post(reverse("contacts:contact_add"),
                                          {"name": "X", "email": "x@example.com"}).status_code, 403)
        self.assertEqual(self.client.delete(reverse("contacts:contact_delete", args=[contact.id])).status_code, 403)
        self.assertEqual(Contact.objects.count(), 1)

    def test_menu_link_only_for_owner(self):
        User.objects.create_user("biasa", password="pass12345")
        self.client.login(username="biasa", password="pass12345")
        self.assertNotContains(self.client.get(reverse("main:show_main")), reverse("contacts:contact_list"))
        User.objects.create_superuser("owner", "owner@example.com", "pass12345")
        self.client.login(username="owner", password="pass12345")
        self.assertContains(self.client.get(reverse("main:show_main")), reverse("contacts:contact_list"))


class ContactListTest(ContactsTestBase):
    def test_page_loads_htmx_and_rows(self):
        response = self.client.get(reverse("contacts:contact_list"))
        self.assertContains(response, "htmx.org@2.0.11")
        self.assertContains(response, 'id="contact-rows"')
        self.assertContains(response, "X-CSRFToken")
        self.assertContains(response, f'id="contact-{self.ani.id}"')

    def test_empty_list_shows_message(self):
        Contact.objects.all().delete()
        self.assertContains(self.client.get(reverse("contacts:contact_list")), "contacts-empty")


class ContactAddTest(ContactsTestBase):
    def test_add_returns_fragment_only(self):
        response = self.client.post(reverse("contacts:contact_add"), {"name": "Citra Dewi", "email": "citra@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Contact.objects.filter(name="Citra Dewi").exists())
        html = response.content.decode()
        self.assertIn("Citra Dewi", html)
        self.assertNotIn("<html", html)

    def test_invalid_email_is_not_saved(self):
        self.client.post(reverse("contacts:contact_add"), {"name": "Salah", "email": "bukan-email"})
        self.assertFalse(Contact.objects.filter(name="Salah").exists())

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(reverse("contacts:contact_add")).status_code, 405)


class ContactDeleteTest(ContactsTestBase):
    def test_delete_returns_empty_200(self):
        response = self.client.delete(reverse("contacts:contact_delete", args=[self.ani.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        self.assertFalse(Contact.objects.filter(pk=self.ani.id).exists())

    def test_post_is_not_allowed(self):
        self.assertEqual(self.client.post(reverse("contacts:contact_delete", args=[self.ani.id])).status_code, 405)


class ContactSearchTest(ContactsTestBase):
    def test_search_is_case_insensitive(self):
        html = self.client.get(reverse("contacts:contact_search"), {"q": "ANI"}).content.decode()
        self.assertIn("Ani Lestari", html)
        self.assertNotIn("Budi Santoso", html)

    def test_empty_query_returns_all(self):
        html = self.client.get(reverse("contacts:contact_search"), {"q": ""}).content.decode()
        self.assertIn("Ani Lestari", html)
        self.assertIn("Budi Santoso", html)


class ContactEditTest(ContactsTestBase):
    def test_edit_and_row_return_two_versions(self):
        edit = self.client.get(reverse("contacts:contact_edit", args=[self.ani.id])).content.decode()
        row = self.client.get(reverse("contacts:contact_row", args=[self.ani.id])).content.decode()
        self.assertIn(f'form="edit-form-{self.ani.id}"', edit)
        self.assertIn("hx-put", edit)
        self.assertNotIn("<input", row)

    def test_update_with_put_body(self):
        response = self.client.put(
            reverse("contacts:contact_update", args=[self.ani.id]),
            data="name=Ani+Baru&email=ani.baru%40example.com",
            content_type="application/x-www-form-urlencoded",
        )
        self.assertEqual(response.status_code, 200)
        self.ani.refresh_from_db()
        self.assertEqual(self.ani.name, "Ani Baru")
        self.assertEqual(self.ani.email, "ani.baru@example.com")
        self.assertNotIn("<input", response.content.decode())

    def test_invalid_update_keeps_edit_row(self):
        response = self.client.put(
            reverse("contacts:contact_update", args=[self.ani.id]),
            data="name=&email=ani%40example.com",
            content_type="application/x-www-form-urlencoded",
        )
        self.assertIn("hx-put", response.content.decode())
        self.ani.refresh_from_db()
        self.assertEqual(self.ani.name, "Ani Lestari")