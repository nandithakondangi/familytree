from google.adk.agents import LlmAgent

from familytree.ai.specialized_agents.data_fetcher.agent import _model

_name = "family_tree_narrator"
_model = "gemini-2.0-flash"

# The Family tree Narrator
family_tree_narrator = LlmAgent(
    name=_name,
)
