# 🤖 AI Agent with LangChain

A Python learning project that builds a **tool-using AI agent** with LangChain, a **Model Context Protocol (MCP)** server, and a **RAG (Retrieval-Augmented Generation)** pipeline. Everything runs locally on **Ollama**, so no API keys are needed.

The agent finds its tools at runtime from an MCP server that runs as a separate process. A separate RAG script answers questions from your own notes using a FAISS vector store.

---

## ✨ Features

### 🧠 Tool-Using Agent (`main.py`)
- Built with LangChain's `create_agent`.
- Loads its tools from the MCP server at startup instead of hard-coding them.
- Sends the user's question to the model, which decides whether and how to call a tool, then prints the final answer.

### 🔌 MCP Server (`server.py`)
- A **FastMCP** server (bundled with the `mcp` SDK) that exposes three tools:

| Tool | Description |
|---|---|
| `current_time` | Returns the current date and time (`DD-MM-YYYY HH:MM:SS`) |
| `roll_dice` | Rolls a six-sided dice |
| `generate_password` | Generates a secure random password (default length 12) |

- Communicates with the client over the **stdio** transport, so it logs to **stderr** and keeps stdout free for JSON-RPC messages.

### 🔗 MCP Client (`mcp_tools.py`)
- Uses `MultiServerMCPClient` from `langchain-mcp-adapters` to start the server and turn its MCP tools into LangChain tools.
- Starts the server with `sys.executable`, so it always runs with the same virtual environment as the app.

### 📚 RAG Pipeline (`rag.py` + `retriever.py`)
- Loads `notes.txt`, splits it into chunks of 300 characters with a 50-character overlap, and embeds them with `nomic-embed-text`.
- Stores the embeddings in an in-memory **FAISS** index.
- Answers the question **using only the retrieved context**, through an LCEL chain: `retriever → prompt → model → StrOutputParser`.

### 🧩 Shared Model (`model.py`)
- A single `ChatOllama` instance that the agent and the RAG chain both import.

### 🛠️ Extras
- `tools.py` has the same three tools written as plain LangChain `@tool` functions, a non-MCP version for comparison.
- `prompt.py` has a sample `ChatPromptTemplate` with a system persona.

---

## 🛠️ Tech Stack

