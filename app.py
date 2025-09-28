import os
import gradio as gr
from research_core import search_papers, extract_info

# ---- Fonctions UI (deviennent des outils MCP) ----
def ui_search(topic: str, max_results: int = 5):
    return ", ".join(search_papers(topic, max_results))

def ui_info(paper_id: str):
    return extract_info(paper_id)

# ---- Deux Interfaces séparées ----
demo_search = gr.Interface(
    fn=ui_search,
    inputs=[gr.Textbox(label="Topic"), gr.Number(value=5, label="Max results")],
    outputs="text",
    title="Search papers",
    description="Search arXiv and list paper IDs",
)

demo_info = gr.Interface(
    fn=ui_info,
    inputs=[gr.Textbox(label="Paper ID (ex: 1310.1984v2)"]],
    outputs="text",
    title="Extract paper info",
    description="Fetch stored JSON/TXT for a given paper ID",
)

# ---- UI combinée (onglets) => les 2 fonctions deviennent 2 outils MCP ----
with gr.Blocks(title="Research MCP (Gradio)") as demo:
    gr.Markdown("## Research MCP (Gradio)\nDeux outils : recherche & extraction d'infos.")
    with gr.Tab("Search"):
        demo_search.render()
    with gr.Tab("Info"):
        demo_info.render()

# Sur Hugging Face Spaces, le script est exécuté comme __main__, donc on lance :
if __name__ == "__main__":
    demo.launch(
        mcp_server=True,             # ← active le serveur MCP
        server_name="0.0.0.0",       # OK pour Spaces
        server_port=int(os.getenv("PORT", "7860")),
    )
