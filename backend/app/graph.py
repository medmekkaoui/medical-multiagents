from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from .nodes.diagnostic_agent import diagnostic_agent
from .nodes.physician_review import physician_review
from .nodes.report_agent import report_agent
from .nodes.supervisor import supervisor
from .state import MedicalState


builder = StateGraph(MedicalState)

builder.add_node("supervisor", supervisor)
builder.add_node("diagnostic_agent", diagnostic_agent)
builder.add_node("physician_review", physician_review)
builder.add_node("report_agent", report_agent)

builder.set_entry_point("supervisor")


def route_next(state: MedicalState):
    return state["next"]


builder.add_conditional_edges(
    "supervisor",
    route_next,
    {
        "diagnostic_agent": "diagnostic_agent",
        "physician_review": "physician_review",
        "report_agent": "report_agent",
        "FINISH": END,
    },
)

builder.add_edge("diagnostic_agent", "supervisor")
builder.add_edge("physician_review", "supervisor")
builder.add_edge("report_agent", "supervisor")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
