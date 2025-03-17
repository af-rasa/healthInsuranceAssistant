from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
from ..api.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)

class AuthenticateUserAction(Action):
    """Action to authenticate a user with their member ID."""
    
    def name(self) -> Text:
        return "authenticate_user_action"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        member_id = tracker.get_slot("member_id")
        logger.info(f"Authenticating user with member ID: {member_id}")
        
        # Initialize connection manager and get member data
        conn_manager = ConnectionManager()
        member_record = conn_manager.get_member_data(member_id)
        
        if member_record:
            # Store primary account details (preserved throughout session)
            events = [
                SlotSet("member_found", True),
                SlotSet("member_name", member_record['name']),
                SlotSet("member_dob", member_record['dob']),
                SlotSet("policy_end_date", member_record['policyEndDate']),
                SlotSet("has_child_accounts", member_record['has_child_accounts'])
            ]
            
            # Also set the primary account as the selected account by default
            events.extend([
                SlotSet("selected_account_id", member_record['memberID']),
                SlotSet("working_selected_account_id", member_record['memberID']),
                SlotSet("selected_account_name", member_record['name']),
                SlotSet("selected_account_dob", member_record['dob']),
                SlotSet("selected_policy_end_date", member_record['policyEndDate'])
            ])

            # Handle child accounts if they exist
            if member_record['has_child_accounts'] and member_record['child_accounts']:
                child_details = conn_manager.get_child_account_details(member_record['child_accounts'])
                events.append(SlotSet("child_accounts", child_details))
            
            return events
        
        logger.warning(f"Member ID not found: {member_id}")
        return [SlotSet("member_found", False)]


class AuthSuccessful(Action):
    """Action to mark authentication as successful."""
    
    def name(self) -> Text:
        return "auth_successful"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logger.info("Authentication successful")
        return [SlotSet("auth_status", True)]


class ActionAskSelectedAccountId(Action):
    """Action to display account selection options as buttons."""
    
    def name(self) -> Text:
        return "action_ask_selected_account_id"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the main account and child accounts
        member_name = tracker.get_slot("member_name")
        member_id = tracker.get_slot("member_id")
        member_dob = tracker.get_slot("member_dob")
        policy_end_date = tracker.get_slot("policy_end_date")
        child_accounts = tracker.get_slot("child_accounts") or []
        selected_account_id = tracker.get_slot("selected_account_id")
        
        # Log account details and switching state
        logger.info(f"Primary account: {member_name} ({member_id})")
        logger.info(f"Current selected account: {selected_account_id}")
        
        # If primary account details are missing, try to recover them
        if not member_id and member_name:
            logger.warning("Missing primary account ID - attempting to recover")
            
            # Try to find primary account information from first child account's parent
            if child_accounts and len(child_accounts) > 0:
                conn_manager = ConnectionManager()
                # Try to find the primary account again
                primary_accounts = [
                    account for account in conn_manager.get_all_members()
                    if account.get('has_child_accounts', False)
                ]
                
                if primary_accounts:
                    # Use the first primary account (should be the same one)
                    primary = primary_accounts[0]
                    member_id = primary.get('memberID')
                    member_name = primary.get('name')
                    member_dob = primary.get('dob')
                    policy_end_date = primary.get('policyEndDate')
                    logger.info(f"Recovered primary account: {member_name} ({member_id})")
        
        # Create buttons for account selection (including main account)
        buttons = []
        
        # Add the primary account as the first option - ensure ID is properly formatted
        if member_id and member_name:
            buttons.append({
                "title": f"{member_name} (Primary)",
                "payload": f"/SetSlots(selected_account_id={member_id}, working_selected_account_id={member_id}, selected_account_name={member_name}, selected_account_dob={member_dob}, selected_policy_end_date={policy_end_date})"
            })
            logger.info(f"Added primary account button with ID: {member_id}")
        else:
            logger.warning("Missing primary account details - may cause issues")
        
        # Add each child account as an option
        for account in child_accounts:
            account_id = account.get('memberID')
            account_name = account.get('name')
            if account_id and account_name:
                buttons.append({
                    "title": f"{account_name}",
                    "payload": f"/SetSlots(selected_account_id={account_id}, working_selected_account_id={account_id}, selected_account_name={account['name']}, selected_account_dob={account['dob']}, selected_policy_end_date={account['policyEndDate']})"
                })
                logger.info(f"Added child account button: {account_name} with ID: {account_id}")
        
        # Send the message with buttons
        dispatcher.utter_message(
            text="Please select which account you'd like to work with:",
            buttons=buttons
        )
        
        return []


class ActionClearSelectedAccount(Action):
    """Action to clear the selected account (for re-selection)."""
    
    def name(self) -> Text:
        return "action_clear_selected_account"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logger.info("Clearing selected account for re-selection")
        
        # Get the primary account info to preserve it
        member_id = tracker.get_slot("member_id")
        member_name = tracker.get_slot("member_name")
        logger.info(f"Preserving primary account information: {member_name} ({member_id})")
        
        # Only clear the selected account details, not the primary authentication
        return [
            SlotSet("selected_account_id", None),
            SlotSet("working_selected_account_id", None),
            SlotSet("selected_account_name", None),
            SlotSet("selected_account_dob", None),
            SlotSet("selected_policy_end_date", None)
        ]


class ActionTrackSelectedAccount(Action):
    """Action to track and confirm the selected account."""
    
    def name(self) -> Text:
        return "action_track_selected_account"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the selected account ID directly
        selected_account_id = tracker.get_slot("selected_account_id")
        logger.info(f"Processing account selection for ID: {selected_account_id}")
        
        if not selected_account_id:
            logger.warning("No account ID selected")
            dispatcher.utter_message("I couldn't identify which account you want to work with.")
            return []
        
        # Make a direct API call to get the account data
        conn_manager = ConnectionManager()
        account_data = conn_manager.get_member_data(selected_account_id)
        
        if account_data:
            logger.info(f"Account selection confirmed: {account_data['name']} ({selected_account_id})")
            dispatcher.utter_message(f"You are now working with account: {account_data['name']}")
            
            # Set all the slots explicitly to ensure they have the correct values
            return [
                SlotSet("selected_account_id", selected_account_id),
                SlotSet("working_selected_account_id", selected_account_id),
                SlotSet("selected_account_name", account_data['name']),
                SlotSet("selected_account_dob", account_data['dob']),
                SlotSet("selected_policy_end_date", account_data['policyEndDate'])
            ]
        
        # If we can't get the account data from the API, try using the values from the tracker
        logger.warning(f"Could not get account data from API for ID: {selected_account_id}")
        selected_account_name = tracker.get_slot("selected_account_name")
        
        if selected_account_name:
            logger.info(f"Using existing slot values for account: {selected_account_name}")
            dispatcher.utter_message(f"You are now working with account: {selected_account_name}")
            # We'll use the existing slot values, but ensure working_selected_account_id is set
            return [SlotSet("working_selected_account_id", selected_account_id)]
        
        # If all else fails
        logger.error(f"Failed to confirm account selection for ID: {selected_account_id}")
        dispatcher.utter_message("I couldn't retrieve the details for this account.")
        return [] 