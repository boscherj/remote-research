"""
mcp_chatbot_commente.py
------------------------

Version commentée du client MCP pour Claude (Anthropic).

Ce fichier est prévu pour être ouvert directement dans un IDE comme VS Code.
Il contient :
- le code original de ton client MCP,
- des commentaires détaillés (en français) destinés à des informaticiens,
  pour comprendre la logique globale et le rôle de chaque partie.

Le but est pédagogique : tu peux t’en servir comme support de cours ou de révision.
"""

# --- Imports et configuration globale ---------------------------------------

from dotenv import load_dotenv  # Pour charger les variables d'environnement depuis un fichier .env
from anthropic import Anthropic  # Client Python officiel pour appeler les modèles Claude

# Primitives MCP : gestion de la session côté client, lancement serveur en STDIO, typage
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client  # Helper pour se connecter à un serveur MCP via stdin/stdout

from typing import List  # Annotation de type générique pour les listes
import asyncio           # Boucle événementielle asynchrone
import nest_asyncio      # Permet de patcher asyncio pour supporter les boucles imbriquées (notamment en notebooks)

# Patch de la boucle asyncio actuelle pour permettre des exécutions imbriquées (utile en environnements interactifs)
nest_asyncio.apply()

# Chargement des variables d'environnement depuis le fichier .env à la racine du projet
# (par exemple : ANTHROPIC_API_KEY)
load_dotenv()


# --- Classe principale du chatbot MCP ---------------------------------------

