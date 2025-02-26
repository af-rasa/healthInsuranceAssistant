from typing import Any, Text, Dict, List, Optional, Tuple
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)

class CancelPolicyAction(Action):
    """
    This action cancels the policy for the selected account (and child accounts if primary).
    It sets the policy_end_date to tomorrow's date.
    """
    
    def name(self) -> Text:
        return "cancel_policy_action"

    def _get_tomorrow_date(self) -> str:
        """Get tomorrow's date in YYYY-MM-DD format."""
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.strftime("%Y-%m-%d")
    
    def _check_if_already_canceled(self, policy_end_date: str) -> bool:
        """
        Check if the policy is already canceled (end date is in the past or tomorrow).
        
        Parameters:
        - policy_end_date: The current policy end date
        
        Returns:
        - True if policy is already canceled, False otherwise
        """
        try:
            # Parse the end date
            end_date = datetime.strptime(policy_end_date, "%Y-%m-%d")
            current_date = datetime.now()
            
            # Add one day to current date to compare with tomorrow
            tomorrow = current_date + timedelta(days=1)
            
            # If end date is today or earlier, it's already canceled
            return end_date <= tomorrow
        except Exception as e:
            logger.error(f"Error checking if already canceled: {str(e)}")
            return False

    def _get_policy_status(self, member_id: str) -> Tuple[bool, Optional[str]]:
        """
        Fetch the current policy end date for a member.
        
        Parameters:
        - member_id: The member ID to check
        
        Returns:
        - Tuple of (is_already_canceled, policy_end_date)
        """
        try:
            # Log the member_id for debugging
            logger.info(f"Getting policy status for member ID: '{member_id}'")
            
            response = requests.get(
                'https://api.jsonbin.io/v3/b/67aa6b3aacd3cb34a8dd1abb',
                headers={'X-Master-Key': '$2a$10$j9N2X2cOS686Gk5IRXITw.8JhMMn9o/66t2N9h2twDPIkLse3uVHW'}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch data: {response.status_code}")
                return False, None
                
            data = response.json()
            records = data['record']
            
            # Debug: Log the first few records to verify structure
            logger.info(f"Database records (first 2): {json.dumps(records[:2], indent=2)}")
            
            # Find the member's record
            for record in records:
                if record['memberID'] == member_id:
                    policy_end_date = record['policyEndDate']
                    logger.info(f"Found member {member_id} with policy end date: {policy_end_date}")
                    is_already_canceled = self._check_if_already_canceled(policy_end_date)
                    return is_already_canceled, policy_end_date
            
            logger.error(f"Member ID '{member_id}' not found in records")
            return False, None
            
        except Exception as e:
            logger.error(f"Error getting policy status for {member_id}: {str(e)}")
            return False, None

    def _cancel_policy(self, member_id: str, tomorrow_date: str) -> bool:
        """
        Update the policy end date for the specified member.
        Uses the same API endpoint as in auth_actions.py but updates the policy end date.
        """
        try:
            # Log the member ID for debugging
            logger.info(f"Attempting to cancel policy for member ID: '{member_id}'")
            
            # First, get the current data
            response = requests.get(
                'https://api.jsonbin.io/v3/b/67aa6b3aacd3cb34a8dd1abb',
                headers={'X-Master-Key': '$2a$10$j9N2X2cOS686Gk5IRXITw.8JhMMn9o/66t2N9h2twDPIkLse3uVHW'}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch data: {response.status_code}")
                return False
                
            data = response.json()
            records = data['record']
            
            # Find the member's record and update it
            updated = False
            for record in records:
                if record['memberID'] == member_id:
                    logger.info(f"Found member {member_id} to update. Old end date: {record['policyEndDate']}")
                    record['policyEndDate'] = tomorrow_date
                    updated = True
                    break
            
            if not updated:
                logger.error(f"Member ID '{member_id}' not found in records")
                return False
            
            # Update the entire JSON bin with the modified records
            update_response = requests.put(
                'https://api.jsonbin.io/v3/b/67aa6b3aacd3cb34a8dd1abb',
                json=records,
                headers={
                    'X-Master-Key': '$2a$10$j9N2X2cOS686Gk5IRXITw.8JhMMn9o/66t2N9h2twDPIkLse3uVHW',
                    'Content-Type': 'application/json'
                }
            )
            
            success = update_response.status_code == 200
            if success:
                logger.info(f"Successfully updated policy end date for {member_id} to {tomorrow_date}")
            else:
                logger.error(f"Failed to update policy: {update_response.status_code}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error cancelling policy for {member_id}: {str(e)}")
            return False

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Log all relevant slots for debugging
        logger.info(f"Running cancel_policy_action with slots:")
        logger.info(f"  selected_account_id: {tracker.get_slot('selected_account_id')}")
        logger.info(f"  is_primary_account: {tracker.get_slot('is_primary_account')}")
        logger.info(f"  member_id: {tracker.get_slot('member_id')}")
        logger.info(f"  has_child_accounts: {tracker.get_slot('has_child_accounts')}")
        
        selected_id = tracker.get_slot("selected_account_id")
        is_primary = tracker.get_slot("is_primary_account")
        tomorrow_date = self._get_tomorrow_date()
        
        # Initialize events list for return
        events = []
        
        # Set the cancellation date
        events.append(SlotSet("cancellation_date", tomorrow_date))
        
        # For primary accounts, cancel all child accounts too
        if is_primary:
            # First check if primary account is already canceled
            primary_already_canceled, primary_end_date = self._get_policy_status(selected_id)
            if primary_already_canceled:
                logger.info(f"Policy for {selected_id} is already canceled with end date {primary_end_date}")
                return [
                    SlotSet("already_canceled", True),
                    SlotSet("existing_end_date", primary_end_date)
                ]
            
            has_child_accounts = tracker.get_slot("has_child_accounts")
            if has_child_accounts:
                affected_child_ids = tracker.get_slot("affected_child_ids") or []
                logger.info(f"This is a primary account with {len(affected_child_ids)} child accounts")
                all_cancelled = True
                cancelled_ids = []
                already_cancelled_ids = []
                
                # Cancel the primary account
                primary_cancelled = self._cancel_policy(selected_id, tomorrow_date)
                if primary_cancelled:
                    cancelled_ids.append(selected_id)
                else:
                    all_cancelled = False
                    logger.error(f"Failed to cancel primary account {selected_id}")
                
                # Check and cancel all child accounts
                for child_id in affected_child_ids:
                    already_canceled, _ = self._get_policy_status(child_id)
                    if already_canceled:
                        already_cancelled_ids.append(child_id)
                        logger.info(f"Child account {child_id} is already canceled")
                        continue
                        
                    child_cancelled = self._cancel_policy(child_id, tomorrow_date)
                    if child_cancelled:
                        cancelled_ids.append(child_id)
                        logger.info(f"Successfully canceled child account {child_id}")
                    else:
                        all_cancelled = False
                        logger.error(f"Failed to cancel child account {child_id}")
                
                events.extend([
                    SlotSet("all_cancelled", all_cancelled),
                    SlotSet("cancelled_ids", cancelled_ids),
                    SlotSet("already_cancelled_ids", already_cancelled_ids),
                    SlotSet("already_canceled", False)
                ])
            else:
                # This is a primary account with no children
                logger.info(f"This is a primary account with no child accounts")
                success = self._cancel_policy(selected_id, tomorrow_date)
                events.extend([
                    SlotSet("cancellation_success", success),
                    SlotSet("all_cancelled", success),
                    SlotSet("already_canceled", False)
                ])
        else:
            # Check if just the selected child account is already canceled
            already_canceled, existing_end_date = self._get_policy_status(selected_id)
            if already_canceled:
                logger.info(f"Child account {selected_id} is already canceled with end date {existing_end_date}")
                return [
                    SlotSet("already_canceled", True),
                    SlotSet("existing_end_date", existing_end_date)
                ]
            
            # Cancel the selected child account
            success = self._cancel_policy(selected_id, tomorrow_date)
            logger.info(f"Cancellation of child account {selected_id} succeeded: {success}")
            events.extend([
                SlotSet("cancellation_success", success),
                SlotSet("already_canceled", False)
            ])
        
        return events