# MCP Project – README

## Overview
This project provides:
- A full MCP (Model Context Protocol) training environment
- Multiple versions of MCP clients and servers
- A Hugging Face-compatible server with Gradio
- A clean and structured project layout

## Project Structure
```
mcp_project/
│
├── notebooks/                # All training notebooks L3 → L7
├── config/                   # MCP configuration files
├── docs/                     # Documentation & diagrams
├── servers/                  # MCP servers for the course
├── client/                   # MCP chatbot clients (v1 → v3 + L7)
│
├── research_core.py          # Core logic used by servers
├── research_server_HF.py     # HuggingFace-compatible MCP server
├── app.py                    # Gradio UI
├── test_core.py              # Tests for research_core
│
├── requirements.txt
├── requirements-hf.txt
├── pyproject.toml
├── runtime.txt
├── README.md
└── vars.env
```

## Running the MCP Chatbot Clients
### Version 3
```
uv run client/mcp_chatbot_v3.py
```

### Lesson 7 version
```
uv run client/mcp_chatbot_L7.py
```

These clients rely on the MCP server configuration files located in `config/`.

## Running the MCP Servers (Course Versions)
Each server corresponds to a lesson in the course:

```
uv run servers/research_server.py
uv run servers/research_server_L7.py
uv run servers/research_server_L9.py
```

These are referenced automatically by the chatbot via the configuration files.

## Running the Hugging Face MCP Server
```
uv run research_server_HF.py
```
You will see something like:
```
* Running on local URL: http://127.0.0.1:7860
* Streamable MCP URL: http://127.0.0.1:7860/gradio_api/mcp/
```

## Running the Gradio UI
```
uv run app.py
```

## Environment Variables
All API keys are stored in `vars.env`.
Do **not** commit this file.

## Notes
- Use `uv venv` to recreate the virtual environment.
- Use `uv pip install -r requirements-hf.txt` to install Hugging Face–related dependencies.
- Use `uv pip install -r requirements.txt` for basic dependencies.
