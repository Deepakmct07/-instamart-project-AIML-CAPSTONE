"""Zero-shot and few-shot prompts for ticket classification. They only ever receive redacted text."""
LABELS = ["billing", "delivery", "technical", "fraud"]
ZERO_SHOT = """You are a customer-support ticket classifier for a quick-commerce app.
Classify the ticket into exactly one of: {labels}. Reply with only the label.
Ticket: {ticket}
Label:"""
FEW_SHOT = """You are a customer-support ticket classifier for a quick-commerce app.
Classify the ticket into exactly one of: {labels}. Reply with only the label.
Ticket: I was charged twice for order [ORDER_ID]. Please refund the extra payment. Label: billing
Ticket: Delivery for [ORDER_ID] is very late and the rider is not picking up. Label: delivery
Ticket: The app crashes every time I open the cart. Label: technical
Ticket: Someone hacked my account and used my wallet balance. Label: fraud
Ticket: {ticket}
Label:"""
def build_prompt(ticket, few_shot=True):
    return (FEW_SHOT if few_shot else ZERO_SHOT).format(labels=", ".join(LABELS), ticket=ticket)
