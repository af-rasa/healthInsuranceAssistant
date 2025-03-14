from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging

# Add logger at top of file
logger = logging.getLogger(__name__)

class ActionAskSelectedAccountId(Action):
    """
    This action displays buttons for the primary and child accounts.
    It uses a domain-defined response for the message text.
    """
    
    def name(self) -> Text:
        return "action_ask_selected_account_id"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Log current slot values
        logger.info("Current slot values in ActionAskSelectedAccountId:")
        logger.info("selected_account_id: %s", tracker.get_slot("selected_account_id"))
        logger.info("member_id: %s", tracker.get_slot("member_id"))
        logger.info("member_name: %s", tracker.get_slot("member_name"))
        
        # Create primary account button
        primary_id = tracker.get_slot("member_id")
        primary_name = tracker.get_slot("member_name")
        logger.info("Creating primary account button with ID: %s", primary_id)

        buttons = [{
            'title': f"{primary_name} (Primary Account Holder)",
            'payload': f"/SetSlots{{\"selected_account_id\":\"{primary_id}\"}}"
        }]
        
        # Add child account buttons if they exist
        child_accounts = tracker.get_slot("child_accounts") or []
        for child in child_accounts:
            buttons.append({
                'title': child['name'],
                'payload': f"/SetSlots{{\"selected_account_id\":\"{child['memberID']}\"}}"
            })
        
        # Log the final buttons being sent
        logger.info("Sending buttons: %s", buttons)
        
        # Use a response from the domain for the message text
        dispatcher.utter_message(text="Please select which account you'd like to work with at this time:", buttons=buttons)
        
        return []