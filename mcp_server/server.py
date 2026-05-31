import json
import sys


def _has_red_flag(patient_answers: list[str]) -> bool:
    text = " ".join(patient_answers).lower()
    red_flags = [
        "essoufflement",
        "difficulte respiratoire",
        "difficulté respiratoire",
        "douleur thoracique",
        "forte fievre",
        "forte fièvre",
        "39",
        "40",
        "39.5",
        "sang",
        "malaise",
        "confusion",
    ]
    return any(flag in text for flag in red_flags)


def _has_unusable_answers(patient_answers: list[str]) -> bool:
    markers = [
        "je ne sais pas",
        "aucune idee",
        "rien a voir",
        "hors sujet",
        "test",
        "azerty",
        "qwerty",
        "blabla",
    ]
    for answer in patient_answers:
        normalized = answer.strip().lower()
        if len(normalized) < 3 or any(marker in normalized for marker in markers):
            return True
    return False


def recommend_interim_care(patient_answers: list[str] | None = None) -> str:
    patient_answers = patient_answers or []
    if _has_unusable_answers(patient_answers):
        return (
            "Recommandation intermediaire MCP : certaines reponses patient semblent "
            "incompletes ou hors sujet. Il faut reclarifier les symptomes, leur duree, "
            "la presence de fievre, les traitements en cours et les antecedents avant "
            "toute orientation. Cette recommandation ne remplace pas l'avis d'un medecin."
        )

    if _has_red_flag(patient_answers):
        return (
            "Recommandation intermediaire MCP : signes de vigilance possibles. "
            "Surveiller l'evolution, eviter l'automedication risquee et consulter "
            "rapidement un medecin ou un service d'urgence en cas d'aggravation, "
            "difficulte respiratoire, douleur intense, confusion ou fievre elevee. "
            "Cette recommandation ne remplace pas l'avis d'un medecin."
        )

    return (
        "Recommandation intermediaire MCP : repos, hydratation, surveillance des "
        "symptomes et consultation medicale si les symptomes persistent ou "
        "s'aggravent. Cette recommandation ne remplace pas l'avis d'un medecin."
    )


TOOLS = {
    "recommend_interim_care": recommend_interim_care,
}


def handle_request(request: dict) -> dict:
    request_id = request.get("id")
    method = request.get("method")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "medical-mcp-server", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [
                    {
                        "name": "recommend_interim_care",
                        "description": "Produit une recommandation intermediaire prudente.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "patient_answers": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                }
                            },
                        },
                    }
                ]
            },
        }

    if method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        if tool_name not in TOOLS:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Outil inconnu: {tool_name}"},
            }

        text = TOOLS[tool_name](**arguments)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"content": [{"type": "text", "text": text}]},
        }

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": f"Methode inconnue: {method}"},
    }


def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        response = handle_request(json.loads(line))
        print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
