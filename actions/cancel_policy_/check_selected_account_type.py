from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class CheckSelectedAccountType(Action):
    """
    This action determines whether the selected account is the primary account
    or a child account to handle different cancellation logic.
    """
    
    def name(self) -> Text:
        return "check_selected_account_type"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        selected_id = tracker.get_slot("selected_account_id")
        member_id = tracker.get_slot("member_id")
        
        # Check if the selected account is the primary account
        is_primary = selected_id == member_id
        
        if is_primary:
            child_accounts = tracker.get_slot("child_accounts") or []
            child_ids = [account['memberID'] for account in child_accounts]
            return [
                SlotSet("is_primary_account", True),
                SlotSet("affected_child_ids", child_ids)
            ]
        else:
            # Find the child account details
            child_accounts = tracker.get_slot("child_accounts") or []
            child_account = next(
                (account for account in child_accounts if account['memberID'] == selected_id),
                None
            )
            
            if child_account:
                return [
                    SlotSet("is_primary_account", False),
                    SlotSet("child_name", child_account['name'])
                ]
            
        return [SlotSet("cancellation_error", True)]