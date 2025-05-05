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


class CollectionAPITests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user1)

    def test_get_collections_list(self):
        url = reverse("pages-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "User1 Collection")

    def test_create_collection(self):
        url = reverse("pages-list")
        data = {"title": "New Test Collection", "description": "Test description"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Collection.objects.count(), 3)
        self.assertEqual(Collection.objects.latest("id").owner, self.user1)

    def test_get_collection_with_tasks(self):
        url = reverse("collection-tasks", args=[self.collection1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["collection"]["title"], "User1 Collection")
        self.assertEqual(len(response.data["tasks"]), 1)

    def test_share_page_with_users(self):
        url = reverse("share-page")
        data = {"page_id": self.collection1.id, "usernames": ["user2"], "permission": "edit"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            SharedPage.objects.filter(
                page=self.collection1, shared_with=self.user2, permission="edit"
            ).exists()
        )

    def test_update_link_share_settings(self):
        url = reverse("page-share-settings", args=[self.collection1.id])
        data = {"is_link_shareable": True, "shareable_permission": "view"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.collection1.refresh_from_db()
        self.assertTrue(self.collection1.is_link_shareable)
        self.assertEqual(self.collection1.shareable_permission, "view")

    def test_add_to_shared_collections(self):
        # Ensure collection is link-shareable and has a valid token
        self.collection1.is_link_shareable = True
        self.collection1.shareable_permission = "view"  # Make sure permission is set
        self.collection1.save()

        # Authenticate as user2 (not the owner)
        self.client.force_authenticate(user=self.user2)

        # Make sure user2 doesn't already have access
        SharedPage.objects.filter(page=self.collection1, shared_with=self.user2).delete()

        url = reverse("add-to-shared", args=[self.collection1.shareable_link_token])
        response = self.client.post(url)

        # Debug output if needed
        if response.status_code != status.HTTP_200_OK:
            print(f"Test failed. Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            SharedPage.objects.filter(page=self.collection1, shared_with=self.user2).exists()
        )
