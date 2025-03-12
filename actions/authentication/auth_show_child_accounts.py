from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

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
        
        # Initialize empty list to store our button options
        buttons = []
        
        # Get primary account information from conversation tracker
        primary_id = tracker.get_slot("member_id")      # Primary account holder's ID
        primary_name = tracker.get_slot("member_name")  # Primary account holder's name
        primary_dob = tracker.get_slot("member_dob")
        primary_policy_end_date = tracker.get_slot("policy_end_date")
        
        # Create button for primary account holder with full slot updates
        primary_payload = (
            f"/SetSlots("
            f"selected_account_id='{primary_id}',"
            f"selected_account_name='{primary_name}',"
            f"selected_account_dob='{primary_dob}',"
            f"selected_policy_end_date='{primary_policy_end_date}')"
        )
        
        buttons.append({
            "title": f"{primary_name} (Primary Account Holder)",
            "payload": primary_payload
        })
        
        # Get list of child accounts (if any exist)
        child_accounts = tracker.get_slot("child_accounts") or []
        
        # Create a button for each child account with full slot updates
        for child in child_accounts:
            child_payload = (
                f"/SetSlots("
                f"selected_account_id='{child['memberID']}',"
                f"selected_account_name='{child['name']}',"
                f"selected_account_dob='{child['dob']}',"
                f"selected_policy_end_date='{child['policyEndDate']}')"
            )
            
            buttons.append({
                "title": f"{child['name']}",
                "payload": child_payload
            })
        
        # Use a response from the domain for the message text
        dispatcher.utter_message(response="utter_select_account", buttons=buttons)
        
        return []