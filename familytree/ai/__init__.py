from google_adk import graph

from familytree.ai.executor_agents import ExecutorAgent
from familytree.ai.planner_agent import PlannerAgent


def create_agent_team():
    """Creates and configures the agent team graph."""
    planner = PlannerAgent()
    executor = ExecutorAgent()

    # The graph defines the data flow.
    # The output of `planner` ("plan") is mapped to the input of `executor` ("plan").
    agent_graph = graph.Graph()
    agent_graph.add_agent(planner, is_entry=True)
    agent_graph.add_agent(executor)
    agent_graph.add_edge(planner, executor, {"plan": "plan"})

    return agent_graph
