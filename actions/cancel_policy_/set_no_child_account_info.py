from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging

logger = logging.getLogger(__name__)

class SetNoChildAccountInfo(Action):
    """
    This action sets the proper information for accounts without children.
    It properly copies the member_id to selected_account_id and sets is_primary_account to True.
    """
    
    def name(self) -> Text:
        return "set_no_child_account_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        member_id = tracker.get_slot("member_id")
        
        # Log the member ID for debugging
        logger.info(f"Setting up account without children. Member ID: {member_id}")
        
        return [
            SlotSet("selected_account_id", member_id),
            SlotSet("is_primary_account", True)
        ]