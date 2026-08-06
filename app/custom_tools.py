from typing import Any

from app.knowledge import KnowledgeProvider

FILENAME = "average_travel_costs.md"

class CustomTools:
    '''Custom operations that the AI agent can perform on the knowledge base.'''

    def __init__(self, knowledge_provider: KnowledgeProvider):
        self.knowledge = knowledge_provider
    
    def estimate_ticket_cost(self, number_of_visitors: int, visitor_categories: list[str], attractions: list[str]) -> dict[str, Any]:
        '''
        Estimate the ticket cost and ticket cost breakdown for a trip to Milan based on the number of people, the attractions they want to visit and the visitor category for each person in the group. Mention attractions whose ticket prices are not available in the knowledge base if applicable. Mention that full price ticket prices are used by default if no category is specified for a visitor in the group. Mention that ticket pirces are subject to change and that the user should check the official websites of the attractions for the most up-to-date information. 

        Use this tool when the user asks about the estimated ticket cost for a trip to Milan.

         Args:
            number_of_visitors: The number of people in the group.
            visitor_categories: A list of categories for each visitor in the group. Possible visitor categories are: "adult", "child", "student", "senior".
            attractions: A list of attractions the group wants to visit. Possible attractions are: "Milan Cathedral Rooftop and Museum ", "Milan Cathedral Rooftop Terrace Only", "Scala Museum", "Leonardo da Vinci's Last Supper", "Pinacoteca di Brera", "National Museum of Science and Technology", "Royal Palace of Milan", "Museo del Novecento", "Galleria Vittorio Emanuele II", "Parco Sempione", "Parco Solari", "Giardino di Guastalla", "Navigli District".

        Returns:
            A dictionary containing the status, the estimated ticket cost for the trip,  a dictionary containing the cost breakdown for each attraction with known ticket prices, a list of attractions with unavailable prices.
        '''
        if number_of_visitors < 0:
            return {
            "status": "error",
            "message": "The number of visitors cannot be negative.",
            }

        if attractions is None or len(attractions) == 0:
            return {
                "status": "error",
                "message": "No tourist attractions were specified. What do you want to visit in Milan? Here are some options: Milan Cathedral Rooftop and Museum,'Milan Cathedral Rooftop Terrace Only, Scala Museum, Leonardo da Vinci's Last Supper, Pinacoteca di Brera, National Museum of Science and Technology, Royal Palace of Milan, Museo del Novecento, Galleria Vittorio Emanuele II, Parco Sempione, Parco Solari, Giardino di Guastalla, Navigli District.",
            }

        for visitor in visitor_categories:
            if visitor not in ["adult", "child", "student", "senior"]:
                return {
                    "status": "error",
                    "message": f"Invalid visitor category: {visitor}. Possible visitor categories are: 'adult', 'child', 'student', 'senior'.",
                }

        if len(visitor_categories) > number_of_visitors:
            return {
                "status": "error",
                "message": "The number of visitor categories exceeds the number of visitors.",
            }

        if visitor_categories is None or len(visitor_categories) != number_of_visitors:
            visitor_categories.extend(["adult"] * (number_of_visitors - len(visitor_categories)))

        content = self.knowledge.read_document(FILENAME)
        startReadingPrices = False
        attraction_prices = {}
        cost_breakdown = {}
        unavailable_prices = []
        total_cost = 0.0

        for line in content.splitlines():
            if line.startswith("## Attractions"):
                startReadingPrices = True

            if startReadingPrices and ("Category" in line) or ("-" in line):
                continue
            elif startReadingPrices and line.startswith("|") and line.endswith("|"):
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

            if startReadingPrices and line.startswith("## Free Attractions"):
                startReadingPrices = False

                if line.startswith("## Free Attractions"):
                    free_attraction = line.strip("-").strip()
                    attraction_prices[free_attraction] = {
                        "adult": 0.0,
                        "reduced": 0.0,
                        "child": 0.0
                    }
                
        for attraction in attractions:
            if attraction in attraction_prices:
                cost_breakdown[attraction] = 0.0

                for age_category in visitor_categories:
                    if age_category == "adult":
                        total_cost += attraction_prices[attraction]["adult"]
                        cost_breakdown[attraction] += attraction_prices[attraction]["adult"]
                    elif age_category == "child":
                        total_cost += attraction_prices[attraction]["child"]
                        cost_breakdown[attraction] += attraction_prices[attraction]["child"]
                    elif age_category in ["student", "senior"]:
                        total_cost += attraction_prices[attraction]["reduced"]
                        cost_breakdown[attraction] += attraction_prices[attraction]["reduced"]
            else:
                unavailable_prices.append(attraction)

        return {
            "status": "success",
            "number_of_visitors": number_of_visitors,
            "visitor_categories": visitor_categories,
            "attractions": attractions,
            "total_cost": total_cost,
            "cost_breakdown": cost_breakdown,
            "unavailable_prices": unavailable_prices,
        }