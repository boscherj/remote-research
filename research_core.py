# Pour HuggingFace
# research_core.py
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Dict

import arxiv


# ---------- utils ----------
def _safe_id(pid: str) -> str:
    """
    Transforme un ID arXiv en nom de fichier sûr.
    Exemple: 'gr-qc/0612006v1' -> 'gr-qc_0612006v1'
    """
    return (
        pid.replace("/", "_")
        .replace("\\", "_")
        .replace(":", "-")
        .strip()
    )


# ---------- API principale (utilisable sans MCP) ----------
def search_papers(topic: str, max_results: int = 5, base_dir: str | Path = "papers") -> List[str]:
    """
    Recherche des papiers sur arXiv, stocke leur meta en JSON (et un .txt du résumé),
    et retourne la liste des paper_ids arXiv (non ‘safe’, c.-à-d. l’ID d’origine).

    Dossiers créés: papers/<topic>/
    Fichiers: <safe_id>.json, <safe_id>.txt
    """
    base = Path(base_dir)
    topic_dir = base / topic
    topic_dir.mkdir(parents=True, exist_ok=True)

    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    results: List[str] = []

    for paper in search.results():
        # Champs utiles
        paper_id = paper.get_short_id()  # ex: '2508.12345v1' ou 'gr-qc/0612006v1'
        title = paper.title or ""
        summary = (paper.summary or "").strip()
        authors = [a.name for a in getattr(paper, "authors", [])]
        published = paper.published.isoformat() if getattr(paper, "published", None) else None
        url = paper.entry_id or ""

        # Ecriture sur disque (safe filename)
        safe_id = _safe_id(paper_id)
        data: Dict[str, object] = {
            "paper_id": paper_id,  # on garde l'ID original pour retrouver l’article
            "title": title,
            "summary": summary,
            "authors": authors,
            "published": published,
            "url": url,
            "topic": topic,
        }

        (topic_dir / f"{safe_id}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # Optionnel: résumé brut pour consultation rapide
        (topic_dir / f"{safe_id}.txt").write_text(summary, encoding="utf-8")

        results.append(paper_id)

    return results


def extract_info(paper_id: str, base_dir: str | Path = "papers") -> Optional[Dict]:
    """
    Retrouve l’info JSON d’un paper_id (ID d’origine arXiv), en scannant tous les topics.
    Retourne le dict si trouvé, sinon None.
    """
    base = Path(base_dir)
    if not base.exists():
        return None

    safe = _safe_id(paper_id)

    # On cherche dans papers/*/<safe_id>.json
    for json_path in base.glob(f"*/{safe}.json"):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        # Par sécurité, on vérifie qu'on retombe bien sur le paper_id recherché
        if isinstance(data, dict) and data.get("paper_id") == paper_id:
            return data

    return None


__all__ = ["search_papers", "extract_info"]
