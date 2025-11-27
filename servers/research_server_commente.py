# ---------------------------------------------------------------------------
# research_server.py
# ---------------------------------------------------------------------------
# Ce fichier implémente un petit serveur MCP basé sur FastMCP.
# Il expose deux tools :
#   - search_papers(topic, max_results) : cherche des papiers sur arXiv
#                                        et stocke leurs métadonnées en local.
#   - extract_info(paper_id)           : récupère les informations d'un papier
#                                        (préalablement sauvegardé) à partir
#                                        de son identifiant arXiv.
#
# Ce serveur est ensuite lancé en mode STDIO pour être utilisé par un client MCP
# (par exemple le mcp_chatbot côté client).
# ---------------------------------------------------------------------------

import arxiv           # Bibliothèque Python pour interroger l'API arXiv
import json            # Pour sérialiser/désérialiser les métadonnées au format JSON
import os              # Pour manipuler le système de fichiers (répertoires, chemins...)
from typing import List
from mcp.server.fastmcp import FastMCP  # Implémentation simplifiée de serveur MCP


# Répertoire racine dans lequel on va stocker les informations sur les papiers.
# La structure finale ressemblera à :
#   papers/
#     <topic1>/
#       papers_info.json
#     <topic2>/
#       papers_info.json
PAPER_DIR = "papers"

# Initialisation de l'objet serveur FastMCP.
# Le nom "research" sera le nom du serveur MCP, utilisé par les clients.
mcp = FastMCP("research")


@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.

    Args:
        topic: The topic to search for
        max_results: Maximum number of results to retrieve (default: 5)

    Returns:
        List of paper IDs found in the search
    """

    # Création d'un client arxiv pour interroger l'API.
    # La bibliothèque gère la pagination, les requêtes HTTP, etc.
    client = arxiv.Client()

    # Construction de l'objet de recherche.
    # - query : mots-clés recherchés.
    # - max_results : limite du nombre de résultats renvoyés.
    # - sort_by : tri par "Relevance" pour avoir les papiers jugés les plus pertinents d'abord.
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    # Exécution de la recherche via le client arxiv.
    # `client.results(search)` renvoie un itérable de "paper" (objets arxiv.Result).
    papers = client.results(search)

    # Construction du chemin de stockage pour ce "topic" particulier.
    # On normalise le nom du topic :
    #   - passage en minuscules
    #   - remplacement des espaces par underscore (_)
    # Exemple : "Large Language Models" -> "large_language_models"
    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))

    # Création récursive du dossier (ne plante pas si le dossier existe déjà).
    os.makedirs(path, exist_ok=True)

    # Fichier JSON dans lequel on va stocker (ou mettre à jour) les métadonnées des papiers.
    file_path = os.path.join(path, "papers_info.json")

    # On tente de lire le contenu existant du fichier JSON pour :
    #   - ne pas perdre les anciens papiers,
    #   - et pouvoir mettre à jour ou enrichir l'ensemble.
    try:
        with open(file_path, "r") as json_file:
            papers_info = json.load(json_file)
    # Deux cas où l'on considère qu'il n'y a pas de données valides :
    #   - FileNotFoundError : le fichier n'existe pas (première exécution sur ce topic).
    #   - json.JSONDecodeError : le fichier existe mais contient du JSON invalide.
    except (FileNotFoundError, json.JSONDecodeError):
        papers_info = {}

    # Liste qui servira à renvoyer les identifiants de tous les papiers trouvés.
    paper_ids = []

    # Parcours de l'itérable de résultats renvoyé par arxiv.
    for paper in papers:
        # Récupération de l'identifiant "court" (sans la version ou l'URL complète).
        # Exemple : "2209.07474v3"
        short_id = paper.get_short_id()
        paper_ids.append(short_id)

        # Construction d'un dictionnaire de métadonnées pour ce papier.
        # On extrait :
        #   - le titre,
        #   - la liste des auteurs (noms),
        #   - le résumé / abstract,
        #   - l'URL du PDF,
        #   - la date de publication (convertie en string YYYY-MM-DD).
        paper_info = {
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "summary": paper.summary,
            "pdf_url": paper.pdf_url,
            "published": str(paper.published.date()),
        }

        # On enregistre l'entrée dans le dictionnaire global "papers_info",
        # indexée par l'identifiant court du papier.
        papers_info[short_id] = paper_info

    # Une fois tous les papiers traités, on écrase (ou crée) le fichier JSON
    # avec la nouvelle version de "papers_info".
    # indent=2 permet un JSON lisible humainement.
    with open(file_path, "w") as json_file:
        json.dump(papers_info, json_file, indent=2)

    # Message de log côté serveur, utile pour savoir où les résultats ont été stockés.
    print(f"Results are saved in: {file_path}")

    # La valeur de retour de la fonction est la liste des IDs de papiers trouvés.
    # C'est ce qui sera renvoyé au client MCP (et donc au LLM, puis à l'utilisateur).
    return paper_ids


@mcp.tool()
def extract_info(paper_id: str) -> str:
    """
    Search for information about a specific paper across all topic directories.

    Args:
        paper_id: The ID of the paper to look for

    Returns:
        JSON string with paper information if found, error message if not found
    """

    # L'objectif de cette fonction est de retrouver les informations d'un papier
    # à partir de son identifiant `paper_id`, sans avoir à connaître le "topic"
    # (puisque les papiers sont rangés par topic dans différents sous-dossiers).
    #
    # La stratégie :
    #   - Parcourir tous les sous-répertoires du dossier PAPER_DIR,
    #   - Chercher à chaque fois un fichier "papers_info.json",
    #   - Charger ce fichier, et vérifier si `paper_id` est présent dans le JSON.

    # Parcours de tous les éléments du répertoire `PAPER_DIR` (ex: papers/).
    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)

        # On ne s'intéresse qu'aux sous-dossiers (chaque sous-dossier représente un topic).
        if os.path.isdir(item_path):
            # Chemin vers le fichier JSON qui contient les métadonnées des papiers pour ce topic.
            file_path = os.path.join(item_path, "papers_info.json")

            # On ne tente de lire que si le fichier existe réellement.
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as json_file:
                        papers_info = json.load(json_file)

                        # Si l'identifiant recherché est présent dans ce fichier, on le retourne immédiatement.
                        # On renvoie une string JSON plutôt qu'un dict (pour être "LLM-friendly" côté client MCP).
                        if paper_id in papers_info:
                            return json.dumps(papers_info[paper_id], indent=2)

                # En cas d'erreurs d'I/O ou de JSON invalide, on logge l'erreur et on continue.
                # On ne lève pas d'exception car on veut continuer d'explorer les autres dossiers.
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Error reading {file_path}: {str(e)}")
                    continue

    # Si on arrive ici, c'est qu'aucun des fichiers "papers_info.json" n'a contenu l'ID recherché.
    # On renvoie un message d'erreur textuel.
    return f"There's no saved information related to paper {paper_id}."


# Point d'entrée du script lorsqu'il est exécuté directement.
# Exemple :
#   uv run servers/research_server.py
if __name__ == "__main__":
    # Démarrage du serveur MCP avec un transport basé sur STDIO.
    # Cela signifie que le serveur lit les requêtes JSON-RPC sur stdin
    # et écrit les réponses sur stdout.
    # C'est le mode de fonctionnement standard attendu par la plupart
    # des clients MCP (dont ton mcp_chatbot).
    mcp.run(transport="stdio")
