# test_client.py

import asyncio
import websockets
import json


async def chat():

    uri = "ws://127.0.0.1:8000/ws/chat/"

    async with websockets.connect(uri) as websocket:

        greeting = await websocket.recv()

        print(f"\n🤖 AI: {json.loads(greeting)['message']}")

        while True:

            msg = input("\n👤 Ви: ")

            if msg.lower() in ["exit", "quit"]:
                break

            await websocket.send(json.dumps({
                "message": msg
            }))

            response = await websocket.recv()

            print(f"\n🤖 AI: {json.loads(response)['message']}")


asyncio.run(chat())