import os
import random
import uuid
from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from users.models import User
from pages.models import Collection
from tasks.models import Task
from tracker.models import Note
from sharing.models import SharedPage

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates dummy data for demonstration purposes'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting dummy data generation...'))
        
        # Create users
        users = self._create_users()
        # Create collections
        collections = self._create_collections(users)
        # Create tasks
        tasks = self._create_tasks(collections)
        # Create notes
        self._create_notes(tasks)
        # Create sharing relationships
        self._create_sharing_relationships(collections)
        
        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data!'))
    
    def _create_users(self):
        """Create demo users with realistic profiles"""
        self.stdout.write('Creating users...')
        
        users_data = [
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'password': 'securepass123',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '+1234567890',
                'bio': 'UI/UX Designer with 5+ years experience. Love minimalist design and user-centered experiences.',
                'birthdate': '1990-05-15',
                'country': 'United States',
                'is_active': True,
            },
            {
                'username': 'sarah_smith',
                'email': 'sarah@example.com',
                'password': 'securepass123',
                'first_name': 'Sarah',
                'last_name': 'Smith',
                'phone_number': '+1987654321',
                'bio': 'Marketing professional and fitness enthusiast. Passionate about data-driven strategies.',
                'birthdate': '1988-10-22',
                'country': 'Canada',
                'is_active': True,
            },
            {
                'username': 'ahmed_hassan',
                'email': 'ahmed@example.com',
                'password': 'securepass123',
                'first_name': 'Ahmed',
                'last_name': 'Hassan',
                'phone_number': '+20123456789',
                'bio': 'Software developer specialized in full-stack web development. Coffee addict.',
                'birthdate': '1992-03-10',
                'country': 'Egypt',
                'is_active': True,
            },
            {
                'username': 'maria_garcia',
                'email': 'maria@example.com',
                'password': 'securepass123',
                'first_name': 'Maria',
                'last_name': 'Garcia',
                'phone_number': '+34612345678',
                'bio': 'Content writer and book lover. Currently working on my first novel.',
                'birthdate': '1995-07-08',
                'country': 'Spain',
                'is_active': True,
            },
            {
                'username': 'demo_user',
                'email': 'demo@example.com',
                'password': 'demo12345',
                'first_name': 'Demo',
                'last_name': 'User',
                'phone_number': '+9876543210',
                'bio': 'This is a demo account for presentation purposes. Feel free to explore all features!',
                'birthdate': '2000-01-01',
                'country': 'Demo Country',
                'is_active': True,
            }
        ]
        
        users = []
        for user_data in users_data:
            # Check if user already exists
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    phone_number=user_data['phone_number'],
                    bio=user_data['bio'],
                    birthdate=datetime.strptime(user_data['birthdate'], '%Y-%m-%d').date(),
                    country=user_data['country'],
                    is_active=user_data['is_active'],
                )
                self.stdout.write(f"Created user: {user.username}")
                users.append(user)
            else:
                user = User.objects.get(username=user_data['username'])
                self.stdout.write(f"User already exists: {user.username}")
                users.append(user)
                
        return users
    
    def _create_collections(self, users):
        """Create various collections for each user"""
        self.stdout.write('Creating collections...')
        
        collections_templates = [
            {
                'title': 'Work Projects',
                'description': 'Tasks related to my current work projects and deadlines',
                'is_link_shareable': True,
                'shareable_permission': 'view',
            },
            {
                'title': 'Personal Goals',
                'description': 'Tracking my personal development goals and habits',
                'is_link_shareable': False,
                'shareable_permission': 'view',
            },
            {
                'title': 'Home Renovation',
                'description': 'Planning and tracking my home improvement projects',
                'is_link_shareable': True,
                'shareable_permission': 'edit',
            },
            {
                'title': 'Health Tracker',
                'description': 'Track my health metrics, exercise routines and doctor appointments',
                'is_link_shareable': False,
                'shareable_permission': 'view',
            },
            {
                'title': 'Vacation Planning',
                'description': 'Ideas and plans for upcoming vacations and trips',
                'is_link_shareable': True,
                'shareable_permission': 'edit',
            },
            {
                'title': 'Reading List',
                'description': 'Books I want to read and notes on books I\'ve completed',
                'is_link_shareable': True,
                'shareable_permission': 'view',
            },
            {
                'title': 'Learning',
                'description': 'Online courses and skills I\'m developing',
                'is_link_shareable': False,
                'shareable_permission': 'view',
            },
            {
                'title': 'Shopping',
                'description': 'Shopping lists and items to buy',
                'is_link_shareable': True,
                'shareable_permission': 'edit',
            },
            {
                'title': 'Team Project Alpha',
                'description': 'Collaborative project tasks for Team Alpha',
                'is_link_shareable': True,
                'shareable_permission': 'edit',
            },
        ]
        
        collections = []
        
        # Clear existing collections if needed
        # Collection.objects.all().delete()
        
        for user in users:
            # Assign 3-5 random collections to each user
            num_collections = random.randint(3, 5)
            user_collection_templates = random.sample(collections_templates, num_collections)
            
            for template in user_collection_templates:
                collection = Collection.objects.create(
                    title=template['title'],
                    description=template['description'],
                    owner=user,
                    is_link_shareable=template['is_link_shareable'],
                    shareable_permission=template['shareable_permission'],
                )
                self.stdout.write(f"Created collection: {collection.title} for {user.username}")
                collections.append(collection)
        
        return collections
    
    def _create_tasks(self, collections):
        """Create tasks for each collection"""
        self.stdout.write('Creating tasks...')
        
        task_templates = [
            {
                'title': 'Complete project proposal',
                'details': 'Draft and submit the project proposal with budget estimates',
                'category': 'Work',
            },
            {
                'title': 'Weekly team meeting',
                'details': 'Discuss project progress and address any blockers',
                'category': 'Meeting',
            },
            {
                'title': 'Gym workout',
                'details': '45 min cardio + strength training',
                'category': 'Health',
            },
            {
                'title': 'Prepare presentation',
                'details': 'Prepare slides for the client presentation next week',
                'category': 'Work',
            },
            {
                'title': 'Call mom',
                'details': 'Check in with mom about her doctor\'s appointment',
                'category': 'Personal',
            },
            {
                'title': 'Buy groceries',
                'details': 'Milk, eggs, bread, vegetables, and fruits',
                'category': 'Shopping',
            },
            {
                'title': 'Pay utility bills',
                'details': 'Electricity, internet, and water bills',
                'category': 'Finance',
            },
            {
                'title': 'Read book chapter',
                'details': 'Read chapter 5 of "Atomic Habits"',
                'category': 'Learning',
            },
            {
                'title': 'Car maintenance',
                'details': 'Take car for regular service check-up',
                'category': 'Errands',
            },
            {
                'title': 'Write blog post',
                'details': 'Draft article on productivity tips',
                'category': 'Content',
            },
            {
                'title': 'Dentist appointment',
                'details': 'Regular check-up at Dr. Smith\'s clinic',
                'category': 'Health',
            },
            {
                'title': 'Research vacation destinations',
                'details': 'Look up options for summer vacation',
                'category': 'Travel',
            },
            {
                'title': 'Fix kitchen faucet',
                'details': 'Replace washer to stop the leak',
                'category': 'Home',
            },
            {
                'title': 'Review code PR',
                'details': 'Review pull request #127 for the authentication module',
                'category': 'Development',
            },
            {
                'title': 'Plan dinner party',
                'details': 'Create menu and guest list for Saturday dinner',
                'category': 'Social',
            },
        ]
        
        tasks = []
        now = timezone.now()
        
        for collection in collections:
            # Create 3-8 tasks per collection
            num_tasks = random.randint(3, 8)
            collection_task_templates = random.sample(task_templates, num_tasks) if len(task_templates) >= num_tasks else task_templates
            
            for idx, template in enumerate(collection_task_templates):
                # Randomize due dates between today and next 30 days
                days_ahead = random.randint(0, 30)
                due_date = (now + timedelta(days=days_ahead)).date()
                
                # Randomize start and end times
                start_hour = random.randint(8, 16)
                duration_hours = random.randint(1, 3)
                start_time = time(start_hour, 0, 0)
                end_time = time(start_hour + duration_hours, 0, 0)
                
                # Randomize completion status
                # Tasks due in the past or today have higher chance of being completed
                if days_ahead <= 0:
                    completed = random.random() < 0.8
                elif days_ahead <= 7:
                    completed = random.random() < 0.3
                else:
                    completed = random.random() < 0.1
                    
                task = Task.objects.create(
                    title=template['title'],
                    details=template['details'],
                    due_date=due_date,
                    start_time=start_time,
                    end_time=end_time,
                    category=template['category'],
                    completed=completed,
                    collection=collection,
                    owner=collection.owner,
                )
                
                self.stdout.write(f"Created task: {task.title} for collection {collection.title}")
                tasks.append(task)
        
        return tasks
    
    def _create_notes(self, tasks):
        """Create notes for selected tasks"""
        self.stdout.write('Creating notes...')
        
        note_templates = [
            {
                'title': 'Meeting notes',
                'content': 'Discussed project timeline and deliverables. Action items:\n- Follow up with design team\n- Schedule follow-up meeting\n- Send summary to stakeholders'
            },
            {
                'title': 'Ideas',
                'content': 'Potential approaches to solving the problem:\n1. Implement caching layer\n2. Optimize database queries\n3. Consider using a CDN for static assets'
            },
            {
                'title': 'Progress update',
                'content': '- Completed first phase of the project\n- Found potential issues with the current approach\n- Need to revisit initial assumptions'
            },
            {
                'title': 'Resources',
                'content': 'Helpful links:\n- https://example.com/documentation\n- https://example.com/tutorial\n- Book: "Advanced Techniques" chapter 7'
            },
            {
                'title': 'Questions to ask',
                'content': '1. What is the expected timeline?\n2. Who is the main stakeholder?\n3. What are the success metrics?\n4. Are there any existing solutions?'
            },
            {
                'title': 'Research findings',
                'content': 'Based on initial research:\n- Market size is approximately $2.5B\n- Main competitors: CompA, CompB, CompC\n- Key differentiators: price, features, support'
            },
            {
                'title': 'Feedback received',
                'content': 'Feedback from beta testers:\n- Interface is intuitive\n- Loading times could be improved\n- Missing export functionality\n- Overall positive reception'
            },
        ]
        
        # Add notes to approximately 40% of tasks
        for task in random.sample(tasks, int(len(tasks) * 0.4)):
            # Add 1-3 notes per task
            num_notes = random.randint(1, 3)
            task_note_templates = random.sample(note_templates, num_notes) if len(note_templates) >= num_notes else note_templates
            
            for template in task_note_templates:
                note = Note.objects.create(
                    title=template['title'],
                    content=template['content'],
                    task=task,
                    user=task.owner,
                )
                self.stdout.write(f"Created note: {note.title} for task {task.title}")
    
    def _create_sharing_relationships(self, collections):
        """Create sharing relationships between users and collections"""
        self.stdout.write('Creating sharing relationships...')
        
        users = User.objects.all()
        
        # Share about 30% of collections that are not owned by demo_user
        sharable_collections = [c for c in collections if c.owner.username != 'demo_user']
        collections_to_share = random.sample(sharable_collections, int(len(sharable_collections) * 0.3))
        
        for collection in collections_to_share:
            # Get 1-3 users who are not the owner
            potential_users = [u for u in users if u != collection.owner]
            if not potential_users:
                continue
                
            num_users = min(random.randint(1, 3), len(potential_users))
            shared_with_users = random.sample(potential_users, num_users)
            
            for user in shared_with_users:
                # Randomly decide on permission (view/edit)
                permission = random.choice(['view', 'edit'])
                
                # Create sharing relationship if it doesn't exist
                if not SharedPage.objects.filter(page=collection, shared_with=user).exists():
                    SharedPage.objects.create(
                        page=collection,
                        shared_with=user,
                        permission=permission,
                    )
                    self.stdout.write(f"Shared collection '{collection.title}' with user {user.username} ({permission} permission)")
        
        # Make sure demo_user has access to some collections
        demo_user = User.objects.filter(username='demo_user').first()
        if demo_user:
            # Get collections not owned by demo_user
            other_collections = [c for c in collections if c.owner != demo_user]
            if other_collections:
                # Share 2-4 collections with demo_user
                num_collections = min(random.randint(2, 4), len(other_collections))
                for collection in random.sample(other_collections, num_collections):
                    permission = random.choice(['view', 'edit'])
                    if not SharedPage.objects.filter(page=collection, shared_with=demo_user).exists():
                        SharedPage.objects.create(
                            page=collection,
                            shared_with=demo_user,
                            permission=permission,
                        )
                        self.stdout.write(f"Shared collection '{collection.title}' with demo_user ({permission} permission)")