- **Core:** Python 3
- **LLM runtime:** [Ollama](https://ollama.com) (local)
- **Libraries:**
  - `langchain`, `langchain-core`, `langchain-community`, `langchain-text-splitters`
  - `langchain-ollama`: chat model and embeddings
  - `langchain-mcp-adapters`: MCP client
  - `mcp`: MCP SDK, including FastMCP for the server
  - `faiss-cpu`: vector store

---

## 📁 Project Structure

```
ai-agent-langchain/
├── main.py          # Entry point: MCP-powered agent
├── mcp_tools.py     # MCP client configuration (starts server.py over stdio)
├── server.py        # MCP server exposing tools
├── model.py         # Shared ChatOllama model
├── rag.py           # RAG chain: answers questions from notes.txt
├── retriever.py     # Loads, chunks, embeds notes.txt into FAISS
├── notes.txt        # Knowledge base for RAG
├── tools.py         # Same tools as plain LangChain @tool functions
├── prompt.py        # Example prompt template
├── requirements.txt # Pinned dependencies
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/mishraabhishek11/ai-agent-langchain.git
cd ai-agent-langchain
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ **Keep `mcp` below 2.0** (pinned in `requirements.txt`). `langchain-mcp-adapters` 0.3.x is incompatible with `mcp` 2.x (see [Troubleshooting](#-troubleshooting)).

### 4. Install Ollama and pull the models
```bash
ollama pull qwen3:1.7b         # chat model (set in model.py)
ollama pull nomic-embed-text   # embedding model (used by retriever.py)
```

To use a different chat model, change the `model=` value in `model.py`. The model must support **tool calling** (for example `qwen3:4b`).

### 5. Run
```bash
python main.py   # MCP tool-using agent
python rag.py    # RAG question answering over notes.txt
```

---

## 🚀 Usage

### Agent
```
python main.py

Starting MCP server..
INFO     Processing request of type ListToolsRequest
INFO     Processing request of type CallToolRequest

FINAL ANSWER
The current date and time is 10-11-2026 12:45:26.
```

To ask something else, edit the `content` of the user message in `main.py`, for example *"Roll a dice"* or *"Generate a 16-character password"*.

### RAG
```
python rag.py

MCP stands for Model Context Protocol. It provides a standard way for AI
applications to connect to external tools and resources.
```

To change the question, edit the `chain.invoke(...)` argument in `rag.py`. To change the knowledge base, edit `notes.txt`.

---

## 🔄 How It Works

### Agent flow
1. `main.py` calls `client.get_tools()`.
2. `MultiServerMCPClient` starts `server.py` as a subprocess and connects to it over stdio.
3. The client and server do the MCP handshake (`initialize` → `list_tools`), and the MCP tools become LangChain tools.
4. `create_agent(model, tools)` builds a LangGraph agent loop.
5. The model either answers directly or makes a **tool call**. The client sends the call to the MCP server and passes the result back to the model.
6. The loop ends when the model produces a final answer.

```
User question
     │
     ▼
 ┌────────┐   tool call   ┌────────────┐   stdio / JSON-RPC   ┌───────────┐
 │ Agent  │ ────────────► │ MCP Client │ ───────────────────► │ MCP Server│
 │ (LLM)  │ ◄──────────── │            │ ◄─────────────────── │ server.py │
 └────────┘  tool result  └────────────┘                      └───────────┘
     │
     ▼
Final answer
```

### RAG flow
```
question ──► retriever (FAISS) ──► top chunks ──► prompt {context, question} ──► model ──► answer
```

---

## ➕ Adding Your Own Tool

1. Add a function to `server.py` and decorate it with `@mcp.tool()`. Include a docstring, because the model reads it to decide when to call the tool:
   ```python
   @mcp.tool()
   def add(a: int, b: int) -> int:
       """Add two numbers."""
       return a + b
   ```
2. Run `python main.py`. The agent finds the new tool automatically, with no client changes needed.

To connect another MCP server, add an entry to the dictionary in `mcp_tools.py`.

---

## 🧯 Troubleshooting

| Error | Cause / Fix |
|---|---|
| `ImportError: cannot import name 'RequestContext' from 'mcp.shared.context'` | `mcp` 2.x is installed, but `langchain-mcp-adapters` requires 1.x. Run `pip install "mcp>=1.9,<2"`. |
| `McpError: Connection closed` | The MCP server crashed on startup. Run `python server.py` directly to see the real error. Common causes are a missing package in the interpreter that runs it, or something printed to **stdout** in the server. |
| `FastMCP server support is not installed` / `No module named 'mcp.server.request_state'` | The standalone `fastmcp` 4.x package needs `mcp` 2.x. Import the bundled version instead: `from mcp.server.fastmcp import FastMCP`. |
| `ollama._types.ResponseError: model '...' not found (status code: 404)` | The model in `model.py` hasn't been pulled. Run `ollama pull <model>` or switch to a model listed by `ollama list`. |
| Connection refused to `localhost:11434` | Ollama isn't running. Start it with `ollama serve`. |
| Agent answers without calling a tool | Small models sometimes skip tools. Try a larger tool-capable model (for example `qwen3:4b`). |

---

## 🎯 Learning Objectives

- Build an agent with LangChain's `create_agent`.
- Expose tools through an **MCP server** and use them from an **MCP client**.
- Understand the stdio transport and why stdout must stay clean.
- Build a **RAG** pipeline: load → split → embed → store → retrieve → generate.
- Compose chains with **LCEL** (`|` operator).
- Run LLMs and embeddings fully locally with Ollama.

---

## 🔮 Future Enhancements

- Accept user input interactively instead of a hard-coded question.
- Combine RAG and MCP by exposing the retriever as an agent tool.
- Persist the FAISS index to disk instead of rebuilding it on every run.
- Move model names and settings into a `.env`-based config.
- Add tests for the MCP tools and the RAG chain.
- Add logging and error handling around tool and LLM calls.

---

## 🤝 Contributing

1. Fork the repository.
2. Create a branch: `git checkout -b feat/your-feature`
3. Commit with Conventional Commits: `git commit -m "feat(scope): your message"`
4. Push: `git push origin feat/your-feature`
5. Open a Pull Request.

---

## 👤 Author

**Abhishek Mishra**
GitHub: [mishraabhishek11](https://github.com/mishraabhishek11)

---

⭐ If you found this project helpful, please give it a star!
