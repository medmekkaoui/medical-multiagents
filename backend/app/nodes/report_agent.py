from ..llm import llm
from ..state import MedicalState


def report_agent(state: MedicalState):
    prompt = f"""
    Genere un rapport medical professionnel et structure.

    Synthese :
    {state.get("diagnostic_summary")}

    Recommandation :
    {state.get("interim_care")}

    Avis medecin :
    {state.get("physician_treatment")}

    Ajouter exactement cette mention :
    "Ce systeme ne remplace pas une consultation medicale."
    """

    response = llm.invoke(prompt)
    return {"final_report": response.content}
