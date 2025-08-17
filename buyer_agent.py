from concordia.agents import Persona
from concordia.agents.modules import (
    AgentModule,
    MemoryModule,
    ObservationModule,
    DecisionModule
)
from concordia.document import Document
from typing import List, Optional
import re
import random


class NegotiationResponse:
    def __init__(self, action: str, message: str, offer_price: Optional[int] = None):
        self.action = action
        self.message = message
        self.offer_price = offer_price


class YourBuyerAgent:
    def __init__(self, product: str, budget: int):
        self.product = product
        self.budget = budget
        self.negotiation_rounds = 0

        self.persona = Persona(
            name="Data Analyst Buyer",
            traits=["Analytical", "Budget-conscious", "Polite", "Deadline-aware"],
            goals=[
                f"Purchase {product} within budget of {budget}",
                "Maintain good relationship with seller",
                "Get the best possible deal"
            ]
        )

        self.memory = MemoryModule()
        self.observer = ObservationModule()
        self.decision = DecisionModule()

    def _parse_price(self, message: str) -> Optional[int]:
        """Extracts price from message with currency flexibility"""
        match = re.search(r"(?:₹|rs|inr)?\s*(\d{1,3}(?:,\d{3})*)", message.lower())
        if match:
            return int(match.group(1).replace(",", ""))
        return None

    def _generate_counter_message(self, offer: int, budget: int) -> str:
        """Generate context-aware counter messages"""
        messages = [
            f"My research suggests ₹{offer} would be a fair price. What do you think?",
            f"I can do ₹{offer} based on current market rates.",
            f"Would ₹{offer} work for you? That aligns better with my budget.",
            f"Given the specs, I believe ₹{offer} is reasonable. Your thoughts?"
        ]
        return random.choice(messages)

    def negotiate(self, product: str, budget: int, seller_message: str) -> NegotiationResponse:
        self.negotiation_rounds += 1
        self.memory.store(Document(content=f"Seller (Round {self.negotiation_rounds}): {seller_message}"))

        offer_price = self._parse_price(seller_message)
        is_final = "final" in seller_message.lower()
        is_urgent = any(word in seller_message.lower() for word in ["soon", "quick", "immediate"])

        if offer_price:
            if offer_price <= budget * 0.85:
                # Great deal - accept immediately
                action = "ACCEPT"
                reply = f"Excellent! I accept ₹{offer_price}. Let's proceed with the paperwork."
                response_price = offer_price
            elif offer_price <= budget:
                if self.negotiation_rounds >= 3 or is_final:
                    # After several rounds or final offer - accept
                    action = "ACCEPT"
                    reply = f"I'll accept your ₹{offer_price} offer to conclude this deal."
                    response_price = offer_price
                else:
                    # Counter with small discount
                    counter = max(int(offer_price * 0.93), int(budget * 0.95))
                    action = "COUNTER"
                    reply = self._generate_counter_message(counter, budget)
                    response_price = counter
            else:
                if is_urgent and budget * 1.1 >= offer_price:
                    # For urgent deals slightly above budget
                    counter = int(budget * 0.98)
                    action = "COUNTER"
                    reply = f"I understand the urgency. My best offer is ₹{counter}."
                    response_price = counter
                else:
                    # Standard counter offer
                    counter = int((budget + min(offer_price, budget * 1.2)) / 2)
                    if counter >= budget * 1.1:
                        action = "REJECT"
                        reply = "This exceeds my budget constraints. Thank you for your time."
                        response_price = None
                    else:
                        action = "COUNTER"
                        reply = f"My maximum is ₹{budget}. Could we settle at ₹{counter}?"
                        response_price = counter
        else:
            if is_final:
                action = "REJECT"
                reply = "Without a clear price, I'll need to decline. Thank you."
            else:
                action = "ASK"
                reply = "Could you please specify your asking price for the product?"
            response_price = None

        self.memory.store(Document(content=f"Buyer: {reply}"))
        return NegotiationResponse(action, reply, response_price)