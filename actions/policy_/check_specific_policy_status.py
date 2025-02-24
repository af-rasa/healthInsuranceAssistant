from typing import Any, Text, Dict, List, Optional, Tuple
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime

class CheckSpecificPolicyStatus(Action):
    """
    This action checks the policy status for any account (primary or child).
    It determines if the policy is active by comparing the policy end date with the current date.
    """
    
    def name(self) -> Text:
        return "check_specific_policy_status"

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

    def _check_policy_status(self, policy_end_date: str) -> bool:
        """
        Helper function to check if a policy is active based on its end date.
        
        Parameters:
        - policy_end_date: The date the policy ends
        
        Returns:
        - True if policy is active, False if not
        """
        try:
            end_date = datetime.strptime(policy_end_date, "%Y-%m-%d")
            return end_date > datetime.now()
        except Exception:
            return False

    def _get_account_details(self, tracker: Tracker, selected_id: str) -> Tuple[Optional[str], List[Dict[Text, Any]]]:
        """
        Helper function to get account details and prepare events.
        
        Parameters:
        - tracker: The conversation tracker
        - selected_id: The selected account ID
        
        Returns:
        - Tuple of (policy_end_date, events)
        """
        events = []
        member_id = tracker.get_slot("member_id")
        
        # Determine if this is a primary account check
        if not member_id:
            original_member_id = self._find_original_member_id(tracker)
            is_primary = selected_id == original_member_id
        else:
            is_primary = selected_id == member_id

        # Handle primary account
        if is_primary:
            return tracker.get_slot("policy_end_date"), [SlotSet("is_child_account", False)]
        
        # Handle child account
        child_accounts = tracker.get_slot("child_accounts") or []
        child_account = next(
            (account for account in child_accounts if account['memberID'] == selected_id),
            None
        )
        
        if child_account:
            return child_account['policyEndDate'], [
                SlotSet("child_name", child_account['name']),
                SlotSet("is_child_account", True)
            ]
            
        return None, []

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """
        This is the main function that checks if a policy is active for any account.
        It looks at the policy end date and compares it with today's date.
        
        Parameters:
        - dispatcher: Like a messenger - helps the bot send messages to the user
        - tracker: Like the bot's memory - keeps track of all conversation information
        - domain: Like a rulebook - contains all the things the bot can say and do
        
        Returns:
        - A list of updates to make to the conversation memory (like marking if a policy is active)
        """
        selected_id = tracker.get_slot("selected_account_id")
        policy_end_date, events = self._get_account_details(tracker, selected_id)
        
        if not policy_end_date:
            return [SlotSet("is_policy_active", False)]
        
        is_active = self._check_policy_status(policy_end_date)
        events.append(SlotSet("is_policy_active", is_active))
        return events