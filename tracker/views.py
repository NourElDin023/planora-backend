# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Note, Task
from sharing.models import SharedPage
from .serializers import NoteSerializer


def has_edit_permission(user, task):
    """Check if user has edit permissions for the task's collection"""
    collection = task.collection

    # Owner has full permissions
    if collection.owner == user:
        return True

    # Check shared edit permission
    if SharedPage.objects.filter(page=collection, shared_with=user, permission="edit").exists():
        return True

    # Check link-based edit permission
    if collection.is_link_shareable and collection.shareable_permission == "edit":
        return True

    return False


@api_view(["GET", "POST"])
def notes_list(request):
    if request.method == "GET":
        # Get all tasks the user can access
        accessible_tasks = Task.objects.filter(
            Q(collection__owner=request.user)
            | Q(collection__shared_entries__shared_with=request.user)
            | Q(collection__is_link_shareable=True)
        ).distinct()

        notes = Note.objects.filter(task__in=accessible_tasks)

        # Filter by task if specified
        task_id = request.query_params.get("task")
        if task_id:
            notes = notes.filter(task=task_id)

        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.validated_data["task"]

            if not has_edit_permission(request.user, task):
                return Response(
                    {"detail": "You don't have permission to create notes for this task"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Automatically set the user from request
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def note_detail(request, pk):
    try:
        note = Note.objects.get(pk=pk)
        task = note.task
    except Note.DoesNotExist:
        return Response({"detail": "Note not found."}, status=status.HTTP_404_NOT_FOUND)

    # Check base view permission
    has_access = (
        task.collection.owner == request.user
        or task.collection.shared_entries.filter(shared_with=request.user).exists()
        or task.collection.is_link_shareable
    )

    if not has_access:
        return Response({"detail": "Note not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = NoteSerializer(note)
        return Response(serializer.data)

    elif request.method in ["PUT", "DELETE"]:
        if not has_edit_permission(request.user, task):
            return Response(
                {"detail": "You need edit permissions to modify notes"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.method == "PUT":
            serializer = NoteSerializer(note, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == "DELETE":
            note.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
