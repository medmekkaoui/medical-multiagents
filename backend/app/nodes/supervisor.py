from ..state import MedicalState


def supervisor(state: MedicalState):
    """
    Decide quelle etape executer ensuite dans le workflow.
    """
    question_count = state.get("question_count", 0)

    if question_count < 5:
        return {"next": "diagnostic_agent"}

    if not state.get("diagnostic_summary"):
        return {"next": "diagnostic_agent"}

    if not state.get("physician_treatment"):
        return {"next": "physician_review"}

    if not state.get("final_report"):
        return {"next": "report_agent"}

    return {"next": "FINISH"}
