from langgraph.types import interrupt

from ..state import MedicalState


def physician_review(state: MedicalState):
    """
    Etape Human-in-the-Loop : le medecin valide la synthese et saisit
    une conduite a tenir avant la generation du rapport final.
    """
    summary = state.get("diagnostic_summary", "Synthese non disponible")
    interim_care = state.get("interim_care", "Recommandation non disponible")

    physician_input = interrupt(
        {
            "message": "Validation medecin requise",
            "diagnostic_summary": summary,
            "interim_care": interim_care,
            "instruction": "Veuillez saisir le traitement ou la conduite a tenir.",
        }
    )

    return {"physician_treatment": physician_input}
