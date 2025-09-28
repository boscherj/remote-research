# app.py — Gradio Space exposant un serveur MCP, sans décorateurs

import gradio as gr

# ⬇️ import “sans framework” de ta logique métier
from research_core import search_papers, extract_info

# ⬇️ API MCP de Gradio (pas de décorateurs)
# gradio[mcp] installe le module `gradio_mcp`
from gradio.mcp import Server, Tool, create_mcp_app

# 1) Crée un serveur MCP
server = Server(name="research")

# 2) Enregistre tes fonctions pures comme outils MCP (sans décorateurs)
server.add_tool(
    Tool(
        function=search_papers,
        name="search_papers",
        description=(search_papers.__doc__ or "Search arXiv and store JSON/TXT."),
    )
)
server.add_tool(
    Tool(
        function=extract_info,
        name="extract_info",
        description=(extract_info.__doc__ or "Read stored metadata for a paper ID."),
    )
)

# 3) Construit l’app ASGI qui expose les endpoints MCP (dont /sse)
mcp_app = create_mcp_app(server)

# 4) (optionnel) Un mini-UI Gradio pour montrer que le Space tourne
with gr.Blocks() as demo:
    gr.Markdown("### Research MCP Space (HF)\nUse via MCP client at `/sse`.")
    topic = gr.Textbox(label="Topic", value="transformers")
    out = gr.Textbox(label="Paper IDs")
    btn = gr.Button("Search 2 papers")
    def _demo_call(t):
        try:
            return ", ".join(search_papers(t, max_results=2))
        except Exception as e:
            return f"Error: {e}"
    btn.click(_demo_call, [topic], [out])

# 5) Monte l’UI Gradio sur la même app ASGI (path root), MCP reste dispo sur /sse
#    -> L’app finale exportée par le Space s’appelle **app**
app = gr.mount_gradio_app(mcp_app, demo, path="/")

# HF lance l’app automatiquement, pas besoin de if __name__ == "__main__"
