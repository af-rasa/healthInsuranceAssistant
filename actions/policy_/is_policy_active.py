from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime

class IsPolicyActiveAction(Action):
    """
    This action checks if a policy is active by comparing its end date with the current date.
    It's used specifically for primary account holders (not child accounts).
    """
    
    def name(self) -> Text:
        # The name that will be used to call this action from the Rasa flow
        return "is_policy_active_action"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the policy end date from conversation tracker
        policy_end_date = tracker.get_slot("policy_end_date")
        
        # If no end date is found, return inactive status
        if not policy_end_date:
            return [SlotSet("is_policy_active", False)]
        
        try:
            # Convert the policy end date string to a datetime object
            end_date = datetime.strptime(policy_end_date, "%Y-%m-%d")
            current_date = datetime.now()
            
            # Policy is active if end date is in the future
            is_active = end_date > current_date
            return [SlotSet("is_policy_active", is_active)]
            
        except Exception as e:
            # If there's any error processing the dates, return inactive status
            return [SlotSet("is_policy_active", False)] 