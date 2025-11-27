# Remote Research – MCP Project

Ce dépôt contient un projet complet autour de **MCP (Model Context Protocol)**, construit comme support de cours et de démonstration :

- un **chatbot client** qui se connecte à un ou plusieurs serveurs MCP,
- plusieurs **serveurs MCP** (local, versions de cours, version Hugging Face),
- des **ressources de recherche** (papiers, fichiers JSON/TXT),
- des **transcriptions de cours** et des **notebooks** pour apprendre MCP pas à pas.

L’objectif est double :

1. Servir de **base de travail pédagogique** pour comprendre MCP (architecture, client, serveurs, config).
2. Fournir un **assistant de recherche distant** capable d’interroger des ressources (articles, fichiers) via des tools MCP.

---

## 🧱 Fonctionnalités

- 💬 **Client MCP type chatbot** (`client/mcp_chatbot.py`) :
  - se connecte à un serveur MCP via STDIO,
  - expose dynamiquement les tools du serveur aux modèles Claude (Anthropic),
  - orchestre les tool calls et les réponses.

- 🛠️ **Serveurs MCP** (`servers/` + `research_server_HF.py`) :
  - exposent des tools comme `search_papers` et `extract_info`,
  - accèdent aux données locales (`papers/`, etc.),
  - incluent différentes variantes utilisées dans les leçons (L7, L9…).

- 📚 **Corpus de recherche** (`papers/transformers/`) :
  - fichiers `.json` et `.txt` représentant des papiers,
  - fichier d’index `papers_info.json`.

- 🧑‍🏫 **Ressources pédagogiques** :
  - transcriptions de chaque leçon MCP (`docs/transcripts/*.txt`),
  - notebooks Jupyter (`notebooks/L3.ipynb` … `L7.ipynb`),
  - plan de cours (`course_map.md`),
  - diagrammes d’architecture (`docs/mcp_architecture_diagram.txt`, `docs/mcp_diagram.txt`, `docs/mcp_summary.md`).

---

## 🏗️ Architecture générale

L’architecture suit le schéma classique MCP :

1. **Client MCP**  
   - Démarre un chatbot en ligne de commande.
   - Se connecte à un serveur MCP via STDIO (process `uv run ...`).
   - Interroge le modèle Claude avec une liste de tools MCP.
   - Exécute les tool calls via `ClientSession.call_tool(...)`.

2. **Serveur MCP**  
   - Lancé comme un process séparé (ex. `uv run servers/research_server.py`).
   - Expose des tools (ex. `search_papers`, `extract_info`) via MCP.
   - Lit et traite des ressources locales (papiers, fichiers, etc.).

3. **Ressources**  
   - Papiers de recherche (transformers) stockés dans `papers/transformers/`.
   - Scripts Python (`research_core.py`, `test_core.py`) pour manipuler ces ressources.
   - Configurations (`config/server_config.json`, `server_config.json`).

Les fichiers dans `docs/` et `notebooks/` accompagnent cette architecture pour en faire un **support de cours complet**.

---

## 📁 Structure du projet

Vue simplifiée :

```text
remote-research/
├── client/
│   ├── mcp_chatbot.py
│   ├── mcp_chatbot_commente.py
│   ├── mcp_chatbot_L7.py
│   ├── mcp_chatbot_v2.py
│   └── mcp_chatbot_v3.py
├── servers/
│   ├── research_server.py
│   ├── research_server_L7.py
│   └── research_server_L9.py
├── config/
│   ├── server_config.json
│   └── server_config_L7.json
├── docs/
│   ├── mcp_architecture_diagram.txt
│   ├── mcp_diagram.txt
│   ├── mcp_summary.md
│   └── transcripts/
├── notebooks/
├── papers/
├── research_core.py
├── research_server_HF.py
├── test_core.py
├── course_map.md
├── server_config.json
├── pyproject.toml
├── requirements.txt
└── .gitignore
```

---

## ⚙️ Prérequis

- Python **3.11+**
- [`uv`](https://github.com/astral-sh/uv)
- Une clé API Anthropic
- (Optionnel) Un compte Hugging Face pour `research_server_HF.py`

---

## 🔑 Configuration

Créer un fichier `.env` :

```bash
ANTHROPIC_API_KEY=sk-ant-api-...
```

---

## ▶️ Lancer un serveur MCP

Serveur local :

```bash
uv run servers/research_server.py
```

Serveur Hugging Face :

```bash
uv run research_server_HF.py
```

---

## 💬 Lancer le client MCP

```bash
uv run client/mcp_chatbot.py
```

---

## 🧑‍🏫 Ressources de cours

- `docs/transcripts/` : leçons
- `notebooks/` : notebooks du cours
- `client/mcp_chatbot_commente.py` : client annoté

---

## 📄 Licence

Projet pédagogique – Licence à définir.
