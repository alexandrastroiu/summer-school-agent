"""Tests for the assistant's custom tools."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.knowledge import LocalKnowledgeProvider
from app.custom_tools import CustomTools, FILENAME

TEST_TICKET_COSTS = """
## Attractions

| Category | Full price (€) (adult) | Reduced price (€) (student, senior) | Free (child) |
| -------- | ---------------------- | ----------------------------------- | ------------ |
| Milan Cathedral Rooftop and Museum | 32.00 | 17.00 | 0.00 |
| Milan Cathedral Rooftop Terrace Only | 22.00 | 11.50 | 0.00 |
| Scala Museum | 12.00 | 8.00 | 0.00 |
| Leonardo da Vinci's Last Supper | 15.00 | 2.00 | 0.00 |
| Pinacoteca di Brera | 20.00 | 4.00 | 0.00 |
| National Museum of Science and Technology | 13.00 | 8.00 | 0.00 |
| Royal Palace of Milan | 15.00 | 13.00 | 0.00 |
| Museo del Novecento | 10.00 | 5.00 | 0.00 |

## Free attractions:

- Galleria Vittorio Emanuele II
- Parco Sempione
- Parco Solari
- Giardino di Guastalla
- Navigli District
"""

class CustomToolsTests(unittest.TestCase):
    """Test the tools using a temporary local knowledge base."""

    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        knowledge_path = Path(self.temporary_directory.name)

        (knowledge_path / FILENAME).write_text(
                    TEST_TICKET_COSTS,
                    encoding="utf-8",
        )
        
        provider = LocalKnowledgeProvider(knowledge_path)
        self.tools = CustomTools(provider)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_adult_visitor(self) -> None:
        result = self.tools.estimate_ticket_cost(1, ["adult"], ["Scala Museum", "Royal Palace of Milan"])

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total_cost"], 27.00)
        self.assertEqual(result["cost_breakdown"], {"Scala Museum": 12.00, "Royal Palace of Milan": 15.00})
        self.assertEqual(result["unavailable_prices"], [])

    def test_group(self) -> None:
        result = self.tools.estimate_ticket_cost(4, ["adult", "senior", "student", "child"], ["Scala Museum"])

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total_cost"], 28.00)

    def test_free_attraction(self) -> None:
        result = self.tools.estimate_ticket_cost(1, ["adult"], ["Galleria Vittorio Emanuele II", "Parco Sempione", "Parco Solari", "Giardino di Guastalla", "Navigli District"])

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total_cost"], 0.00)

    def test_unavailable_attraction(self) -> None:
        result = self.tools.estimate_ticket_cost(1, ["adult"], ["Eiffel Tower"])

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total_cost"], 0.00)
        self.assertEqual(result["unavailable_prices"], ["Eiffel Tower"])

    def test_negative_number_of_visitors(self) -> None:
        result = self.tools.estimate_ticket_cost(-1, ["adult"], ["Scala Museum"])

        self.assertEqual(result["status"], "error")
        self.assertIn("The number of visitors cannot be negative", result["message"])

    def test_no_attractions(self) -> None:
        result = self.tools.estimate_ticket_cost(1, ["adult"], [])

        self.assertEqual(result["status"], "error")
        self.assertIn("No tourist attractions were specified", result["message"])

    def test_invalid_visitor_category(self) -> None:
        result = self.tools.estimate_ticket_cost(1, ["tourist"], ["Scala Museum"])

        self.assertEqual(result["status"], "error")
        self.assertIn("Invalid visitor category", result["message"])

    def test_invalid_visitor_categories_length(self) -> None:
        result = self.tools.estimate_ticket_cost(1, ["adult", "senior", "student", "child"], ["Scala Museum"])

        self.assertEqual(result["status"], "error")
        self.assertIn("The number of visitor categories exceeds the number of visitors", result["message"])

    def test_missing_visitor_categories(self) -> None:
        result = self.tools.estimate_ticket_cost(3, ["adult"], ["Scala Museum"])

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total_cost"], 36.00)
        self.assertEqual(result["cost_breakdown"], {"Scala Museum": 36.00})
        self.assertEqual(result["unavailable_prices"], [])

if __name__ == "__main__":
    unittest.main()