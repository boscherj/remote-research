import os
import gradio as gr
from research_core import search_papers, extract_info

def ui_search(topic: str, max_results: int = 5) -> str:
    ids = search_papers(topic, max_results)
    return ", ".join(ids)

def ui_info(paper_id: str) -> str:
    return extract_info(paper_id)

with gr.Blocks() as demo:
    gr.Markdown("# Research MCP (Gradio)\nCherche sur arXiv et récupère les infos d’un papier.")

    with gr.Tab("Search"):
        t = gr.Textbox(label="Topic")
        n = gr.Number(value=5, label="Max results")
        out_ids = gr.Textbox(label="Paper IDs (comma-separated)")
        gr.Button("Search").click(ui_search, [t, n], out_ids)

    with gr.Tab("Info"):
        pid = gr.Textbox(label="Paper ID (ex: 1310.1984v2)")
        out_info = gr.Textbox(label="Paper info (JSON)")
        gr.Button("Get info").click(ui_info, [pid], out_info)

# Sur HF Spaces, on lance avec mcp_server=True pour exposer l’endpoint MCP
demo.launch(
    mcp_server=True,
    server_name="0.0.0.0",
    server_port=int(os.getenv("PORT", "7860"))
)
