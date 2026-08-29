import ollama
import numpy as np
from sqlalchemy import select

from assistant.models import DocumentEmbedding


def get_ai_response( user_message: str, db,  memory_facts):
    relevant_past_messages = search_history(user_message, db)
    system_prompt = "You are a personal assistant. Here is what you know about the user: "
    for fact in memory_facts:
        system_prompt += f"{fact.key}: {fact.value}, "
    if relevant_past_messages:
        system_prompt += "\n\nHere is some relevant context from past conversations:\n"
        for past_msg in relevant_past_messages:
            system_prompt += f"-{past_msg}\n"
    messages = [{"role" : "system", "content" : system_prompt}]
    messages.append({"role": "user", "content": user_message})
    print(system_prompt)
    response = ollama.chat(
        model="llama3.1",
        messages=messages
    )

    return response["message"]["content"]

def get_memory_facts(history):
    messages=[]
    for msg in history:
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

def get_ai_title(user_message: str):
    system_prompt = ("You are a highly efficient title generator. Your only job is to read the user's "
                     "message and summarize it into a short, relevant title."
                     "STRICT RULES: "
                     "1. The title must be between 2 and 5 words."
                     "2. Do Not use quotation marks."
                     "3. Do Not use any punctuation at the end."
                     "4. Do Not use any conversation filler like Here is your title or Sure."
                     "5. Output ONLY the words of the title and absolutely nothing else.")

    messages = [
        {"role" : "system", "content" : system_prompt},
        {"role" : "user", "content" : f"User Message: {user_message}\nTitle: "}
    ]



    response = ollama.chat(
        model="llama3.1",
        messages=messages
    )

    return response["message"]["content"]

def get_vector(user_message: str):
    memory_vector = np.array(ollama.embeddings(model="nomic-embed-text", prompt=user_message)["embedding"])
    return memory_vector

def search_history(user_message: str, db):
    current_message = get_vector(user_message)
    results = db.scalars(select(DocumentEmbedding)
                         .order_by(DocumentEmbedding.embedding.cosine_distance(current_message))
                         .limit(3)).all()
    return [item.content for item in results]