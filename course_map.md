# MCP Course Map

A high-level map of all notebooks, client scripts, server scripts, and deployment components.

---
## 1. Notebooks (Training)
Located in `notebooks/`:

- **L3.ipynb** – Introduction to MCP Client & Server
- **L4.ipynb** – Progressive improvements to the client
- **L5.ipynb** – MCP client v2
- **L6.ipynb** – MCP client v3 (multi-server, tools, prompts)
- **L7.ipynb** – Prompts & Resources; advanced server

---
## 2. MCP Chatbot Clients
Located in `client/`:

- **mcp_chatbot.py** – Version 1
- **mcp_chatbot_v2.py** – Version 2
- **mcp_chatbot_v3.py** – Version 3 (final local version)
- **mcp_chatbot_L7.py** – Version aligned with Lesson 7

Run them via:
```
uv run client/mcp_chatbot_v3.py
uv run client/mcp_chatbot_L7.py
```

---
## 3. MCP Servers (Course)
Located in `servers/`:

- **research_server.py** – Base version
- **research_server_L7.py** – Version aligned with Lesson 7
- **research_server_L9.py** – Version for Lesson 9 (remote server concepts)

Run them with:
```
uv run servers/research_server.py
```

These servers are referenced by the configuration files in `config/`.

---
## 4. Hugging Face / Gradio Components
Located in project root:

- **app.py** – Gradio UI
- **research_server_HF.py** – HuggingFace-compatible MCP server
- **requirements-hf.txt** – Required dependencies for HF deployment

Run locally:
```
uv run research_server_HF.py
```

---
## 5. Core Logic & Utilities
- **research_core.py** – Main functions used by servers & UI
- **test_core.py** – Tests for the research core
- **vars.env** – API keys (do **not** commit)

---
## 6. Configuration
Located in `config/`:

- **server_config.json** – Default MCP configuration
- **server_config_L7.json** – Configuration for Lesson 7

---
## 7. Dependencies & Project Files
- **requirements.txt** – Standard dependencies
- **requirements-hf.txt** – HF dependencies
- **pyproject.toml** – Project metadata & dependencies
- **runtime.txt** – Python version

---
## Summary Table

| Area | Files | Purpose |
|------|-------|----------|
| Notebooks | L3 → L7 | Training progression |
| Clients | v1, v2, v3, L7 | MCP chatbot implementations |
| Servers | L3, L7, L9 | Server-side lesson progression |
| HF | app.py, research_server_HF.py | Web UI + cloud MCP server |
| Config | server_config*.json | Defines MCP servers to load |
| Core | research_core.py | Main logic shared by servers & UI |
| Env | vars.env | API keys |

---
This file acts as a navigation map so you always know:
- where the code lives,
- which file belongs to which lesson,
- which components interact together.
