import os
import google.generativeai as genai
from rest_framework.response import Response
from rest_framework import status
from .tools import tools_list
from adrf.views import APIView as AsyncAPIView # Використовуй adrf для асинхронних DRF views
from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiExample

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="Your message to the AI assistant")

class AIChatView(AsyncAPIView):
    """
    Endpoint for communicating with the AI assistant through a classic HTTP POST request.
    """
    @extend_schema(
        request=ChatRequestSerializer,
        responses={200: dict},
        description="Send a message to the AI assistant",
        examples=[
            OpenApiExample(
                'Example request',
                value={'message': 'Find tickets to London'}
            )
        ]
    )
    async def post(self, request):
        user_message = request.data.get('message')
        
        if not user_message:
            return Response({"error": "Message is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Ініціалізуємо модель (як у консьюмері)
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                tools=tools_list,
                system_instruction="You are the official AI assistant of Airline Service..."
            )
            
            # Створюємо чат сесію (без історії для простого POST запиту, або передавай історію з фронта)
            chat_session = model.start_chat(history=[], enable_automatic_function_calling=True)
            
            # Отримуємо відповідь
            response = await chat_session.send_message_async(user_message)
            
            return Response({
                "message": response.text
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)