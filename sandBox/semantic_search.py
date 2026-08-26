import ollama
import numpy as np

sentence_1 = "I want to learn software engineering."
sentence_2 = "Coding and building applications is my goal."
sentence_3 = "The best way to cook a steak is medium rare."

vec_1 = np.array(ollama.embeddings(model="nomic-embed-text", prompt=sentence_1)["embedding"])
vec_2 = np.array(ollama.embeddings(model="nomic-embed-text", prompt=sentence_2)["embedding"])
vec_3 = np.array(ollama.embeddings(model="nomic-embed-text", prompt=sentence_3)["embedding"])

def calculate_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    norm_1 = np.linalg.norm(v1)
    norm_2 = np.linalg.norm(v2)
    return dot_product/(norm_1*norm_2)

score_1_vs_2 = calculate_similarity(vec_1, vec_2)
score_1_vs_3 = calculate_similarity(vec_1, vec_3)

print(f"Similarity between 'Software' and 'Coding' sentences: {score_1_vs_2:.4f}")
print(f"Similarity between 'Software' and 'Food' sentences: {score_1_vs_3:.4f}")