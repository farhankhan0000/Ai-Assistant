import ollama


def get_ai_response(user_message: str, history, memory_facts):
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
        "content" : "go through the recent messages and extract what is worth saving in key value pair."
                    "key is the title, value is the description. return as JSON only."})


    response=ollama.chat(
        model="llama3.1",
        messages=messages
    )

    return response["message"]["content"]