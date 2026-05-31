from .mcp_client import MCPClientError, call_mcp_tool


FALLBACK_INTERIM_CARE = (
    "Recommandation intermediaire : repos, hydratation, surveillance des symptomes. "
    "Consulter rapidement un medecin en cas d'aggravation, forte fievre, douleur "
    "intense ou difficulte respiratoire. Cette recommandation ne remplace pas "
    "l'avis d'un medecin."
)


def recommend_interim_care(patient_answers: list[str] | None = None) -> str:
    """
    Genere une recommandation intermediaire prudente via un outil MCP local.
    """
    try:
        return call_mcp_tool(
            "recommend_interim_care",
            {"patient_answers": patient_answers or []},
        )
    except MCPClientError:
        return FALLBACK_INTERIM_CARE
