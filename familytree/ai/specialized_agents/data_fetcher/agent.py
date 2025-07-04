from google.adk.agents import LlmAgent

_name = "family_tree_oracle"
_model = "gemini-2.0-flash"

# The Family tree Expert
family_tree_oracle = LlmAgent(
    name=_name,
)
