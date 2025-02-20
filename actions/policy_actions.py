from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime

# class GetCurrentAuthStatus(Action):
#     def name(self) -> Text:
#         return "get_current_auth_status"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         auth_status = tracker.get_slot("auth_status")
#         return [SlotSet("auth_status", auth_status or False)]

class IsPolicyActiveAction(Action):
    def name(self) -> Text:
        return "is_policy_active_action"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        policy_end_date = tracker.get_slot("policy_end_date")
        if not policy_end_date:
            return [SlotSet("is_policy_active", False)]
        
        try:
            # Convert string dates to datetime objects
            end_date = datetime.strptime(policy_end_date, "%Y-%m-%d")
            current_date = datetime.now()
            
            # Compare dates
            is_active = end_date > current_date
            
            return [SlotSet("is_policy_active", is_active)]
            
        except Exception as e:
            print(f"Error checking policy status: {str(e)}")
            return [SlotSet("is_policy_active", False)] 