from langgraph.types import Command

from backend.app.graph import graph

config = {"configurable": {"thread_id": "test-consultation-1"}}

initial_state = {
    "messages": [{"role": "user", "content": "Patient avec syndrome respiratoire simple."}],
    "question_count": 0,
    "patient_answers": [],
}

result = graph.invoke(initial_state, config=config)
print("Interruption patient 1 :", result["__interrupt__"][0].value)

answers = [
    "Depuis 3 jours",
    "Oui, 38.5 degres",
    "Toux et fatigue",
    "Aucun medicament",
    "Aucun antecedent important",
]

for index, answer in enumerate(answers, start=1):
    result = graph.invoke(Command(resume=answer), config=config)
    interrupt_value = result.get("__interrupt__", [None])[0].value
    print(f"Apres reponse {index} :", interrupt_value)

result = graph.invoke(
    Command(resume="Traitement symptomatique, surveillance et consultation si aggravation."),
    config=config,
)

print("\n=== RAPPORT FINAL ===")
print(result.get("final_report"))
