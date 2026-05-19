import json
import os
import google.generativeai as genai
from channels.generic.websocket import AsyncWebsocketConsumer
from .tools import tools_list

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=tools_list,
            system_instruction=(
                "You are the official AI assistant of Airline Service. "
                "Use tools to search for real flights in our database. "
                "If there are no flights in the database, clearly say so. "
                "Do not invent flights yourself. "
                "Respond only to topics related to the airline services in our project. "
                "CRITICAL RULE: You must always communicate and respond exclusively in English, "
                "regardless of the user's language or the language of the provided tools."
            )
        )
        self.chat_session = self.model.start_chat(history=[], enable_automatic_function_calling=True)

        await self.send(text_data=json.dumps({
            'message': 'Connection established. I have access to the flight database!'
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data.get('message', '')

        try:
            response = await self.chat_session.send_message_async(user_message)

            await self.send(text_data=json.dumps({
                'message': response.text
            }))

        except Exception as e:
            print(f"Consumer error: {e}")
            await self.send(text_data=json.dumps({
                'message': f"Oops, a problem occurred: {str(e)}"
            }))