# Rapport technique court

## Architecture

Le projet est separe en quatre blocs :

- `backend/app/graph.py` construit le graphe LangGraph.
- `backend/app/nodes/` contient les agents : supervision, diagnostic, revue medecin et rapport.
- `backend/app/tools/` contient les tools patient et le client MCP.
- `mcp_server/server.py` expose un outil MCP local via JSON-RPC stdio.
- `frontend/index.html` fournit une interface React statique connectee a l'API FastAPI.

## Workflow

1. L'utilisateur saisit un cas patient.
2. Le `Diagnostic Agent` pose 5 questions successives via `ask_patient`.
3. Les reponses sont conservees dans l'etat LangGraph.
4. Le systeme produit une synthese clinique preliminaire.
5. Le tool MCP `recommend_interim_care` genere une recommandation prudente.
6. `Physician Review` interrompt le graphe pour recueillir l'avis du medecin.
7. `Report Agent` produit le rapport final avec la mention ethique obligatoire.

## Choix realises

- `MemorySaver` permet de reprendre les interruptions pendant l'execution de l'API.
- SQLite sauvegarde les resultats principaux afin de consulter les rapports generes.
- Le LLM utilise OpenAI si `OPENAI_API_KEY` est disponible, sinon un fallback local permet de tester le projet sans cle.
- L'integration MCP est locale et legere, adaptee au besoin academique d'appeler au moins un outil via un serveur MCP.

## Tests effectues

- Appel direct du graphe avec 5 reponses patient et validation medecin.
- Test API complet avec `FastAPI TestClient`.
- Verification de l'appel MCP local pour la recommandation intermediaire.