class MCP_ChatBot:
    """
    Encapsule toute la logique du chatbot :
    - gestion de la session MCP,
    - initialisation du client Anthropic,
    - orchestration entre le modèle Claude et les tools MCP,
    - boucle d'interaction avec l'utilisateur (en ligne de commande).
    """

    def __init__(self) -> None:
        """
        Constructeur : initialise les attributs principaux
        sans encore démarrer la connexion MCP.
        """
        # Session MCP active (sera initialisée plus tard dans connect_to_server_and_run)
        self.session: ClientSession | None = None

        # Client Anthropic utilisé pour tous les appels au modèle Claude
        self.anthropic = Anthropic()

        # Liste des tools disponibles côté MCP, au format attendu par l'API Anthropic
        # Chaque élément est un dict : {"name": ..., "description": ..., "input_schema": ...}
        self.available_tools: List[dict] = []

    # ---------------------------------------------------------------------
    # Orchestration d'une requête utilisateur : modèle Claude + tools MCP
    # ---------------------------------------------------------------------
    async def process_query(self, query: str) -> None:
        """
        Traite une requête utilisateur :
        1. envoie la question à Claude avec la liste des tools disponibles,
        2. inspecte la réponse :
           - si c'est du texte simple, on affiche et on s'arrête,
           - si le modèle veut appeler un tool (tool_use), on exécute ce tool via MCP,
        3. renvoie le résultat du tool au modèle,
        4. boucle jusqu'à ce que le modèle donne une réponse finale (texte seul).
        """
        # Historique de la conversation côté Anthropic.
        # Format attendu : liste de dicts {"role": "...", "content": ...}
        messages = [
            {
                "role": "user",
                "content": query,  # ici, content est simplement une chaîne de caractères
            }
        ]

        # Premier appel au modèle Claude avec la requête utilisateur.
        # On fournit la liste des tools MCP dans le paramètre "tools".
        response = self.anthropic.messages.create(
            max_tokens=2024,                        # Limite de tokens pour la réponse
            model="claude-3-7-sonnet-20250219",     # Identifiant du modèle Claude utilisé
            tools=self.available_tools,             # Tools exposés au modèle (tool calling)
            messages=messages,                      # Historique de la conversation
        )

        # Flag pour contrôler la boucle de traitement tant que le modèle
        # n'a pas fourni de réponse finale purement textuelle.
        process_query = True

        # Boucle principale : on traite la réponse courante de Claude
        # et on relance éventuellement un nouvel appel si des tools sont utilisés.
        while process_query:
            # Contenu de la réponse de l'assistant pour ce tour (texte + éventuels tool_use)
            assistant_content = []

            # La réponse peut contenir plusieurs blocs : texte, tool_use, etc.
            for content in response.content:
                # -----------------------------------------------------------------
                # 1) Cas "texte simple" : le modèle répond directement à l'utilisateur
                # -----------------------------------------------------------------
                if content.type == "text":
                    # On affiche le texte pour l'utilisateur dans la console
                    print(content.text)

                    # On garde ce bloc dans assistant_content pour l'historique si besoin
                    assistant_content.append(content)

                    # Si la réponse ne contient qu'un seul bloc (ce texte),
                    # on considère que la requête est complètement traitée
                    if len(response.content) == 1:
                        process_query = False

                # -----------------------------------------------------------------
                # 2) Cas "tool_use" : le modèle souhaite appeler un outil MCP
                # -----------------------------------------------------------------
                elif content.type == "tool_use":
                    # On ajoute le tool_use au contenu de l'assistant pour ce tour
                    assistant_content.append(content)

                    # On pousse ce tour assistant (texte éventuel + tool_use) dans l'historique
                    messages.append(
                        {
                            "role": "assistant",
                            "content": assistant_content,
                        }
                    )

                    # Récupération des informations nécessaires pour exécuter le tool MCP
                    tool_id = content.id        # identifiant unique du tool_use dans cette réponse
                    tool_args = content.input   # arguments du tool (dict)
                    tool_name = content.name    # nom du tool à appeler côté MCP

                    # Log console pour visualiser les tool calls (utile en debug)
                    print(f"Calling tool {tool_name} with args {tool_args}")

                    # -----------------------------------------------------------------
                    # Appel réel du tool via la session MCP
                    # -----------------------------------------------------------------
                    # On délègue l'exécution au serveur MCP via JSON-RPC.
                    result = await self.session.call_tool(tool_name, arguments=tool_args)

                    # -----------------------------------------------------------------
                    # Encodage du résultat de tool pour le renvoyer au modèle Anthropic
                    # -----------------------------------------------------------------
                    # Convention Anthropic : on renvoie un message avec role="user"
                    # et un bloc de type "tool_result" qui référence le tool_use initial
                    # via tool_use_id.
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_id,     # lie ce résultat au tool_use correspondant
                                    "content": result.content,  # contenu renvoyé par le serveur MCP
                                }
                            ],
                        }
                    )

                    # -----------------------------------------------------------------
                    # Nouveau tour d'appel au modèle Claude
                    # -----------------------------------------------------------------
                    response = self.anthropic.messages.create(
                        max_tokens=2024,
                        model="claude-3-7-sonnet-20250219",
                        tools=self.available_tools,
                        messages=messages,
                    )

                    # Si la nouvelle réponse ne contient qu'un seul bloc texte,
                    # on l'affiche et on termine le traitement de cette requête.
                    if (
                        len(response.content) == 1
                        and response.content[0].type == "text"
                    ):
                        print(response.content[0].text)
                        process_query = False

    # ---------------------------------------------------------------------
    # Boucle interactive côté utilisateur (CLI simple)
    # ---------------------------------------------------------------------
    async def chat_loop(self) -> None:
        """
        Boucle interactive en ligne de commande.

        - Affiche un prompt "Query: ",
        - lit la saisie utilisateur,
        - appelle process_query(query),
        - s'arrête quand l'utilisateur tape 'quit'.
        """
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")

        # Boucle infinie jusqu'à la commande de sortie
        while True:
            try:
                # Lecture de l'entrée utilisateur (synchrone, côté stdin)
                query = input("\nQuery: ").strip()

                # Permet de sortir proprement de la boucle
                if query.lower() == "quit":
                    break

                # Orchestration complète de la requête (modèle + tools)
                await self.process_query(query)

                # Ligne vide pour aérer l'affichage
                print("\n")

            except Exception as e:
                # Gestion très simple des erreurs : affichage dans la console
                print(f"\nError: {str(e)}")

    # ---------------------------------------------------------------------
    # Connexion au serveur MCP (STDIO) + lancement de la boucle de chat
    # ---------------------------------------------------------------------
    async def connect_to_server_and_run(self) -> None:
        """
        Établit la connexion au serveur MCP via STDIO, initialise la session,
        récupère la liste des tools disponibles et lance la boucle interactive.

        Étapes :
        1. Construction des paramètres pour lancer le serveur MCP (command + args),
        2. Ouverture d'une connexion STDIO (stdio_client),
        3. Création d'une ClientSession MCP par-dessus ces flux,
        4. Initialisation de la session (handshake MCP),
        5. Récupération de la liste des tools et adaptation au format Anthropic,
        6. Démarrage de la boucle de chat.
        """
        # Paramètres décrivant comment lancer le serveur MCP via STDIO.
        # Ici on utilise `uv run research_server.py` comme commande.
        server_params = StdioServerParameters(
            command="uv",                    # Exécutable à lancer
            args=["run", "servers/research_server.py"],  # Arguments de ligne de commande
            env=None,                        # Variables d'environnement supplémentaires (None => héritées)
        )

        # Ouverture de la connexion STDIO vers le serveur MCP.
        # stdio_client lance le process et renvoie deux coroutines read/write.
        async with stdio_client(server_params) as (read, write):
            # Création d'une session MCP à partir des flux read/write
            async with ClientSession(read, write) as session:
                # On garde une référence à la session dans l'instance du chatbot
                self.session = session

                # Initialisation de la connexion MCP (handshake, capabilities, etc.)
                await session.initialize()

                # -----------------------------------------------------------------
                # Récupération et affichage de la liste des tools disponibles
                # -----------------------------------------------------------------
                response = await session.list_tools()
                tools = response.tools

                # Feedback console : liste les noms de tous les tools exposés par le serveur MCP
                print("\nConnected to server with tools:", [tool.name for tool in tools])

                # Conversion des descriptions de tools MCP au format attendu par l'API Anthropic.
                # Anthropic attend une liste de dicts avec : name, description, input_schema.
                self.available_tools = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema,
                    }
                    for tool in response.tools
                ]

                # Une fois la session prête et les tools connus, on lance la boucle interactive
                await self.chat_loop()


# --- Point d'entrée du script ----------------------------------------------

async def main() -> None:
    """
    Point d'entrée asynchrone du script :
    - crée une instance de MCP_ChatBot,
    - lance la connexion au serveur MCP et la boucle de chat.
    """
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_server_and_run()


if __name__ == "__main__":
    # asyncio.run() crée et gère la boucle événementielle,
    # puis exécute la coroutine main() jusqu'à complétion.
    asyncio.run(main())
