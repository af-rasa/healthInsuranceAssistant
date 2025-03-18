from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import logging
from ..api.connection_manager import ConnectionManager

# Set up logging for this module
logger = logging.getLogger(__name__)

class AuthenticateUserAction(Action):
    """
    Action to authenticate a user with their member ID.
    
    This is the first step in the authentication process:
    1. Takes the member ID provided by the user
    2. Checks if it exists in our database
    3. If found, stores all relevant member information in slots
    4. Sets up both primary account and initial selected account (same at first)
    """
    
    def name(self) -> Text:
        # The name used to call this action from rules/stories
        return "authenticate_user_action"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Retrieve member ID from conversation slot
        member_id = tracker.get_slot("member_id")
        logger.info(f"Authenticating user with member ID: {member_id}")
        
        # Initialize connection manager and get member data from the database
        conn_manager = ConnectionManager()
        member_record = conn_manager.get_member_data(member_id)
        
        if member_record:
            # Member found in database - store primary account details
            # These details are preserved throughout the entire session
            events = [
                SlotSet("member_found", True),
                SlotSet("member_name", member_record['name']),
                SlotSet("member_dob", member_record['dob']),
                SlotSet("policy_end_date", member_record['policyEndDate']),
                SlotSet("has_child_accounts", member_record['has_child_accounts']),
                # Store the primary account member ID in a dedicated slot
                # This will never change during the session, even when working with child accounts
                SlotSet("primary_account_memberID", member_record['memberID'])
            ]
            
            # Also set the primary account as the selected account by default
            # This creates the initial working state where primary = selected account
            events.extend([
                SlotSet("selected_account_id", member_record['memberID']),
                SlotSet("working_selected_account_id", member_record['memberID']),
                SlotSet("selected_account_name", member_record['name']),
                SlotSet("selected_account_dob", member_record['dob']),
                SlotSet("selected_policy_end_date", member_record['policyEndDate'])
            ])

            # If this member has child accounts (like dependents), retrieve them
            if member_record['has_child_accounts'] and member_record['child_accounts']:
                # Get additional details for each child account
                child_details = conn_manager.get_child_account_details(member_record['child_accounts'])
                events.append(SlotSet("child_accounts", child_details))
            
            return events
        
        # If we reach here, the member ID was not found in our database
        logger.warning(f"Member ID not found: {member_id}")
        return [SlotSet("member_found", False)]


class AuthSuccessful(Action):
    """
    Action to mark authentication as successful.
    
    This simple action completes the authentication process by:
    1. Setting the auth_status slot to True
    2. This status helps prevent re-authentication attempts in the same session
    """
    
    def name(self) -> Text:
        return "auth_successful"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Log successful authentication and update the status slot
        logger.info("Authentication successful")
        return [SlotSet("auth_status", True)]


class ActionAskSelectedAccountId(Action):
    """
    Action to display account selection options as buttons.
    
    This action:
    1. Retrieves primary and child account information
    2. Creates interactive buttons for each account
    3. Displays them to the user for selection
    4. Uses the permanent primary_account_memberID for reliability
    """
    
    def name(self) -> Text:
        return "action_ask_selected_account_id"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the main account and child accounts from slots
        member_name = tracker.get_slot("member_name")
        member_id = tracker.get_slot("member_id")
        member_dob = tracker.get_slot("member_dob")
        policy_end_date = tracker.get_slot("policy_end_date")
        child_accounts = tracker.get_slot("child_accounts") or []
        selected_account_id = tracker.get_slot("selected_account_id")
        
        # Get the permanent primary account reference
        # This should always be available after initial authentication
        primary_account_memberID = tracker.get_slot("primary_account_memberID")
        
        # Log account details and current selection state for debugging
        logger.info(f"Primary account ID (permanent reference): {primary_account_memberID}")
        logger.info(f"Current selected account: {selected_account_id}")
        
        # RECOVERY MECHANISM:
        # If primary account details are missing, use the permanent reference to retrieve them
        if primary_account_memberID and (not member_id or not member_name):
            logger.info(f"Using permanent reference to retrieve primary account: {primary_account_memberID}")
            
            # Make a targeted API call for just this specific member
            conn_manager = ConnectionManager()
            primary_account = conn_manager.get_member_data(primary_account_memberID)
            
            if primary_account:
                # Use the retrieved data to restore primary account information
                member_id = primary_account.get('memberID')
                member_name = primary_account.get('name')
                member_dob = primary_account.get('dob')
                policy_end_date = primary_account.get('policyEndDate')
                logger.info(f"Recovered primary account using permanent ID: {member_name} ({member_id})")
                
                # If child accounts are also missing, restore them too
                if not child_accounts and primary_account.get('has_child_accounts') and primary_account.get('child_accounts'):
                    child_accounts = conn_manager.get_child_account_details(primary_account['child_accounts'])
                    logger.info(f"Restored {len(child_accounts)} child accounts")
            else:
                logger.warning(f"Failed to recover primary account using permanent ID: {primary_account_memberID}")
        
        # Create buttons for account selection (including main account)
        buttons = []
        
        # Add the primary account as the first option
        # Make sure the member ID is properly formatted in the payload
        if member_id and member_name:
            buttons.append({
                "title": f"{member_name} (Primary)",
                "payload": f"/SetSlots(selected_account_id={member_id}, working_selected_account_id={member_id}, selected_account_name={member_name}, selected_account_dob={member_dob}, selected_policy_end_date={policy_end_date})"
            })
            logger.info(f"Added primary account button with ID: {member_id}")
        else:
            # This is a serious issue as primary account should always be available
            logger.warning("Missing primary account details - may cause issues")
        
        # Add each child account as an option with its own button
        for account in child_accounts:
            account_id = account.get('memberID')
            account_name = account.get('name')
            if account_id and account_name:
                buttons.append({
                    "title": f"{account_name}",
                    "payload": f"/SetSlots(selected_account_id={account_id}, working_selected_account_id={account_id}, selected_account_name={account['name']}, selected_account_dob={account['dob']}, selected_policy_end_date={account['policyEndDate']})"
                })
                logger.info(f"Added child account button: {account_name} with ID: {account_id}")
        
        # Display the account selection buttons to the user
        dispatcher.utter_message(
            text="Please select which account you'd like to work with:",
            buttons=buttons
        )
        
        # No slot changes needed from this action
        return []


