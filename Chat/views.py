import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import os
from dotenv import load_dotenv


load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Optional: Keep chat history in memory (you can store it in a DB instead)
chat_history = {}

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_with_assistant(request):
    try:
        user_id = request.data.get("user_id", "default")  # Track users if needed
        message = request.data.get("message", "").strip()

        if not message:
            return Response({"error": "No message provided"}, status=400)

        # Reuse chat session per user (optional enhancement)
        if user_id not in chat_history:
            model = genai.GenerativeModel("models/gemini-1.5-pro")
            chat = model.start_chat()
            chat_history[user_id] = chat
        else:
            chat = chat_history[user_id]

        response = chat.send_message(message)

        return Response({"response": response.text})

    except Exception as e:
        import traceback
        print("=== Gemini Chat Error ===")
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)
