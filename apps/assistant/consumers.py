import json
import os
import google.generativeai as genai
from channels.generic.websocket import AsyncWebsocketConsumer
from .tools import tools_list

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # Підключаємо інструменти (tools)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            tools=tools_list,  # ПЕРЕДАЄМО НАШІ ФУНКЦІЇ СЮДИ
            system_instruction=(
                "Ти — офіційний ШІ-асистент Airline Service. "
                "Використовуй інструменти для пошуку реальних рейсів у нашій базі. "
                "Якщо в базі немає рейсів, так і кажи. Не вигадуй рейси самостійно. "
                "Відповідай тільки по темі авіаперевезень нашого проєкту."
            )
        )
        self.chat_session = self.model.start_chat(history=[], enable_automatic_function_calling=True)

        await self.send(text_data=json.dumps({
            'message': 'З’єднання встановлено. Я маю доступ до бази рейсів!'
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data.get('message', '')

        try:
            # ВИПРАВЛЕНО: Використовуємо асинхронний метод замість asyncio.to_thread
            response = await self.chat_session.send_message_async(user_message)

            await self.send(text_data=json.dumps({
                'message': response.text
            }))

        except Exception as e:
            # Якщо це помилка ліміту, ми побачимо її тут чітко
            print(f"❌ Помилка в Consumer: {e}")
            await self.send(text_data=json.dumps({
                'message': f"Упс, виникла проблема: {str(e)}"
            }))