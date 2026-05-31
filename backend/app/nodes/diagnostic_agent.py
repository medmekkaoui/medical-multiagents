from langgraph.types import interrupt

from ..llm import llm
from ..state import MedicalState
from ..tools.care_tools import recommend_interim_care
from ..tools.patient_tools import ask_patient, validate_patient_answer


def diagnostic_agent(state: MedicalState):
    question_count = state.get("question_count", 0)
    patient_answers = list(state.get("patient_answers", []))

    if question_count < 5:
        base_question = ask_patient(question_count)
        feedback = state.get("invalid_answer_feedback")
        question = f"{feedback}\n\n{base_question}" if feedback else base_question
        answer = interrupt(question)

        is_valid, validation_feedback = validate_patient_answer(question_count, answer)
        if not is_valid:
            return {
                "question_count": question_count,
                "patient_answers": patient_answers,
                "current_question": base_question,
                "current_answer": answer,
                "invalid_answer_feedback": validation_feedback,
            }

        patient_answers.append(answer)

        return {
            "question_count": question_count + 1,
            "patient_answers": patient_answers,
            "current_question": base_question,
            "current_answer": answer,
            "invalid_answer_feedback": "",
        }

    prompt = f"""
    Tu es un assistant medical pour un exercice academique.

    Voici les reponses du patient :
    {patient_answers}

    Genere une synthese clinique preliminaire courte et professionnelle.
    Ne fournis pas de diagnostic definitif.
    """

    response = llm.invoke(prompt)
    interim_care = recommend_interim_care(patient_answers)

    return {
        "diagnostic_summary": response.content,
        "interim_care": interim_care,
    }
