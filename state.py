from typing import Annotated, List, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    dataset_sample: str   # The CSV data string
    analysis_report: str  # The insights found by the Analyst
    chart_code: str       # The Python code to generate the chart
    next_step: str        # Supervisor routing decision