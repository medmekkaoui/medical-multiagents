# Frontend React

Le projet garde uniquement le frontend React statique.

## Lancer le backend

Depuis la racine du projet :

```powershell
.\.venv\Scripts\uvicorn.exe backend.app.api:app --reload --host 127.0.0.1 --port 8000
```

## Lancer le frontend React

Dans un deuxieme terminal :

```powershell
.\.venv\Scripts\python.exe -m http.server 5500 --directory frontend
```

Puis ouvrir :

```text
http://127.0.0.1:5500/index.html
```
