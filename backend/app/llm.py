import ast
import os
import re
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


@dataclass
class LLMResponse:
    content: str


def _extract_patient_answers(prompt: str) -> list[str]:
    match = re.search(r"Voici les reponses du patient\s*:\s*(\[.*?\])", prompt, re.S)
    if not match:
        return []

    try:
        parsed = ast.literal_eval(match.group(1))
    except (SyntaxError, ValueError):
        return []

    if not isinstance(parsed, list):
        return []

    return [str(item).strip() for item in parsed]


def _extract_section(prompt: str, title: str) -> str:
    pattern = rf"{re.escape(title)}\s*:\s*(.*?)(?:\n\s*\n|$)"
    match = re.search(pattern, prompt, re.S | re.I)
    return match.group(1).strip() if match else ""


def _is_unusable_answer(answer: str) -> bool:
    normalized = answer.strip().lower()
    if len(normalized) < 3:
        return True

    unusable_markers = [
        "je ne sais pas",
        "aucune idee",
        "rien a voir",
        "hors sujet",
        "test",
        "azerty",
        "qwerty",
        "blabla",
        "kkkk",
        "hhhh",
    ]
    return any(marker in normalized for marker in unusable_markers)


def _has_red_flag(text: str) -> bool:
    normalized = text.lower()
    red_flags = [
        "essoufflement",
        "difficulte respiratoire",
        "difficulté respiratoire",
        "douleur thoracique",
        "forte fievre",
        "forte fièvre",
        "39",
        "40",
        "sang",
        "malaise",
        "confusion",
    ]
    return any(flag in normalized for flag in red_flags)


class MedicalLLM:
    def __init__(self):
        self._client = None
        if os.getenv("OPENAI_API_KEY"):
            self._client = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                temperature=0.2,
            )

    def invoke(self, prompt: str):
        if self._client is not None:
            try:
                return self._client.invoke(prompt)
            except Exception:
                pass

        return LLMResponse(content=self._fallback_response(prompt))

    def _fallback_response(self, prompt: str) -> str:
        lower_prompt = prompt.lower()

        if "rapport" in lower_prompt:
            return self._fallback_report(prompt)

        return self._fallback_summary(prompt)

    def _fallback_summary(self, prompt: str) -> str:
        answers = _extract_patient_answers(prompt)
        usable_answers = [answer for answer in answers if not _is_unusable_answer(answer)]
        unusable_count = len(answers) - len(usable_answers)
        joined_answers = " | ".join(answers) if answers else "Aucune reponse patient disponible."

        red_flag_sentence = (
            "Des signes de vigilance sont mentionnes et doivent etre verifies rapidement."
            if _has_red_flag(joined_answers)
            else "Aucun signe de gravite evident n'est identifiable a partir des reponses fournies."
        )

        quality_sentence = (
            f"{unusable_count} reponse(s) semblent incompletes ou hors sujet; la fiabilite de "
            "l'orientation est donc limitee."
            if unusable_count
            else "Les reponses sont globalement exploitables pour une orientation preliminaire."
        )

        return (
            "Synthese clinique preliminaire :\n"
            f"- Reponses patient recueillies : {joined_answers}\n"
            f"- Qualite des informations : {quality_sentence}\n"
            f"- Orientation prudente : {red_flag_sentence}\n"
            "- Conclusion : ces elements ne permettent pas un diagnostic definitif et doivent "
            "etre valides par le medecin traitant."
        )

    def _fallback_report(self, prompt: str) -> str:
        summary = _extract_section(prompt, "Synthese") or "Synthese non disponible."
        interim_care = _extract_section(prompt, "Recommandation") or "Recommandation non disponible."
        physician_treatment = _extract_section(prompt, "Avis medecin") or "Avis medecin non renseigne."

        return (
            "Rapport medical final\n\n"
            f"1. Synthese clinique preliminaire\n{summary}\n\n"
            f"2. Recommandation intermediaire\n{interim_care}\n\n"
            f"3. Avis du medecin traitant\n{physician_treatment}\n\n"
            "4. Mention obligatoire\n"
            "Ce systeme ne remplace pas une consultation medicale."
        )


llm = MedicalLLM()
