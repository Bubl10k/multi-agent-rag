# Multi-Agent RAG System

Stack:
- Python
- FastAPI
- LangGraph
- LangChain
- Next.js
- PostgreSQL + pgvector


## Description

A monorepo for a multi-agent RAG (Retrieval-Augmented Generation) system.
The system allows users to manage their own AI agents, each with an isolated vector knowledge store.
Users can interact with pre-built agents or create their own, upload documents to expand the agent's knowledge,
and choose which LLM powers the agent.
Each agent's response pipeline is built with LangGraph and can be visualized in the web UI.
The system is accessible via a CLI tool and a web interface.


## Requirements

### Core
1. CLI tool to interact with the system from the terminal.
2. Web interface for browser-based access.
3. Streaming responses in real-time via WebSockets.
4. Conversation history — the system remembers context within a session.

### Agents
1. Pre-built agents ready to use (e.g., Programming, Invoice Generation).
2. Ability to create a custom agent via the web UI.
3. Each agent has its own isolated vector knowledge store (pgvector).
4. Ability to upload and index documents into an agent's knowledge store (PDF, TXT, MD, etc.).
5. Natural language querying over the agent's indexed documents.
6. LLM selection per agent — choose from OpenAI, Anthropic, Gemini, etc. with your own API key.

### Orchestration
1. LangGraph visualization — view the response pipeline graph for each agent in the web UI.
2. Meta-agent with a Router — delegates tasks to specialized agents across sessions. *(Phase 2)*

### Bonus
1. LangGraph graph constructor — build and modify agent pipelines via the web UI. *(Backlog)*


## Usage of this application

### 1. Set up an agent
- On first login, a set of pre-built agents is available (e.g., Programming, Invoice).
- Or create a new agent: give it a name, select an LLM and provide your API key, and optionally upload documents to its knowledge store.

### 2. Expand the knowledge store
- Open any agent and go to the **Knowledge** tab.
- Upload PDF, TXT, or MD files — they will be parsed, chunked, embedded, and indexed automatically.

### 3. Chat with an agent
- Open an agent and start a chat session.
- Ask questions in natural language — the agent retrieves relevant chunks from its knowledge store and generates a streaming response.
- Conversation history is preserved within the session.

### 4. Inspect the pipeline
- Open the **Pipeline** tab on any agent to see a visual graph of its LangGraph flow.

### 5. CLI usage
```bash
# Query an agent
rag query --agent programming "how do I reverse a linked list?"

# Upload a document to an agent's knowledge store
rag upload --agent programming ./docs/algorithms.pdf
```
