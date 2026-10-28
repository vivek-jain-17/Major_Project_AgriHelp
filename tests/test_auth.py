from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from accounts.decorators import farmer_required, admin_required

User = get_user_model()

class AuthFlowTests(TestCase):
    def test_signup_view_creates_user(self):
        response = self.client.post(reverse("signup"), {
            "email": "newfarmer@example.com",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        })
        self.assertEqual(response.status_code, 302) # Redirects to login
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.first()
        self.assertEqual(user.email, "newfarmer@example.com")
        self.assertEqual(user.role, "FARMER")

    def test_login_view(self):
        user = User.objects.create_user(email="login@example.com", password="complexpassword123")
        response = self.client.post(reverse("login"), {
            "username": "login@example.com", # AuthenticationForm uses 'username' field internally
            "password": "complexpassword123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(str(self.client.session["_auth_user_id"]), str(user.id))

class DecoratorTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(email="farmer@example.com", password="pw", role="FARMER")
        self.admin = User.objects.create_user(email="admin@example.com", password="pw", role="ADMIN")

    def test_farmer_decorator(self):
        @farmer_required
        def test_view(request):
            return "success"
        
        # Simulate request for farmer (we test logic directly)
        class MockRequest:
            def __init__(self, user): self.user = user
            
        self.assertEqual(test_view(MockRequest(self.farmer)), "success")
        with self.assertRaises(PermissionDenied):
            test_view(MockRequest(self.admin))

    def test_admin_decorator(self):
        @admin_required
        def test_view(request):
            return "success"
            
        class MockRequest:
            def __init__(self, user): self.user = user
            
        self.assertEqual(test_view(MockRequest(self.admin)), "success")
        with self.assertRaises(PermissionDenied):
            test_view(MockRequest(self.farmer))