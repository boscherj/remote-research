# Pour tester research_core.py
# test_core.py
from research_core import search_papers, extract_info

if __name__ == "__main__":
    print("→ Recherche de 2 papiers sur le topic: transformers")
    ids = search_papers("transformers", max_results=2)
    print("IDs:", ids)

    if ids:
        first = ids[0]
        print(f"\n→ Lecture des infos pour: {first}")
        info = extract_info(first)
        if info:
            print("Titre :", info.get("title"))
            print("Auteurs :", ", ".join(info.get("authors", [])))
            print("Publié :", info.get("published"))
            print("URL    :", info.get("url"))
            print("Topic  :", info.get("topic"))
            print("\nOK: JSON + TXT écrits dans papers/<topic>/")
        else:
            print("Aucune info trouvée (JSON introuvable).")
    else:
        print("Aucun ID retourné.")
