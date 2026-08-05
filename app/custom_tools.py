from typing import Any

from app.knowledge import KnowledgeProvider

FILENAME = "average_travel_costs.md"

class CustomTool:
    def __init__(self, knowledge_provider: KnowledgeProvider):
        self.knowledge = knowledge_provider
    
    def estimate_budget(self, number_of_visitors: int, visitor_age_categories: list[str], attractions: list[str]) -> dict[str, Any]:
        '''
        Estimate the budget for a trip based on the number of people, the attractions they want to visit and their age category.

        Use this tool when the user asks about the estimated budget for a trip to Milan.

         Args:
            number_of_visitors: The number of people in the group.
            visitor_age_categories: A list of age categories for each visitor in the group. Possible age categroies are: "adult", "child", "student", "senior".
            attractions: A list of attractions the group wants to visit. Possible attractions are: "Milan Cathedral Rooftop and Museum ", "Milan Cathedral Rooftop Terrace Only", "Scala Museum", "Leonardo da Vinci's Last Supper", "Pinacoteca di Brera", "National Museum of Science and Technology", "Royal Palace of Milan", "Museo del Novecento".

        Returns:
            A dictionary containing the status, the estimated budget for the trip.
        '''
        if number_of_visitors < 0:
            return {
            "status": "error",
            "message": "The number of visitors cannot be negative.",
            }

        content = self.knowledge.read_document(FILENAME)
        startReading = False
        attraction_prices = {}
        total_cost = 0.0

        for line in content.splitlines():
            if line.startswith("## Attractions"):
                startReading = True

            if startReading and ("Category" in line) or ("-" in line):
                continue
            elif startReading and line.startswith("|") and line.endswith("|"):
                line = line.strip("|")
                list = line.split("|")
                attraction = list[0].strip()
                adult_price = float(list[1].strip())
                reduced_price = float(list[2].strip())
                child_price = float(list[3].strip())
                attraction_prices[attraction] = {
                    "adult": adult_price,
                    "reduced": reduced_price,
                    "child": child_price
                }

            if startReading and line.startswith("## Free Attractions"):
                startReading = False
                break

        for attraction in attractions:
            if attraction in attraction_prices:
                for age_category in visitor_age_categories:
                    if age_category == "adult":
                        total_cost += attraction_prices[attraction]["adult"]
                    elif age_category == "child":
                        total_cost += attraction_prices[attraction]["child"]
                    elif age_category in ["student", "senior"]:
                        total_cost += attraction_prices[attraction]["reduced"]

        return {
            "status": "success",
            "number_of_visitors": number_of_visitors,
            "visitor_age_categories": visitor_age_categories,
            "attractions": attractions,
            "total_cost": total_cost
        }