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


class NoteAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user1)

    def test_get_notes_list(self):
        url = reverse("notes-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Note 1 Title")

    def test_get_notes_filtered_by_task(self):
        url = reverse("notes-list") + f"?task={self.task1.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Note 1 Title")

    def test_create_note(self):
        url = reverse("notes-list")
        data = {"title": "New Note Title", "content": "New Note Content", "task": self.task1.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 3)
        self.assertEqual(Note.objects.latest("id").user, self.user1)

    def test_create_note_no_permission(self):
        data = {"title": "New Note Title", "content": "New Note Content", "task": self.task2.id}
        response = self.client.post(reverse("notes-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_note_detail(self):
        url = reverse("note-detail", args=[self.note1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Note 1 Title")

    def test_update_note(self):
        url = reverse("note-detail", args=[self.note1.id])
        data = {
            "title": "Updated Note Title",
            "content": "Updated Note Content",
            "task": self.task1.id,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.title, "Updated Note Title")

    def test_delete_note(self):
        url = reverse("note-detail", args=[self.note1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Note.objects.count(), 1)
