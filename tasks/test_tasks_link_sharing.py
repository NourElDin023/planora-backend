from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from users.models import User
from pages.models import Collection
from tasks.models import Task
from sharing.models import SharedPage
from datetime import date

class TaskLinkSharingTest(APITestCase):

    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username="user1", email="user1@example.com", password="password123")
        self.user2 = User.objects.create_user(username="user2", email="user2@example.com", password="password123")
        self.user3 = User.objects.create_user(username="user3", email="user3@example.com", password="password123")
        
        # Create collections
        self.collection1 = Collection.objects.create(
            title="Collection 1",
            description="Test collection 1",
            owner=self.user1
        )
        
        self.collection2 = Collection.objects.create(
            title="Collection 2 (Link Shareable)",
            description="Test collection with link sharing enabled",
            owner=self.user1,
            is_link_shareable=True,
            shareable_permission="view"
        )
        
        # Create tasks
        self.task1 = Task.objects.create(
            title="Task 1",
            details="Task details 1",
            owner=self.user1,
            collection=self.collection1,
            due_date=date.today(),
            start_time="09:00:00",
            end_time="10:00:00",
            category="Test"
        )
        
        self.task2 = Task.objects.create(
            title="Task 2 (in link-shared collection)",
            details="Task details 2",
            owner=self.user1,
            collection=self.collection2,
            due_date=date.today(),
            start_time="11:00:00",
            end_time="12:00:00",
            category="Test"
        )
        
        # Create shared page entry for user2
        SharedPage.objects.create(
            page=self.collection1,
            shared_with=self.user2,
            permission="view"
        )
    
    def test_user_cannot_see_link_shareable_tasks_without_adding_collection(self):
        """
        Test that a user cannot see tasks from a link-shareable collection without explicitly
        adding it to their shared collections.
        """
        # Log in as user2
        self.client.force_authenticate(user=self.user2)
        
        # User2 should be able to see their directly shared collection
        response = self.client.get(reverse('tasks-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # User2 should only see tasks from collection1, not the link-shareable collection2
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Task 1')
    
    def test_user_can_see_link_shareable_tasks_after_adding_collection(self):
        """
        Test that a user can see tasks from a link-shareable collection after explicitly
        adding it to their shared collections.
        """
        # Log in as user3 (no shared collections yet)
        self.client.force_authenticate(user=self.user3)
        
        # User3 should not see any tasks initially
        response = self.client.get(reverse('tasks-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
        # Now add the link-shareable collection to user3's shared collections
        response = self.client.post(
            reverse('add-to-shared', args=[self.collection2.shareable_link_token])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Now user3 should be able to see tasks from collection2
        response = self.client.get(reverse('tasks-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Task 2 (in link-shared collection)')
        
    def test_direct_collection_tasks_access_still_works(self):
        """
        Test that directly accessing a collection's tasks still works if the 
        collection is link-shareable, even without adding it
        """
        # Log in as user3 (no shared collections yet)
        self.client.force_authenticate(user=self.user3)
        
        # User3 should be able to directly access the tasks for collection2 through the tasks API with collection filter
        url = reverse('tasks-list') + f"?collection={self.collection2.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Task 2 (in link-shared collection)')
