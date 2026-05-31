# Medical Multi-Agents

Projet academique d'orientation clinique preliminaire base sur LangGraph, FastAPI, MCP et un frontend React statique.

## Avancement par rapport au cahier des charges

- LangGraph : graphe avec `Supervisor`, `Diagnostic Agent`, `Physician Review` et `Report Agent`.
- Human-in-the-Loop : interruptions patient pour 5 questions, puis interruption medecin avant le rapport final.
- Tools : questions patient via `patient_tools.py`, recommandation intermediaire via outil MCP local.
- FastAPI : endpoints obligatoires disponibles, plus export PDF et historique simple.
- Frontend : interface React statique dans `frontend/index.html`.
- Persistance : sauvegarde SQLite des syntheses, recommandations, avis medecin et rapports.
- LangGraph Studio : configuration disponible dans `backend/langgraph.json`.

## Installation

Depuis la racine du projet :

```powershell
uv sync
```

Si `uv` n'est pas disponible :

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r backend\requirements.txt
```

Optionnel, pour utiliser OpenAI au lieu du fallback local :

```powershell
$env:OPENAI_API_KEY="votre_cle"
$env:OPENAI_MODEL="gpt-4o-mini"
```

## Base de donnees

```powershell
.\.venv\Scripts\python.exe -m backend.create_db
```

## Lancer l'API

Depuis la racine :

```powershell
.\.venv\Scripts\uvicorn.exe backend.app.api:app --reload --host 127.0.0.1 --port 8000
```

Documentation interactive :

- http://127.0.0.1:8000/docs

## Lancement rapide

Pour lancer le backend, le frontend React et ouvrir le navigateur avec une seule commande :

```powershell
.\start_project.bat
```

Si un ancien serveur est deja lance et que les changements ne sont pas visibles :

```powershell
.\restart_project.bat
```

Ou directement en PowerShell :

```powershell
powershell -ExecutionPolicy Bypass -File .\start_project.ps1
```

## Lancer le frontend React

Ouvrir le fichier :

```text
frontend/index.html
```

Ou le servir localement :

```powershell
.\.venv\Scripts\python.exe -m http.server 5500 --directory frontend
```

Puis ouvrir :

```text
http://127.0.0.1:5500/index.html
```

Le frontend appelle l'API sur `http://localhost:8000`.

## Endpoints principaux

- `POST /sessions/start`
- `POST /consultation/start`
- `POST /consultation/resume`
- `GET /consultation/{thread_id}`
- `GET /consultation/{thread_id}/report`
- `GET /consultation/{thread_id}/report/pdf`
- `GET /consultations`

## Tester le workflow

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend\tests
```

## LangGraph Studio

Depuis le dossier `backend` :

```powershell
langgraph dev
```

Le fichier `backend/langgraph.json` expose le graphe `medical_graph`.

## Limite ethique

Ce projet est un exercice academique. Il produit une orientation clinique preliminaire et ne doit pas etre presente comme un dispositif medical. Le rapport final contient explicitement : "Ce systeme ne remplace pas une consultation medicale."
"# medical-multiagents" 
