import ollama
import numpy as np
from sqlalchemy import select

from assistant.models import DocumentEmbedding


def get_ai_response( user_message: str, db,  memory_facts):
    relevant_past_messages = search_history(user_message, db)
    system_prompt = ("You are a direct, Insightful, and a Practical AI advisor."
                     "CORE BEHAVIOUR RULES: "
                     "1. NEVER use phrases like 'Based on our previous conversation' "
                     "'As you mentioned', or 'It seems we discussed'"
                     "2. Use your knowledge naturally. "
                     "Do not announce that you have memory or are reading from a database."
                     "3. Provide structured, actionable advice. Do not just summarize what the user said"
                     "or ask passive validation questions (like  'Is that a fair assessment?')."
                     "\n"
                     "USER KNOWLEDGE BASE:")
    for fact in memory_facts:
        if "Not mentioned" not in str(fact.value) and str(fact.value) != "null":
            system_prompt += f"-{fact.key}: {fact.value}\n"

    messages = [{"role": "system", "content": system_prompt}]

    user_content = ""
    if relevant_past_messages:
        user_content += ("BACKGROUND CONTEXT: (Use this to inform your answer invisibly. Do not explicitly reference this seciton):\n")
        for past_msg in relevant_past_messages:
            user_content += f"-{past_msg}\n"
        user_content += "\n"

    user_content += f"CURRENT_MESSAGE: {user_message} "
    messages.append({"role": "user", "content": user_content})
    print("\n---SYSTEM PROMPT---")
    print(system_prompt)
    print("\n---USER PROMPT---")
    print(user_content)
    response = ollama.chat(
        model="llama3.1",
        messages=messages
    )

    return response["message"]["content"]

def get_memory_facts(history):
    history_string = ""
    for msg in history:
        history_string += f"{msg.role} : {msg.content}\n"
    messages = [
        {"role" : "system",
         "content" : """
    Extract important long-term memory facts about the user from the conversation.

Return ONLY valid JSON.

Format Example:
[
    {
        "key": "primary_language",
        "value": "Python"
    }
]

Rules:
- Use snake_case for all keys (e.g. programming_languages, not programmingLanguages)
- Only extract facts about the USER, not general opinions or topics discussed
- Only save personal information that is useful long term (name, skills, goals, preferences, health, background).Ignore general Opinions
- CRITICAL: If a detail (like name, age, or location) is NOT mentioned, DO NOT create a key for it. Never use values like "Not mentioned", "Unknown", or "N/A".
- If the same fact exists with a slightly different key, use the most specific standardized key
- If nothing worth saving exists, return an empty array []
- Do not add explanations
- Do not add markdown
- Do not add ```json
    """},
        {
            "role" : "user",
            "content" : f"here is the conversation history to analyze:\n\n{history_string}"
        }
    ]

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