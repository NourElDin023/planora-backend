# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Note
from .serializers import NoteSerializer
from django.http import JsonResponse


# views.py
@api_view(["GET", "POST"])
def notes_list(request):
    if request.method == "GET":
        # Get notes for specific task
        task_id = request.query_params.get("task")
        notes = Note.objects.filter(user=request.user)

        if task_id:
            notes = notes.filter(task=task_id)

        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            # Ensure task belongs to user
            task = serializer.validated_data["task"]
            if task.owner != request.user:
                return Response({"detail": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def note_detail(request, pk):
    try:
        note = Note.objects.get(pk=pk, user=request.user)
    except Note.DoesNotExist:
        return Response({"detail": "Note not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = NoteSerializer(note)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = NoteSerializer(note, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Update owner just in case
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def hello(request):
    return JsonResponse({"message": "Welcome to the Notes App!"})
