# research_server_HF.py
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import os, json

import gradio as gr
import arxiv


# Où stocker les fichiers (sur Spaces, /tmp est sûr en écriture)
PAPERS_DIR = Path(os.environ.get("PAPERS_DIR", "/tmp/papers"))
PAPERS_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_topic_dir(topic: str) -> Path:
    d = PAPERS_DIR / topic
    d.mkdir(parents=True, exist_ok=True)
    return d


def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.

    Args:
        topic (str): The topic to search for.
        max_results (int): Maximum number of results to retrieve (default: 5).

    Returns:
        List[str]: List of paper IDs found in the search.
    """
    topic = topic.strip()
    if not topic:
        return []

    topic_dir = _ensure_topic_dir(topic)

    search = arxiv.Search(
        query=topic,
        max_results=int(max_results),
        sort_by=arxiv.SortCriterion.Relevance,
    )
    client = arxiv.Client()
    ids: List[str] = []

    for r in client.results(search):
        paper_id = r.get_short_id()
        ids.append(paper_id)
        meta = {
            "id": paper_id,
            "title": r.title,
            "authors": [a.name for a in r.authors],
            "published": r.published.isoformat() if r.published else None,
            "url": r.entry_id,
            "summary": r.summary,
            "topic": topic,
        }
        (topic_dir / f"{paper_id}.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2)
        )
        (topic_dir / f"{paper_id}.txt").write_text(
            f"{meta['title']}\n{', '.join(meta['authors'])}\n{meta['url']}\n\n{meta['summary']}"
        )

    return ids


def extract_info(paper_id: str) -> Dict[str, Any]:
    """
    Search for information about a specific paper across all topic directories.

    Args:
        paper_id (str): The ID of the paper to look for.

    Returns:
        Dict[str, Any]: Paper info if found, or {"error": "..."} if not found.
    """
    pid = paper_id.strip()
    for topic_dir in PAPERS_DIR.glob("*"):
        cand = topic_dir / f"{pid}.json"
        if cand.exists():
            return json.loads(cand.read_text())
    return {"error": f"Paper {pid} not found in {PAPERS_DIR}."}


# ——— Gradio UI (chaque "endpoint" devient un outil MCP automatiquement) ———
iface_search = gr.Interface(
    fn=search_papers,
    inputs=[gr.Textbox(label="Topic"), gr.Slider(1, 20, value=5, step=1, label="Max Results")],
    outputs=gr.JSON(label="Paper IDs"),
    title="search_papers",
    description="Search arXiv and save basic metadata.",
)

iface_extract = gr.Interface(
    fn=extract_info,
    inputs=[gr.Textbox(label="Paper ID")],
    outputs=gr.JSON(label="Paper Info"),
    title="extract_info",
    description="Load saved metadata by arXiv short ID (e.g., 1310.1984v2).",
)

demo = gr.TabbedInterface([iface_search, iface_extract], ["Search", "Info"])

if __name__ == "__main__":
    # Lance l’UI Gradio ET le serveur MCP (HTTP+SSE sur /gradio_api/mcp/sse)
    demo.launch(mcp_server=True)
