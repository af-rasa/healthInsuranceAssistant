from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime

class AskSelectedAccountId(Action):
    """
    This action creates and displays buttons for account selection.
    It shows buttons for both the primary account holder and any child accounts,
    allowing the user to choose which account's policy status they want to check.
    """
    
    def name(self) -> Text:
        # The name that will be used to call this action from the Rasa flow
        return "action_ask_selected_account_id"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Initialize empty list to store our button options
        buttons = []
        
        # Get primary account information from conversation tracker
        primary_id = tracker.get_slot("member_id")      # Primary account holder's ID
        primary_name = tracker.get_slot("member_name")  # Primary account holder's name
        
        # Handle case where primary_id might be missing but user is still authenticated
        if (not primary_id or primary_id == 'None') and tracker.get_slot("auth_status"):
            # Look through conversation history to find the last known member_id
            all_slots = tracker.current_slot_values()
            # Search through past events to find the most recent valid member_id
            for event in reversed(tracker.events):
                if (event.get('event') == 'slot' and 
                    event.get('name') == 'member_id' and 
                    event.get('value')):
                    primary_id = event.get('value')
                    break
        
        # Create button for primary account holder
        buttons.append({
            "title": f"{primary_name} (Primary Account Holder)",  # Button text
            "payload": f"SetSlots(selected_account_id='{primary_id}')"  # What happens when button is clicked
        })
        
        # Get list of child accounts (if any exist)
        child_accounts = tracker.get_slot("child_accounts") or []
        
        # Create a button for each child account
        for child in child_accounts:
            buttons.append({
                "title": f"{child['name']}",  # Button text shows child's name
                "payload": f"SetSlots(selected_account_id='{child['memberID']}')"  # Sets selected ID to child's ID
            })
        
        # Display the message with all our buttons
        dispatcher.utter_message(
            text="Which account's policy status would you like to check?",
            buttons=buttons
        )
        
        # No need to modify any conversation state
        return []