class ActionClearSelectedAccount(Action):
    """
    Action to clear the selected account for re-selection.
    
    This action:
    1. Clears only the selected account slots
    2. Preserves the primary account information
    3. Allows the user to select a different account
    """
    
    def name(self) -> Text:
        return "action_clear_selected_account"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the primary account info before clearing
        member_id = tracker.get_slot("member_id")
        member_name = tracker.get_slot("member_name")
        primary_account_memberID = tracker.get_slot("primary_account_memberID")
        
        logger.info(f"Clearing selected account while preserving primary account: {member_name} ({member_id})")
        logger.info(f"Permanent primary account reference preserved: {primary_account_memberID}")
        
        # IMPORTANT: Only clear the selected account details
        # The primary authentication information (member_id, primary_account_memberID, etc.) stays intact
        return [
            SlotSet("selected_account_id", None),
            SlotSet("working_selected_account_id", None),
            SlotSet("selected_account_name", None),
            SlotSet("selected_account_dob", None),
            SlotSet("selected_policy_end_date", None)
        ]


class ActionTrackSelectedAccount(Action):
    """
    Action to track and confirm the selected account.
    
    This action:
    1. Gets the selected account ID from slots
    2. Makes a direct API call to ensure we have fresh account data
    3. Sets all selected account slots with accurate information
    4. Provides a confirmation to the user
    
    This is a safety mechanism to ensure account data is accurate after selection.
    """
    
    def name(self) -> Text:
        return "action_track_selected_account"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the selected account ID from slots
        selected_account_id = tracker.get_slot("selected_account_id")
        primary_account_memberID = tracker.get_slot("primary_account_memberID")
        
        logger.info(f"Processing account selection for ID: {selected_account_id}")
        logger.info(f"Permanent primary account reference: {primary_account_memberID}")
        
        # Safety check - make sure we have an account ID
        if not selected_account_id:
            logger.warning("No account ID selected")
            return []
        
        # VERIFICATION STEP:
        # Make a direct API call to get fresh account data
        # This ensures we're working with accurate information
        conn_manager = ConnectionManager()
        account_data = conn_manager.get_member_data(selected_account_id)
        
        if account_data:
            # Account data successfully retrieved from API
            logger.info(f"Account selection confirmed: {account_data['name']} ({selected_account_id})")
            
            # Set all the slots explicitly to ensure they have the correct values
            # This handles any potential discrepancies between button payload and actual data
            return [
                SlotSet("selected_account_id", selected_account_id),
                SlotSet("working_selected_account_id", selected_account_id),
                SlotSet("selected_account_name", account_data['name']),
                SlotSet("selected_account_dob", account_data['dob']),
                SlotSet("selected_policy_end_date", account_data['policyEndDate'])
            ]
        
        # FALLBACK MECHANISM:
        # If API call fails, try using the values from the tracker
        logger.warning(f"Could not get account data from API for ID: {selected_account_id}")
        selected_account_name = tracker.get_slot("selected_account_name")
        
        if selected_account_name:
            logger.info(f"Using existing slot values for account: {selected_account_name}")
            # We'll use the existing slot values, but ensure working_selected_account_id is set
            return [SlotSet("working_selected_account_id", selected_account_id)]
        
        # If all else fails, log the error
        logger.error(f"Failed to confirm account selection for ID: {selected_account_id}")
        return [] 