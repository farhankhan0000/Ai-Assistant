import ollama

text_to_embed = "I am learning how to build AI Application"

response = ollama.embeddings(
    model = "nomic-embed-text",
    prompt=text_to_embed
)

vector_math = response["embedding"]

print(f"Total numbers in this array: {len(vector_math)}")
print(f"The first 5 coordinates of the meaning: {vector_math[:5]}")