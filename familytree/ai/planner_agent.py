from google_adk import agents


class PlannerAgent(agents.Agent):
    """An agent that creates a plan based on a user query."""

    def __init__(self, name: str = "Planner"):
        super().__init__(name=name)

    def __call__(self, query: str) -> dict[str, str]:
        # In a real app, you'd use an LLM here to generate a plan.
        # For this example, we'll use a simple rule-based approach.
        print(f"[{self.name}] Received query: {query}")
        plan = f"Simple plan to address the query: '{query}'"
        print(f"[{self.name}] Created plan: {plan}")
        return {"plan": plan}
