import logging
from typing import Any, Dict, List, Text
from datetime import datetime

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from ..api.connection_manager import ConnectionManager

# Set up logging for this module
logger = logging.getLogger(__name__)

class CancelPolicy(Action):
    """Action to cancel a policy by updating policy_end_date in database."""
    
    def name(self) -> Text:
        """Return the action name."""
        return "cancel_policy_action"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        """
        Cancel policy by updating policy_end_date to current date in database.
        
        For primary accounts with child accounts, also cancels all active child accounts.
        Sets was_policy_cancelled slot based on success of operation.
        """
        # Initialize connection manager for database operations
        conn_manager = ConnectionManager()
        
        # Get relevant slots
        selected_account_id = tracker.get_slot("working_selected_account_id")
        is_primary_account = tracker.get_slot("is_primary_account")
        current_date = tracker.get_slot("current_date")
        child_accounts = tracker.get_slot("child_accounts") or []
        
        # Default to failed cancellation
        was_cancelled = False
        
        try:
            logger.info(f"Attempting to cancel policy for account: {selected_account_id}")
            
            # Update data structure for the selected account
            update_data = {"policyEndDate": current_date}
            
            # For primary accounts with children, we need to cancel all active child accounts too
            if is_primary_account:
                logger.info(f"Primary account with children - will update all active child accounts")
                
                # Track whether all updates succeeded
                all_updates_succeeded = True
                
                # First update the primary account
                primary_update_success = conn_manager.update_member_data(selected_account_id, update_data)
                if not primary_update_success:
                    logger.error(f"Failed to update primary account: {selected_account_id}")
                    all_updates_succeeded = False
                
                # Then update each active child account
                for child in child_accounts:
                    child_id = child.get('memberID')
                    child_end_date = child.get('policyEndDate')
                    
                    # Only update active child accounts
                    if child_id and child_end_date and current_date < child_end_date:
                        logger.info(f"Updating active child account: {child_id}")
                        child_update_success = conn_manager.update_member_data(child_id, update_data)
                        
                        if not child_update_success:
                            logger.error(f"Failed to update child account: {child_id}")
                            all_updates_succeeded = False
                    else:
                        logger.info(f"Skipping inactive child account: {child_id}")
                
                # Set cancellation status based on all updates
                was_cancelled = all_updates_succeeded
                
            else:
                # For individual accounts (including child accounts), just update the selected account
                logger.info(f"Updating individual account: {selected_account_id}")
                update_success = conn_manager.update_member_data(selected_account_id, update_data)
                was_cancelled = update_success
        
        except Exception as e:
            # Log any exceptions during the process
            logger.error(f"Error during policy cancellation: {str(e)}")
            was_cancelled = False
        
        # Log the final result
        logger.info(f"Policy cancellation for {selected_account_id} - Success: {was_cancelled}")
        
        # Return SlotSet event with cancellation result
        return [SlotSet("was_policy_cancelled", was_cancelled)]
