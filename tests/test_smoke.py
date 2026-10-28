from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

class CustomUserModelTests(TestCase):
    def test_auth_user_model_is_custom(self):
        User = get_user_model()
        self.assertEqual(User._meta.label, "accounts.User")

    def test_create_user_with_email(self):
        User = get_user_model()
        user = User.objects.create_user(email="farmer@example.com", password="s3cure-pass-123")
        self.assertEqual(user.email, "farmer@example.com")
        self.assertTrue(user.check_password("s3cure-pass-123"))
        self.assertEqual(user.role, "FARMER")

class PageTests(TestCase):
    def test_home_renders(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AgriScheme AI")

    def test_health_endpoint(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "ok"})