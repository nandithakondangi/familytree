from google.adk.agents import SequentialAgent

from familytree.ai.specialized_agents.data_fetcher import family_tree_oracle
from familytree.ai.specialized_agents.response_generator import family_tree_narrator

_name = "family_tree_assistant"
_description = "User facing agent that answers user queries using the specialized skills of sub agents"

# The Query manager (Co-ordinator)
family_tree_assistant = SequentialAgent(
    name=_name,
    description=_description,
    sub_agents=[family_tree_oracle, family_tree_narrator],
)
