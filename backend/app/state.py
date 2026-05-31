from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class MedicalState(TypedDict, total=False):

    # Historique des messages
    messages: Annotated[list, add_messages]

    # Nombre de questions posées
    question_count: int

    # Réponse actuelle du patient
    current_answer: str

    # Historique complet des réponses patient
    patient_answers: list[str]

    # Question actuelle
    current_question: str

    # Message de validation si une reponse patient est hors sujet
    invalid_answer_feedback: str

    # Synthèse clinique
    diagnostic_summary: str

    # Recommandation intermédiaire
    interim_care: str

    # Validation médecin
    physician_treatment: str

    # Rapport final
    final_report: str

    # Routing LangGraph
    next: str
