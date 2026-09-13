# Gritt

### Conversational AI with Persistent Memory

Gritt is a conversational AI application designed to maintain useful context across conversations 
through structured memory and semantic retrieval.

It combines persistent user-specific facts with embedding-based retrieval of relevant past conversations, 
allowing responses to be informed by both long-term memory and previous interactions.

**[Live Demo](https://gritt-delta.vercel.app/)**

## What Gritt Can Do

- Maintain persistent user-specific memory
- Store and retrieve conversation history
- Retrieve semantically relevant past messages using embeddings
- Use retrieved context when generating responses
- Generate conversation titles automatically
- Support authenticated multi-user conversations

## Memory Architecture

Gritt currently uses two complementary forms of memory.

### Structured Memory

Durable user-specific facts are extracted from conversation history and stored as key-value records in 
PostgreSQL.

For example:

`preferred_language → Python`

These facts are loaded when generating future responses and provide persistent user context.

### Semantic Memory

User messages are converted into embeddings using Google's Gemini embedding model and stored in the database.
When a new message arrives, Gritt generates an embedding for it and performs cosine-similarity search 
against previously stored messages. The most relevant results are retrieved and supplied as additional 
context to the language model.


## How a Message Is Processed

1. The user sends a message from the frontend.
2. FastAPI authenticates the request using JWT.
3. The message is stored in PostgreSQL.
4. Recent conversation history is loaded.
5. Persistent memory facts for the user are loaded.
6. The current message is converted into an embedding.
7. Similar past messages are retrieved using cosine similarity.
8. Relevant context, memory, and recent history are provided to the LLM.
9. The generated response is returned to the frontend.
10. Background processing stores the new embedding and extracts durable memory facts.

## Architecture

### Frontend
- HTML
- CSS
- JavaScript
- Authentication and chat interface
- Conversation management

### Backend
- FastAPI
- SQLAlchemy
- Pydantic
- JWT authentication
- PostgreSQL
- Background tasks

### Database
- PostgreSQL (hosted on Neon)

### AI Layer
- Groq
- GPT-OSS-20B
- Gemini Embeddings
- Semantic retrieval
- Memory extraction


## Testing

The backend is tested using pytest.
Tests cover the application's endpoints and core functions, including successful requests,
validation failures, authentication failures, and error-handling paths.


## Deployment

- Frontend: Vercel
- Backend API: Render
- Database: PostgreSQL
[Live Frontend](https://gritt-delta.vercel.app/)
[Live BACKEND](https://gritt-api.onrender.com/)

## Project Journey

Gritt grew alongside my learning in software and AI engineering. Building it required me to work 
through frontend development, backend APIs, authentication, databases, embeddings, vector similarity search,
retrieval-augmented generation, persistent memory, testing, and deployment.
Rather than following a single implementation, I built the system incrementally as 
I learned the concepts required for each part.

## Vision

Gritt started with a broader idea: building a personal AI system that could act as an autonomous assistant.

The long-term vision is for it to work with sources such as emails, messages, and schedules, 
identify important information, keep track of things that matter, remind me about upcoming events and tasks,
and eventually support natural voice conversations.

Gritt is the first foundation toward that idea. Rather than trying to build the entire system at once,
I focused first on conversational interaction, persistent memory, semantic retrieval,
and the backend infrastructure required to support them.
