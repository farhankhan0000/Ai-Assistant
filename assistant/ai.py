import ollama
from assistant.models import MemoryFact


def get_ai_response( user_message: str, history, memory_facts):
    system_prompt = "You are a personal assistant. Here is what you know about the user: "
    for fact in memory_facts:
        system_prompt += f"{fact.key}: {fact.value}, "
    messages = [{"role" : "system", "content" : system_prompt}]
    for msg in history:
        messages.append({"role" : msg.role, "content" : msg.content})
    messages.append({"role": "user", "content": user_message})
    response = ollama.chat(
        model="llama3.1",
        messages=messages
    )

    return response["message"]["content"]

def get_memory_facts(history):
    recent_history = history[-10:]
    messages=[]
    for msg in recent_history:
        messages.append({"role" : msg.role, "content" : msg.content})
    messages.append({"role" : "user",
        "content" : """
    Extract important long-term memory facts about the user from the conversation.

Return ONLY valid JSON.

Format:
[
    {
        "key": "name",
        "value": "Farhan Khan"
    }
]

Rules:
- Use snake_case for all keys (e.g. programming_languages, not programmingLanguages)
- Only extract facts about the USER, not general opinions or topics discussed
- Only save personal information that is useful long term (name, skills, goals, preferences, health, background)
- If the same fact exists with a slightly different key, use the most specific standardized key
- If nothing worth saving exists, return an empty array []
- Do not add explanations
- Do not add markdown
- Do not add ```json
    """})

    response=ollama.chat(
        model="llama3.1",
        messages=messages
    )



    return response["message"]["content"]