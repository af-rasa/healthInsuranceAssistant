from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class AskSelectedAccountId(Action):
    """
    This action creates and displays buttons for account selection.
    It shows buttons for both the primary account holder and any child accounts,
    allowing the user to choose which account's policy status they want to check.
    """
    
    def name(self) -> Text:
        return "action_ask_selected_account_id"

    def _find_original_member_id(self, tracker: Tracker) -> Optional[str]:
        """
        Helper function to find the original member ID from tracker history.
        
        Parameters:
        - tracker: The conversation tracker containing event history
        
        Returns:
        - The original member ID if found, None if not found
        """
        return next(
            (event.get('value') for event in reversed(tracker.events)
            if event.get('event') == 'slot' and 
            event.get('name') == 'member_id' and 
            event.get('value')),
            None
        )

    def _create_account_button(self, name: str, member_id: str, is_primary: bool = False) -> Dict:
        """
        Helper function to create a button for an account.
        
        Parameters:
        - name: The name to display on the button
        - member_id: The ID to set when button is clicked
        - is_primary: Whether this is the primary account button
        
        Returns:
        - A dictionary containing button configuration
        """
        title = f"{name} (Primary Account Holder)" if is_primary else name
        return {
            "title": title,
            "payload": f"SetSlots(selected_account_id='{member_id}')"
        }

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        This is the main function that runs when the bot needs to ask which account to check.
        
        Parameters:
        - dispatcher: This is like a messenger - it helps the bot send messages to the user
        - tracker: This is like the bot's memory - it remembers everything about the conversation
        - domain: This contains all the bot's knowledge - what it can say and do
        
        Returns:
        - A list of any changes we want to make to the conversation memory
        """
        buttons = []
        primary_id = tracker.get_slot("member_id")
        primary_name = tracker.get_slot("member_name")
        
        # Restore primary_id if missing but user is authenticated
        if (not primary_id or primary_id == 'None') and tracker.get_slot("auth_status"):
            primary_id = self._find_original_member_id(tracker)
        
        # Add primary account button
        buttons.append(self._create_account_button(primary_name, primary_id, is_primary=True))
        
        # Add child account buttons
        for child in (tracker.get_slot("child_accounts") or []):
            buttons.append(self._create_account_button(child['name'], child['memberID']))
        
        dispatcher.utter_message(
            text="Which account's policy status would you like to check?",
            buttons=buttons
        )
        return []