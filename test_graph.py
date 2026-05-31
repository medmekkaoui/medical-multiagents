from langgraph.types import Command

from backend.app.graph import graph


config = {"configurable": {"thread_id": "test-graph-demo"}}

initial_state = {
    "messages": [{"role": "user", "content": "Patient avec toux et fievre."}],
    "question_count": 0,
    "patient_answers": [],
}

result = graph.invoke(initial_state, config=config)
print("Question initiale :", result["__interrupt__"][0].value)

for answer in [
    "Depuis 3 jours",
    "Oui, 38.5 degres",
    "Toux et fatigue",
    "Aucun medicament",
    "Aucun antecedent important",
]:
    result = graph.invoke(Command(resume=answer), config=config)

print("Revue medecin :", result["__interrupt__"][0].value)

result = graph.invoke(
    Command(resume="Surveillance, repos, hydratation et consultation si aggravation."),
    config=config,
)

print("\n=== RAPPORT FINAL ===\n")
print(result.get("final_report"))
