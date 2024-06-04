import os
from typing import List, Optional
from pydantic import BaseModel
from schemas import OpenAIChatMessage
import time
import json


class Pipeline:
    class Valves(BaseModel):
        pipelines: List[str] = []
        priority: int = 0
        target_user_roles: List[str] = ["user"]
        max_turns: Optional[int] = None

    def __init__(self):
        self.type = "filter"
        self.name = "Conversation Turn Limit Filter"
        self.valves = self.Valves(
            **{
                "pipelines": os.getenv("CONVERSATION_TURN_PIPELINES", "*").split(","),
                "max_turns": 10,
            }
        )

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
        pass

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        print(f"pipe:{__name__}")
        print(body)  # Выводим содержимое body в консоль
        print(user)  # Выводим информацию о пользователе в консоль

        # Сохранение содержимого body в файл
        with open('body_content.json', 'w') as f:
            json.dump(body, f, indent=4)

        # Сохранение данных пользователя в файл
        if user:
            with open('user_content.json', 'w') as f:
                json.dump(user, f, indent=4)

        # Добавляем содержимое body в messages
        messages = body.get("messages", [])
        messages.append({
            "role": "system",
            "content": f"Request body: {body}"
        })
        body["messages"] = messages

        if user.get("role", "admin") in self.valves.target_user_roles:
            if len(messages) > self.valves.max_turns:
                raise Exception(
                    f"Conversation turn limit exceeded. Max turns: {self.valves.max_turns}"
                )

        return body
