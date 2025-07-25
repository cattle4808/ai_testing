import time
import base64
import openai
import re
import json

from core.settings import OPENAI_API_KEY

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

ASSISTANT_NAME = "TestSolver"
MODEL = "gpt-4o"
INSTRUCTIONS = """
Ты эксперт, который решает любые задачи с изображений (в основном тесты).
Твоя задача:
1. Изучи изображение.
2. Найди вопрос и варианты ответов.
3. Определи, что именно спрашивается.
4. Реши логически, шаг за шагом.
5. Если надо — используй знания, интернет и код.
6. В конце обязательно выведи JSON строго такого формата:

{
  "question": "текст вопроса",
  "options": "варианты ответа (одной строкой)",
  "answer": "правильный ответ (например: A или B)",
  "message": "объяснение, почему именно так"
}
"""


def get_or_create_assistant() -> str:
    assistants = openai_client.beta.assistants.list().data
    for a in assistants:
        if a.name == ASSISTANT_NAME:
            return a.id

    assistant = openai_client.beta.assistants.create(
        name=ASSISTANT_NAME,
        instructions=INSTRUCTIONS,
        tools=[
            {"type": "code_interpreter"},
            {"type": "web_search"}
        ],
        model=MODEL
    )
    return assistant.id


def solve_image_with_assistant(image_base64: str) -> dict:
    assistant_id = get_or_create_assistant()

    image_bytes = base64.b64decode(image_base64)
    file = openai_client.files.create(file=image_bytes, purpose="assistants")

    thread = openai_client.beta.threads.create()

    openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content="Реши задачу по картинке. Используй код, поиск, логику. В конце дай JSON.",
        file_ids=[file.id]
    )

    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    while True:
        run = openai_client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status in ["completed", "failed", "cancelled"]:
            break
        time.sleep(1)

    messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
    content = messages.data[0].content[0].text.value

    json_match = re.search(r"\{[\s\S]*?\"question\"[\s\S]*?\}", content)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    return {
        "question": "Не найден JSON",
        "options": "N/A",
        "answer": "N/A",
        "message": content[:700]
    }
