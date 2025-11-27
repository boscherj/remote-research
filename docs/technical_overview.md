# Remote Research – Vue technique

Ce document décrit l’architecture technique du projet **Remote Research** autour de MCP (Model Context Protocol).

Il est destiné à :
- servir de support pour les formations,
- aider un développeur à comprendre rapidement comment le projet est structuré,
- documenter les principaux scripts (client, serveurs, core).

---

## 1. Composants principaux

### 1.1 Client MCP (`client/`)

- `client/mcp_chatbot.py`
  Client MCP principal en ligne de commande :
  - lance une session MCP via STDIO vers un serveur,
  - récupère la liste des tools exposés par le serveur,
  - expose ces tools au modèle Claude d’Anthropic,
  - orchestre la boucle :
    1. l’utilisateur pose une question,
    2. Claude peut répondre directement ou demander un `tool_use`,
    3. le client exécute le tool via MCP,
    4. le résultat est renvoyé à Claude,
    5. Claude produit la réponse finale.

- `client/mcp_chatbot_commente.py`
  Version commentée ligne par ligne du client, utilisée comme support pédagogique.

- `client/mcp_chatbot_L7.py`, `client/mcp_chatbot_v2.py`, `client/mcp_chatbot_v3.py`
  Variantes utilisées dans différentes leçons / expérimentations.

### 1.2 Serveurs MCP (`servers/` + `research_server_HF.py`)

- `servers/research_server.py`
  Serveur MCP principal, lancé en local via :

  ```bash
  uv run servers/research_server.py
  ```

  Il :
  - expose des tools comme `search_papers` et `extract_info`,
  - s’appuie sur `research_core.py` pour charger et interroger les ressources de `papers/transformers/`,
  - fournit une API MCP standard (tools/list, tools/call, resources/list, etc.).

- `servers/research_server_L7.py`, `servers/research_server_L9.py`
  Variantes du serveur pour des leçons spécifiques.

- `research_server_HF.py`
  Variante adaptée à un déploiement Hugging Face Space.

### 1.3 Core métier

- `research_core.py`
  Logique métier pour charger, indexer et interroger les papiers (JSON/TXT).

- `test_core.py`
  Tests unitaires associés.

---

## 2. MCP : flux de bout en bout

1. **Démarrage du serveur :**

   ```bash
   uv run servers/research_server.py
   ```

2. **Démarrage du client :**

   ```bash
   uv run client/mcp_chatbot.py
   ```

3. **Initialisation :**
   - Le client lance ou rejoint un serveur MCP via STDIO.
   - `ClientSession.initialize()` effectue le handshake.
   - Le client récupère la liste des tools via `session.list_tools()`.

4. **Interaction complète :**
   - L’utilisateur pose une question.
   - Claude peut retourner :
     - une réponse textuelle **directe**,
     - un bloc `tool_use` pour appeler un tool.
   - Le client :
     - exécute le tool via `session.call_tool(...)`,
     - retourne un `tool_result` au modèle,
     - affiche la réponse finale.

---

## 3. Configuration

### Configurations

- `config/server_config.json`
- `config/server_config_L7.json`
- `server_config.json`

### Variables d’environnement

Créer `.env` :

```bash
ANTHROPIC_API_KEY=sk-ant-api-...
```

---

## 4. Ressources (`papers/`, `docs/`, `notebooks/`)

### Papiers de recherche

- `papers/transformers/*.json`
- `papers/transformers/*.txt`
- `papers/transformers/papers_info.json`

### Transcriptions

- `docs/transcripts/*.txt`

### Notebooks

- `notebooks/L3.ipynb` … `notebooks/L7.ipynb`

---

## 5. Points d’entrée

Client :

```bash
uv run client/mcp_chatbot.py
```

Serveur local :

```bash
uv run servers/research_server.py
```

Serveur Hugging Face :

```bash
uv run research_server_HF.py
```

Tests :

```bash
uv run pytest test_core.py
```

---

## 6. Pistes d’extension

- Ajout de nouveaux tools MCP
- Support d’autres LLM (DeepSeek, OpenAI…)
- Interface web (Gradio, Streamlit)
- Génération automatique de documentation
