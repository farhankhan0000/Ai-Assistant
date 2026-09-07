import ollama
import os
import json
import numpy as np
from redis.multidb import exception
from sqlalchemy import select, true
from assistant.models import DocumentEmbedding
from datetime import datetime
from groq import Groq
from pydantic import BaseModel,Field

groq_client = Groq(api_key=os.getenv("GROQ_KEY"))

class MemoryFact(BaseModel):
    key: str=Field(description="snake_case identifier for the fact")
    value: str=Field(description="the extracted fact value")


class MemoryFactResponse(BaseModel):
    facts: list[MemoryFact]



def get_ai_response( user_message: str, db,  memory_facts, history):
    current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    system_prompt = (f"You are a direct, Insightful, and a Practical AI advisor.\n"
                     "CORE BEHAVIOUR RULES: \n"
                     f"CURRENT SYSTEM TIME : {current_time}\n"
                     "1. NEVER use phrases like 'Based on our previous conversation' "
                     "'As you mentioned', or 'It seems we discussed'"
                     "2. Use your knowledge naturally. "
                     "Do not announce that you have memory or are reading from a database."
                     "3. Provide structured, actionable advice. Do not just summarize what the user said"
                     "or ask passive validation questions (like  'Is that a fair assessment?')."
                     "4. Output ONLY your response. NEVER Prefix your reply with labels like 'assistant: ',"
                     "'AI: ' or your role"
                     "5. When the user says a casual greeting like 'Hey' or 'Hi', respond with a welcoming, professional"
                     " tone and immediately ask how you can help them achieve their goals or what project they are working on.\n\n"
                     "USER KNOWLEDGE BASE:")

    for fact in memory_facts:
        if "Not mentioned" not in str(fact.value) and str(fact.value) != "null":
            system_prompt += f"-{fact.key}: {fact.value}\n"

    messages = [{"role": "system", "content": system_prompt}]

    past_context = ""

    formal_words = ["hi", "hey", "hello", "ok", "thankyou", "haha", "ha", "yo", "welcome", "sayonara", "bye",
                    "oh"]

    formal_words_present = False
    for words in formal_words:
        if user_message.lower().strip("!.?, ") == words:
            formal_words_present = True
    if not formal_words_present:
        relevant_past_messages = search_history(user_message, db)
        if relevant_past_messages:
            past_context += "BACKGROUND CONTEXT: (Use this to inform your answer invisibly. Do not explicitly reference this section):\n"
            for past_msg in relevant_past_messages:
                past_context += f"-{past_msg}\n"

            messages.append({"role" : "system", "content" : past_context})


    if history:
        messages.append({
            "role" : "system", "content" : "The following messages are your recent chronological interactions"
                                           " with the user, Use them to maintain Conversational flow."
        })

        for msg in history:
            messages.append({"role" : msg.role, "content" : msg.content})

    messages.append({"role" : "user", "content" : user_message})


    print("\n---- MESSAGE PAYLOAD ---\n")
    for m in messages:
        print(f"[{m['role'].upper()}] : {m['content']}\n")

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.7,
        max_tokens=1024
    )

    return response.choices[0].message.content

def get_memory_facts(history:list) -> list[dict]:
    """
    Extracts durable, user-specific facts from conversation history.
    Returns a Python list of dicts: [{"key": "...", "value": "..."}]
    """
    if len(history) < 2:
        return []
    history_string = "\n".join(f"{msg.role}: {msg.content}" for msg in history)

    system_prompt = """You are a precise long-term memory extraction engine.
    Analyze the user's statements in the conversation and extract durable personal facts.

    Rules:
    1. Extract ONLY facts explicitly stated by the USER (skills, goals, preferences, background, constraints).
    2. Ignore assistant messages, conversational filler, greetings, and temporary task context.
    3. Use concise snake_case for all keys (e.g., `preferred_ide`, `experience_level`).
    4. NEVER assume or infer values not stated (no "unknown", "n/a", or default guesses).
    5. If no new long-term facts about the user exist, return an empty list.

    Examples:
    - User: "I mostly write backend code in Go, and I use Neovim."
      Output: [{"key": "primary_language", "value": "Go"}, {"key": "preferred_editor", "value": "Neovim"}]
    - User: "Can you explain how quicksort works?"
      Output: []"""

    try:
        response=ollama.chat(
            model="llama3.1:8b",
            messages=[
                {"role" : "system", "content" :  system_prompt},
                {"role" : "user",
                 "content" : f"Conversation history:\n\n{history_string}\n\nExtract facts:"},
            ],
            format=MemoryFactResponse.model_json_schema(),
            options={
                "temperature" : 0.0,
                "num_predict" : 512
            }
        )

        raw_content = response["message"]["content"]
        parsed = json.loads(raw_content)
        return parsed.get("facts", [])

    except json.JSONDecodeError:
        return []
    except exception as e:
        print(f"Extraction error: {e}")
        return []

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