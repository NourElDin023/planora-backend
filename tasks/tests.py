import uuid
from datetime import datetime, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from users.models import EmailVerificationToken, PasswordResetToken, User
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

    def test_create_task_with_link_sharing_permission(self):
        # Create a new test user for this specific test
        user3 = User.objects.create_user(
            username="user3",
            email="user3@example.com",
            password="testpass123"
        )
        self.client.force_authenticate(user=user3)
        data = {
            "title": "New Task by User3",
            "details": "Task details",
            "due_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "category": "Work",
            "completed": False,
            "collection": self.collection1.id,  # Collection shared with view permission
        }
        response = self.client.post(reverse("tasks-list"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Task.objects.count(), 2)


class LinkSharingTasksTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        
        # Create a link-shareable collection owned by user1
        self.link_shared_collection = Collection.objects.create(
            title="Link Shared Collection",
            description="Collection with link sharing enabled",
            owner=self.user1,
            is_link_shareable=True,
            shareable_permission="view"
        )
        
        # Create a task in the link-shareable collection
        self.link_shared_task = Task.objects.create(
            title="Task in Link Shared Collection",
            details="This task is in a link-shareable collection",
            owner=self.user1,
            collection=self.link_shared_collection,
            due_date=datetime.now().date() + timedelta(days=3),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=1)).time(),
            category="Test"
        )
    
    def test_user_cannot_see_link_shareable_tasks_without_adding_collection(self):
        """
        Test that a user cannot see tasks from a link-shareable collection without explicitly
        adding it to their shared collections.
        """
        # Log in as user2 who doesn't have access to the link_shared_collection
        self.client.force_authenticate(user=self.user2)
        
        # User2 should only see tasks from collections they own or that are explicitly shared with them
        response = self.client.get(reverse("tasks-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check all response data to ensure the link-shared task is NOT included
        titles = [task['title'] for task in response.data]
        self.assertNotIn("Task in Link Shared Collection", titles)
    
    def test_user_can_see_link_shareable_tasks_after_adding_collection(self):
        """
        Test that a user can see tasks from a link-shareable collection after explicitly
        adding it to their shared collections.
        """
        # Log in as user2
        self.client.force_authenticate(user=self.user2)
        
        # Create a SharedPage entry to simulate user2 having added the link-shared collection
        SharedPage.objects.create(
            page=self.link_shared_collection,
            shared_with=self.user2,
            permission="view"
        )
        
        # User2 should now be able to see tasks from the link-shared collection
        response = self.client.get(reverse("tasks-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the task from the link-shared collection is now included
        titles = [task['title'] for task in response.data]
        self.assertIn("Task in Link Shared Collection", titles)
        
    def test_direct_collection_tasks_access_still_works(self):
        """
        Test that directly accessing a collection's tasks still works if the 
        collection is link-shareable, even without adding it
        """
        # Log in as user2 who doesn't have access to the link_shared_collection
        self.client.force_authenticate(user=self.user2)
        
        # User2 should be able to directly access the tasks for the link-shared collection
        # This is testing the filter in the get_queryset method that allows direct collection access
        url = reverse("tasks-list") + f"?collection={self.link_shared_collection.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # There should be one task in the response
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Task in Link Shared Collection")
