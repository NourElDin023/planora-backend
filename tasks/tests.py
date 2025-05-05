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
from users.tests import BaseAPITestCase


class TaskAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user1)

    def test_get_tasks_list(self):
        url = reverse("tasks-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Task 1 in Collection 1")

    def test_get_tasks_filtered_by_collection(self):
        url = reverse("tasks-list") + f"?collection={self.collection1.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Task 1 in Collection 1")

    def test_create_task(self):
        url = reverse("tasks-list")
        data = {
            "title": "New Task",
            "details": "Task details",
            "due_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "category": "Work",
            "completed": False,
            "collection": self.collection1.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 3)
        self.assertEqual(Task.objects.latest("id").owner, self.user1)

    def test_create_task_with_shared_permission(self):
        self.client.force_authenticate(user=self.user2)
        data = {
            "title": "New Task by User2",
            "details": "Task details",
            "due_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "category": "Work",
            "completed": False,
            "collection": self.collection1.id,  # Collection shared with edit permission
        }
        response = self.client.post(reverse("tasks-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 3)
