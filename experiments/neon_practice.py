import ollama
import psycopg2
from ollama import embeddings
from pgvector.psycopg2 import register_vector
import numpy as np
from redis.commands.search import result

CONNECTION_STRING = ("postgresql://neondb_owner:npg_WTLkHM6e8sdv@ep-"
                     "royal-sound-azid8qy6-pooler.c-3.ap-southeast-1.aws.neon.tech"
                     "/neondb?sslmode=require&channel_binding=require")


conn = psycopg2.connect(CONNECTION_STRING)

register_vector(conn)
cur = conn.cursor()

memoryText = "PostgreSQL is an amazing database for AI and machine learning."
print(f"1. Embedding and saving to cloud: '{memoryText}'")

memoryVector = np.array(ollama.embeddings(model="nomic-embed-Text", prompt=memoryText)["embedding"])

cur.execute(
    "INSERT INTO document_embeddings (content, embedding) VALUES (%s, %s)",
    (memoryText,memoryVector)
)
conn.commit()

searchText = "I love data storage systems that understand math."
print(f"f\n2. Searching database for something similar to: '{searchText}'")

searchVector = np.array(ollama.embeddings(model="nomic-embed-Text", prompt=searchText)["embedding"])

cur.execute("SELECT content FROM document_embeddings ORDER BY embedding <=> %s LIMIT 1",
            (searchVector,))

result = cur.fetchone()

print("\n3. Match found in the database: ")
print(result[0])

cur.close()
conn.close()