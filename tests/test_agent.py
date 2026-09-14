"""Tests for the ADK agent definition."""

import unittest

from app.agent import root_agent


class AgentDefinitionTests(unittest.TestCase):
    """Verify that the agent can be constructed locally."""

    def test_agent_name(self) -> None:
        self.assertEqual(
            root_agent.name,
            "summer_school_assistant",
        )

    def test_agent_has_four_tools(self) -> None:
        self.assertEqual(len(root_agent.tools), 4)

    def test_agent_has_model_and_instruction(self) -> None:
        self.assertTrue(root_agent.model)
        self.assertTrue(root_agent.instruction)


if __name__ == "__main__":
    unittest.main()