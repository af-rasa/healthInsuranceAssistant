from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime

class CheckSpecificPolicyStatus(Action):
    """
    This action checks the policy status for either a primary account holder or a child account.
    It determines if the policy is active by comparing the policy end date with the current date.
    """
    
    def name(self) -> Text:
        # The name that will be used to call this action from the Rasa flow
        return "check_specific_policy_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get important information from the conversation tracker
        selected_id = tracker.get_slot("selected_account_id")  # The ID of the account the user selected
        member_id = tracker.get_slot("member_id")             # The primary account holder's ID
        child_accounts = tracker.get_slot("child_accounts") or []  # List of child accounts, empty if none exist
        
        events = []  # List to store changes we want to make to the conversation state
        
        # CASE 1: When the primary member_id is not available (happens after first pass)
        if not member_id:
            # If the selected ID matches the known primary account ID pattern
            if selected_id == '101':  # This is the primary account ID pattern
                policy_end_date = tracker.get_slot("policy_end_date")
                events.append(SlotSet("is_child_account", False))  # Mark this as primary account check
            else:
                # Look through child accounts to find a matching ID
                child_account = next(
                    (account for account in child_accounts if account['memberID'] == selected_id),
                    None
                )
                if child_account:  # If we found a matching child account
                    policy_end_date = child_account['policyEndDate']
                    events.append(SlotSet("child_name", child_account['name']))
                    events.append(SlotSet("is_child_account", True))  # Mark this as child account check
                else:
                    # No matching account found - return inactive status
                    return [SlotSet("is_policy_active", False)]
        
        # CASE 2: When we have the primary member_id available (first pass)
        else:
            # Check if user selected the primary account
            if selected_id == member_id:
                policy_end_date = tracker.get_slot("policy_end_date")
                events.append(SlotSet("is_child_account", False))
            else:
                # Look for matching child account
                child_account = next(
                    (account for account in child_accounts if account['memberID'] == selected_id),
                    None
                )
                if child_account:
                    policy_end_date = child_account['policyEndDate']
                    events.append(SlotSet("child_name", child_account['name']))
                    events.append(SlotSet("is_child_account", True))
                else:
                    # No matching account found
                    return [SlotSet("is_policy_active", False)]

        try:
            # Convert the policy end date string to a datetime object
            end_date = datetime.strptime(policy_end_date, "%Y-%m-%d")
            current_date = datetime.now()
            
            # Policy is active if end date is in the future
            is_active = end_date > current_date
            events.append(SlotSet("is_policy_active", is_active))
            return events
            
        except Exception as e:
            # If there's any error processing the dates, return inactive status
            return [SlotSet("is_policy_active", False)]