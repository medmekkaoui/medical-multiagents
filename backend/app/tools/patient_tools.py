import re


QUESTIONS = [
    "Depuis quand avez-vous ces symptomes ?",
    "Avez-vous de la fievre ? Si oui, quelle temperature environ ?",
    "Avez-vous des douleurs, une toux, une fatigue ou un essoufflement ?",
    "Prenez-vous actuellement des medicaments ?",
    "Avez-vous des antecedents medicaux importants ?",
]


UNUSABLE_MARKERS = [
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


def ask_patient(question_count: int) -> str:
    """
    Retourne la question suivante a poser au patient.
    """
    if question_count < len(QUESTIONS):
        return QUESTIONS[question_count]

    return "Toutes les questions ont deja ete posees."


def validate_patient_answer(question_count: int, answer: str) -> tuple[bool, str]:
    """
    Valide une reponse patient selon la question courante.
    Si elle est hors sujet, le graphe repose la meme question.
    """
    normalized = answer.strip().lower()
    if len(normalized) < 3 or any(marker in normalized for marker in UNUSABLE_MARKERS):
        return False, "Reponse non exploitable. Merci de repondre clairement a la question."

    validators = [
        _has_duration,
        _has_fever_information,
        _has_symptom_information,
        _has_medication_information,
        _has_history_information,
    ]

    if question_count >= len(validators):
        return True, ""

    if validators[question_count](normalized):
        return True, ""

    return False, _feedback_for(question_count)


def _has_duration(answer: str) -> bool:
    duration_words = [
        "depuis",
        "jour",
        "jours",
        "semaine",
        "semaines",
        "mois",
        "hier",
        "aujourd",
        "matin",
        "soir",
        "heure",
        "heures",
    ]
    return any(word in answer for word in duration_words) or bool(re.search(r"\d+", answer))


def _has_fever_information(answer: str) -> bool:
    fever_words = [
        "oui",
        "non",
        "fievre",
        "fièvre",
        "temperature",
        "température",
        "degre",
        "degré",
        "chaud",
        "aucune",
        "pas",
    ]
    return any(word in answer for word in fever_words) or bool(re.search(r"\b3[5-9](?:[,.]\d)?\b|\b40(?:[,.]\d)?\b", answer))


def _has_symptom_information(answer: str) -> bool:
    symptom_words = [
        "douleur",
        "toux",
        "fatigue",
        "essoufflement",
        "respirer",
        "respiration",
        "gorge",
        "tete",
        "tête",
        "ventre",
        "aucun",
        "non",
        "pas",
    ]
    return any(word in answer for word in symptom_words)


def _has_medication_information(answer: str) -> bool:
    medication_words = [
        "aucun",
        "non",
        "pas",
        "medicament",
        "médicament",
        "traitement",
        "paracetamol",
        "doliprane",
        "ibuprofene",
        "antibiotique",
        "prends",
        "prendre",
    ]
    return any(word in answer for word in medication_words)


def _has_history_information(answer: str) -> bool:
    history_words = [
        "aucun",
        "non",
        "pas",
        "antecedent",
        "antécédent",
        "asthme",
        "diabete",
        "diabète",
        "hypertension",
        "allergie",
        "maladie",
        "operation",
        "opération",
    ]
    return any(word in answer for word in history_words)


def _feedback_for(question_count: int) -> str:
    feedbacks = [
        "Reponse non exploitable. Precisez la duree, par exemple : depuis 2 jours.",
        "Reponse non exploitable. Indiquez s'il y a de la fievre et la temperature si possible.",
        "Reponse non exploitable. Indiquez les symptomes presents ou dites clairement aucun.",
        "Reponse non exploitable. Indiquez les medicaments pris ou dites clairement aucun.",
        "Reponse non exploitable. Indiquez les antecedents medicaux ou dites clairement aucun.",
    ]
    return feedbacks[question_count] if question_count < len(feedbacks) else feedbacks[0]
