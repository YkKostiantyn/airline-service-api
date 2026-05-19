from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.users.models import UserRole

User = get_user_model()

class UserModelTests(TestCase):
    def test_create_user_successful(self):
        user = User.objects.create_user(
            email="normal@example.com",
            password="testpassword123"
        )
        self.assertEqual(user.email, "normal@example.com")
        self.assertTrue(user.check_password("testpassword123"))
        self.assertEqual(user.role, UserRole.USER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        # Перевіряємо, що username дійсно None
        self.assertIsNone(user.username)

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="password123")

    def test_create_superuser_successful(self):
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword123"
        )
        self.assertEqual(admin.email, "admin@example.com")
        self.assertEqual(admin.role, UserRole.ADMIN)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_create_superuser_must_have_is_staff_and_superuser(self):
        with self.assertRaisesMessage(ValueError, "Superuser must have is_staff=True"):
            User.objects.create_superuser(email="test1@example.com", password="123", is_staff=False)
            
        with self.assertRaisesMessage(ValueError, "Superuser must have is_superuser=True"):
            User.objects.create_superuser(email="test2@example.com", password="123", is_superuser=False)