from urllib import response

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAPITests(APITestCase):
    def setUp(self):
        # Створюємо тестових користувачів
        self.normal_user_1 = User.objects.create_user(
            email="user1@example.com", password="password123", first_name="User", last_name="One"
        )
        self.normal_user_2 = User.objects.create_user(
            email="user2@example.com", password="password123", first_name="User", last_name="Two"
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", password="password123"
        )
        
        # Базові URL (замініть на ваші, якщо використовуєте reverse('user-list') тощо)
        self.list_url = "/users/"
        
    def get_detail_url(self, user_id):
        return f"/users/{user_id}/"

    def test_create_user_allow_any(self):
        """Будь-хто може створити акаунт (POST запит)"""
        payload = {
            "email": "newuser@example.com",
            "password": "strongpassword123",
            "first_name": "New",
            "last_name": "User"
        }
        response = self.client.post(self.list_url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 4)
        # Перевіряємо, що пароль не повертається у відповіді (write_only)
        self.assertNotIn("password", response.data)

    def test_list_users_admin_only(self):
        """Тільки адмін може бачити список усіх користувачів"""
        # Анонімний користувач
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Звичайний користувач
        self.client.force_authenticate(user=self.normal_user_1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Адміністратор
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        print("\n=== ВІДПОВІДЬ API ===")
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Варіант 2: рахувати довжину масиву з результатами
        self.assertEqual(len(response.data['results']), 3) # Три користувачі, створені в setUp

    def test_retrieve_user_permissions(self):
        """Звичайний юзер бачить тільки себе, адмін бачить усіх"""
        # Звичайний користувач дивиться свій профіль -> OK
        self.client.force_authenticate(user=self.normal_user_1)
        response = self.client.get(self.get_detail_url(self.normal_user_1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Звичайний користувач намагається подивитися чужий профіль -> Forbidden
        response = self.client.get(self.get_detail_url(self.normal_user_2.id))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Адмін дивиться профіль звичайного користувача -> OK
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.get_detail_url(self.normal_user_2.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user_permissions(self):
        """Звичайний юзер може редагувати себе, адмін - будь-кого"""
        payload = {"first_name": "Updated Name"}
        
        self.client.force_authenticate(user=self.normal_user_1)
        
        # Редагує себе -> OK
        response = self.client.patch(self.get_detail_url(self.normal_user_1.id), payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.normal_user_1.refresh_from_db()
        self.assertEqual(self.normal_user_1.first_name, "Updated Name")
        
        # Намагається відредагувати іншого -> Forbidden
        response = self.client.patch(self.get_detail_url(self.normal_user_2.id), payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)