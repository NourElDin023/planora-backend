import uuid
from datetime import datetime, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from users.models import EmailVerificationToken, PasswordResetToken
from pages.models import Collection
from sharing.models import SharedPage
from tasks.models import Task
from tracker.models import Note

User = get_user_model()


class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test users with custom User model fields
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User1",
            phone_number="+1234567890",
            bio="Test bio 1",
            is_active=True,
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User2",
            phone_number="+9876543210",
            bio="Test bio 2",
            is_active=True,
        )

        # Create collections with various sharing settings
        self.collection1 = Collection.objects.create(
            title="User1 Collection",
            description="Collection owned by User1",
            owner=self.user1,
            is_link_shareable=True,
            shareable_permission="edit",
        )
        self.collection2 = Collection.objects.create(
            title="User2 Collection",
            description="Collection owned by User2",
            owner=self.user2,
            is_link_shareable=False,
        )

        # Share collection1 with user2
        SharedPage.objects.create(page=self.collection1, shared_with=self.user2, permission="edit")

        # Create tasks with all required fields
        self.task1 = Task.objects.create(
            title="Task 1 in Collection 1",
            details="Details for task 1",
            due_date=datetime.now().date() + timedelta(days=1),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=1)).time(),
            category="Work",
            completed=False,
            collection=self.collection1,
            owner=self.user1,
        )
        self.task2 = Task.objects.create(
            title="Task 2 in Collection 2",
            details="Details for task 2",
            due_date=datetime.now().date() + timedelta(days=2),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=2)).time(),
            category="Personal",
            completed=False,
            collection=self.collection2,
            owner=self.user2,
        )

        # Create notes with titles
        self.note1 = Note.objects.create(
            title="Note 1 Title", content="Note 1 for Task 1", task=self.task1, user=self.user1
        )
        self.note2 = Note.objects.create(
            title="Note 2 Title", content="Note 2 for Task 2", task=self.task2, user=self.user2
        )


class AuthenticationTests(BaseAPITestCase):
    def test_user_login(self):
        url = reverse("login")
        data = {"username": "user1", "password": "testpass123"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)
        self.assertIn("user", response.data)

        # Verify custom user fields are included
        self.assertEqual(response.data["user"]["username"], "user1")
        self.assertEqual(response.data["user"]["email"], "user1@example.com")
        self.assertEqual(response.data["user"]["phone_number"], "+1234567890")
