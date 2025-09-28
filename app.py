import os
import gradio as gr
from research_core import search_papers, extract_info

def ui_search(topic: str, max_results: int = 5):
    return ", ".join(search_papers(topic, max_results))

def ui_info(paper_id: str):
    return extract_info(paper_id)

demo = gr.Interface(
    fn=ui_search,
    inputs=[gr.Textbox(label="Topic"), gr.Number(value=5, label="Max results")],
    outputs="text",
    title="Research MCP (Gradio)",
    description="Search arXiv & fetch paper info"
)

if __name__ == "__main__":
    demo.launch(
        mcp_server=True,             # ← active le serveur MCP
        server_name="0.0.0.0",       # OK pour Spaces
        server_port=int(os.getenv("PORT", "7860"))
    )
