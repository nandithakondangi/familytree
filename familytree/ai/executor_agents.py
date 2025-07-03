from google_adk import agents


class ExecutorAgent(agents.Agent):
    """An agent that executes a plan to generate a response."""

    def __init__(self, name: str = "Executor"):
        super().__init__(name=name)

    def __call__(self, plan: str) -> dict[str, str]:
        # In a real app, you'd use an LLM here with the plan as context.
        print(f"[{self.name}] Received plan: {plan}")
        response = f"This is the final response generated based on the plan: '{plan}'"
        print(f"[{self.name}] Generated response: {response}")
        return {"final_response": response}
