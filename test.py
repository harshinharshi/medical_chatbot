from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from utils.tools import TOOLS
from utils.state import State
from utils.nodes import assistant

# Create the graph
graph = StateGraph(State)
graph.add_node("assistant", assistant)
graph.add_node("tools", ToolNode(TOOLS))

# Set up the flow
graph.set_entry_point("assistant")
graph.add_conditional_edges("assistant", tools_condition)
graph.add_edge("tools", "assistant")

agent_executor = graph.compile()
    